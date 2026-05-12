"""High-level crack-tip K_IC integration for M54 with TRIP toughening.

Workflow:
  1. Take a tempered MicrostructuralState (which has measured/inferred f_A
     and matrix YS via assemble_yield_strength).
  2. Estimate the fraction of f_A that actually transforms in the plastic
     zone, given Patel-Cohen + Olson-Cohen thresholds at the local stress
     and strain.
  3. Solve self-consistently for K_total = K_matrix + ΔK_TRIP via
     McMeeking-Evans steady-state formula.

Phase 3.5 v1 simplifications:
  - Bulk-averaged transformation in the plastic zone (no spatial integration).
  - Patel-Cohen used to estimate the FRACTION of austenite triggered by stress
    (vs the fraction triggered by strain via Olson-Cohen) at the crack-tip
    average σ ≈ σ_y.
  - K_matrix is a calibration parameter — fit it so K_total matches the
    Mondière 110 MPa·m^½ anchor; report what value of K_matrix that requires.

Phase 3.6+ refinements (deferred):
  - Spatial integration over the plastic zone using HRR or K-field.
  - Local M_s shift via Patel-Cohen at each material point.
  - Olson-Cohen with M54-specific (α, β) once we calibrate from cw/cr data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from m54model.constants import StrengtheningConstants
from m54model.states import MicrostructuralState
from m54model.strengthening import assemble_yield_strength
from m54model.toughening.mcmeeking_evans import (
    A_BUDIANSKY_HUTCHINSON,
    irwin_plastic_zone_m,
    steady_state_KIC_iterative,
)
from m54model.toughening.olson_cohen import OlsonCohenParams, olson_cohen_volume_fraction
from m54model.toughening.patel_cohen import patel_cohen_max_work

# Default Fe-Ni transformation strains (Patel-Cohen 1953 §3.2). M54-specific
# values would come from XRD-measured γ vs α′ lattice parameters; flagged as
# a Phase 3.6 refinement in docs/FINDINGS.md.
DEFAULT_GAMMA_0 = 0.20
DEFAULT_EPS_0_DEVIATORIC = 0.04
DEFAULT_EPS_V = 0.04  # volumetric Bain strain (3 × deviatoric for isotropic)

# Steel handbook elastic constants
DEFAULT_E_GPA = 210.0
DEFAULT_NU = 0.30


@dataclass(frozen=True)
class CrackTipResult:
    """Bundled K_IC prediction with decomposition."""

    K_matrix_MPa_m_half: float
    """Bare-matrix toughness (input parameter; no TRIP contribution)."""

    delta_K_TRIP_MPa_m_half: float
    """Increment from transformation-toughening shielding."""

    K_total_MPa_m_half: float
    """K_matrix + delta_K_TRIP."""

    plastic_zone_size_m: float
    """Irwin plane-strain r_p at K_total."""

    transformation_zone_height_m: float
    """h ≈ 0.5 r_p (McMeeking-Evans plate-zone simplification)."""

    f_austenite_total: float
    """Total austenite vol fraction far from crack tip."""

    f_transformed_fraction: float
    """Fraction of f_austenite_total that actually transforms in the zone."""

    iterations_to_converge: int

    sigma_y_matrix_MPa: float
    """Matrix yield strength used (from assemble_yield_strength)."""

    def __repr__(self) -> str:
        return (
            f"CrackTipResult(K_matrix={self.K_matrix_MPa_m_half:.1f}, "
            f"ΔK_TRIP={self.delta_K_TRIP_MPa_m_half:.1f}, "
            f"K_total={self.K_total_MPa_m_half:.1f} MPa·m^½, "
            f"r_p={self.plastic_zone_size_m * 1e6:.1f} µm, "
            f"f_A={self.f_austenite_total:.3f}, "
            f"f_transformed={self.f_transformed_fraction:.2f})"
        )


def _patel_cohen_triggered_fraction(
    sigma_eq_MPa: float,
    *,
    gamma_0: float = DEFAULT_GAMMA_0,
    eps_0: float = DEFAULT_EPS_0_DEVIATORIC,
    M_s_offset_K: float = 0.0,
    chemical_driving_force_MPa_per_K: float = 5.0,
) -> float:
    """Estimate the fraction of austenite that triggers via STRESS-ASSISTED
    Patel-Cohen at a given local equivalent stress.

    Heuristic: if mechanical work U_max exceeds the chemical driving-force
    deficit (M_s,chem - T_ambient), all available austenite triggers
    spontaneously (return 1.0). If U_max is well below the threshold,
    nothing triggers spontaneously (return 0.0). Linear ramp between.

    `M_s_offset_K` is the gap (T_ambient - M_s,chem) the stress must close,
    in Kelvin. Default 0 means austenite is right at its M_s — any tensile
    stress triggers transformation. For metastable γ films at lath
    boundaries with a positive offset (γ stable to deeper undercooling),
    a larger offset means stress has to do more work to trigger.

    Returns a fraction in [0, 1].
    """
    U_max_MPa = patel_cohen_max_work(sigma_eq_MPa, gamma_0, eps_0, mode="tension")
    # Effective driving force shift from PC (rough conversion: 1 MPa·dimensionless
    # ≈ 0.2 K depending on -dF/dT slope). For Fe-Ni-C, +1 °C/ksi ≈ +0.145 K/MPa.
    # Use a generic conversion; user can override M_s_offset_K to calibrate.
    dT_from_stress_K = 0.145 * U_max_MPa
    if M_s_offset_K <= 0:
        return 1.0 if U_max_MPa > 0 else 0.0
    if dT_from_stress_K >= M_s_offset_K:
        return 1.0
    return max(0.0, dT_from_stress_K / M_s_offset_K)


def _olson_cohen_triggered_fraction(
    eps_plastic: float,
    olson_cohen_params: OlsonCohenParams | None = None,
) -> float:
    """Strain-induced fraction via Olson-Cohen at a given local plastic strain.

    Defaults to literature-analog Cho 2015 H600 / Angel 304 SS at room temp
    when no M54-specific params are provided (since Phase 3.1 found M54
    cw/cr data is non-monotonic and can't be directly fit; calibration from
    that data is Phase 3.6 work).
    """
    if olson_cohen_params is None:
        # Literature analog: Angel 304 SS at room temperature
        olson_cohen_params = OlsonCohenParams(alpha=3.55, beta=0.30, n=4.5, T_celsius=22)
    return olson_cohen_volume_fraction(eps_plastic, olson_cohen_params)


def crack_tip_KIC(
    state: MicrostructuralState,
    K_matrix_MPa_m_half: float,
    *,
    E_GPa: float = DEFAULT_E_GPA,
    nu: float = DEFAULT_NU,
    epsilon_V: float = DEFAULT_EPS_V,
    gamma_0: float = DEFAULT_GAMMA_0,
    eps_0_deviatoric: float = DEFAULT_EPS_0_DEVIATORIC,
    M_s_offset_K: float = 0.0,
    crack_tip_eps_plastic: float = 0.10,
    olson_cohen_params: OlsonCohenParams | None = None,
    A: float = A_BUDIANSKY_HUTCHINSON,
    h_over_rp: float = 0.5,
    constants: StrengtheningConstants | None = None,
    trigger_combiner: Literal["max", "sum_capped"] = "max",
) -> CrackTipResult:
    """Predict crack-tip K_IC for an M54 microstructural state.

    Steps:
      1. Compute σ_y from the strengthening model.
      2. Estimate Patel-Cohen-triggered fraction of austenite at σ_eq ≈ σ_y.
      3. Estimate Olson-Cohen-triggered fraction at crack_tip_eps_plastic.
      4. Combine the two (default: max — whichever pathway is more
         saturated dominates; alt: sum_capped at 1.0 — both add up).
      5. Iteratively solve K_total = K_matrix + ΔK_TRIP via McMeeking-Evans.

    K_matrix is the user's choice. To use this for Mondière K_IC = 110
    validation, run `K_matrix_for_target` instead, which solves for the
    K_matrix that lands K_total at a chosen target.
    """
    sigma_y_MPa = assemble_yield_strength(state, constants=constants).sigma_y_MPa

    f_PC = _patel_cohen_triggered_fraction(
        sigma_y_MPa,
        gamma_0=gamma_0,
        eps_0=eps_0_deviatoric,
        M_s_offset_K=M_s_offset_K,
    )
    f_OC = _olson_cohen_triggered_fraction(crack_tip_eps_plastic, olson_cohen_params)

    if trigger_combiner == "max":
        f_transformed = max(f_PC, f_OC)
    elif trigger_combiner == "sum_capped":
        f_transformed = min(1.0, f_PC + f_OC)
    else:
        raise ValueError(f"unknown trigger_combiner {trigger_combiner!r}")

    K_total, delta_K, iters = steady_state_KIC_iterative(
        K_matrix_MPa_m_half=K_matrix_MPa_m_half,
        sigma_y_MPa=sigma_y_MPa,
        E_GPa=E_GPa,
        epsilon_V_transformation=epsilon_V,
        f_austenite=state.f_austenite,
        f_transformed_fraction=f_transformed,
        nu=nu,
        A=A,
        h_over_rp=h_over_rp,
    )

    r_p = irwin_plastic_zone_m(K_total, sigma_y_MPa)
    h = h_over_rp * r_p

    return CrackTipResult(
        K_matrix_MPa_m_half=K_matrix_MPa_m_half,
        delta_K_TRIP_MPa_m_half=delta_K,
        K_total_MPa_m_half=K_total,
        plastic_zone_size_m=r_p,
        transformation_zone_height_m=h,
        f_austenite_total=state.f_austenite,
        f_transformed_fraction=f_transformed,
        iterations_to_converge=iters,
        sigma_y_matrix_MPa=sigma_y_MPa,
    )


def K_matrix_for_target(
    state: MicrostructuralState,
    target_K_total_MPa_m_half: float,
    *,
    bracket: tuple[float, float] = (10.0, 200.0),
    tol_MPa_m_half: float = 0.5,
    max_iter: int = 60,
    **crack_tip_kwargs,
) -> CrackTipResult:
    """Bisection: find the K_matrix that produces a chosen K_total.

    Useful for "what bare-matrix K_IC does this microstructure need to land
    at Mondière 110 MPa·m^½?" — the answer says how much of the measured
    K_IC came from TRIP shielding vs the matrix.
    """
    lo, hi = bracket
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        r = crack_tip_KIC(state, K_matrix_MPa_m_half=mid, **crack_tip_kwargs)
        if abs(r.K_total_MPa_m_half - target_K_total_MPa_m_half) < tol_MPa_m_half:
            return r
        if r.K_total_MPa_m_half > target_K_total_MPa_m_half:
            hi = mid
        else:
            lo = mid
    return r
