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

import math
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
from m54model.toughening.williams_field import (
    hrr_radial_rescale,
    irwin_zone_boundary_m,
    williams_k_field,
)
from m54model.xrd.bain import BAIN_EPSILON_V_M54_XRD

# Default Fe-Ni transformation strains (Patel-Cohen 1953 §3.2).
DEFAULT_GAMMA_0 = 0.20
DEFAULT_EPS_0_DEVIATORIC = 0.04

# Volumetric Bain strain γ → α′. As of Phase 3.6b, defaults to the
# M54-specific value measured from the user's 0 % CR XRD (+0.022) instead
# of the textbook Fe-Ni +0.04 used in Phase 3.5. To recover the
# Phase-3.5 result, pass `epsilon_V=0.04` explicitly to crack_tip_KIC.
DEFAULT_EPS_V = BAIN_EPSILON_V_M54_XRD

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


# Default elastic-plastic strain proxy — small but non-trivial work hardening.
# Inside the plastic zone, ε_p(r, θ) ≈ ε_y · ((σ_eq − σ_y)/σ_y) raised to a
# power-law growth toward the tip. This is a practical placeholder; HRR-J-
# controlled scaling (σ ∝ r^(−1/(n+1)), ε ∝ r^(−n/(n+1))) would be a Phase
# 3.6+ refinement. n_workhardening = 5 corresponds to a moderately
# strain-hardening tempered martensite.
DEFAULT_N_WORKHARDENING = 5.0


def _local_plastic_strain(
    sigma_eq_MPa: float,
    sigma_y_MPa: float,
    *,
    n_workhardening: float = DEFAULT_N_WORKHARDENING,
    eps_y: float = 0.008,
) -> float:
    """Power-law plastic strain estimate at a point in the elastic-plastic zone.

    For σ_eq ≤ σ_y returns 0. Above yield, returns ε_y · ((σ_eq/σ_y)^n − 1)
    capped at 1.0 to avoid singular behavior near the crack tip.
    """
    if sigma_eq_MPa <= sigma_y_MPa:
        return 0.0
    return min(1.0, eps_y * ((sigma_eq_MPa / sigma_y_MPa) ** n_workhardening - 1.0))


@dataclass(frozen=True)
class SpatialCrackTipResult:
    """Spatially-integrated crack-tip K_IC prediction (Phase 3.6a)."""

    K_matrix_MPa_m_half: float
    delta_K_TRIP_MPa_m_half: float
    K_total_MPa_m_half: float
    plastic_zone_area_m2: float
    f_transformed_avg: float
    """Area-weighted average of f_PC ⊕ f_OC over the plastic zone."""
    f_PC_avg: float
    f_OC_avg: float
    iterations_to_converge: int
    sigma_y_matrix_MPa: float
    n_radial: int
    n_theta: int

    def __repr__(self) -> str:
        return (
            f"SpatialCrackTipResult(K_matrix={self.K_matrix_MPa_m_half:.1f}, "
            f"ΔK_TRIP={self.delta_K_TRIP_MPa_m_half:.2f}, "
            f"K_total={self.K_total_MPa_m_half:.1f} MPa·m^½, "
            f"<f_PC>={self.f_PC_avg:.3f}, <f_OC>={self.f_OC_avg:.3f}, "
            f"<f_transformed>={self.f_transformed_avg:.3f}, "
            f"area={self.plastic_zone_area_m2 * 1e12:.2f} mm²·1e6)"
        )


def _spatial_average_transformed_fraction(
    K_total_MPa_m_half: float,
    sigma_y_MPa: float,
    *,
    nu: float,
    gamma_0: float,
    eps_0: float,
    M_s_offset_K: float,
    olson_cohen_params: OlsonCohenParams | None,
    n_workhardening: float,
    n_radial: int,
    n_theta: int,
    trigger_combiner: Literal["max", "sum_capped"],
    use_hrr_radial_rescale: bool = False,
) -> tuple[float, float, float, float]:
    """Walk the polar grid (r, θ) ∈ Ω_p (where σ_eq ≥ σ_y), compute
    pointwise f_PC and f_OC, return area-weighted averages.

    Returns (<f_transformed>, <f_PC>, <f_OC>, area).
    """
    import numpy as np

    # θ grid spans the kidney lobe (avoid θ = ±π crack flanks where r_p → 0).
    thetas = np.linspace(-math.pi * 0.95, math.pi * 0.95, n_theta)
    r_p_max = max(
        irwin_zone_boundary_m(t, K_total_MPa_m_half, sigma_y_MPa, nu=nu) for t in thetas
    )
    if r_p_max <= 0:
        return 0.0, 0.0, 0.0, 0.0

    # Radial grid is per-θ; we use a normalized 0→1 grid, scaled to r_p(θ).
    s_norm = np.linspace(0.02, 1.0, n_radial)  # avoid r→0 singularity

    sum_area = 0.0
    sum_area_f_T = 0.0
    sum_area_f_PC = 0.0
    sum_area_f_OC = 0.0

    for t in thetas:
        r_p_local = irwin_zone_boundary_m(t, K_total_MPa_m_half, sigma_y_MPa, nu=nu)
        if r_p_local <= 0:
            continue
        rs = s_norm * r_p_local
        for r in rs:
            stress = williams_k_field(r, t, K_total_MPa_m_half, nu=nu)
            sigma_eq = stress.mises_equivalent_MPa
            if sigma_eq < sigma_y_MPa:
                continue  # outside Ω_p
            sigma_principal = stress.principal_max_in_plane_MPa
            # HRR-style rescaling INSIDE Ω_p: replace K-field's r^(-1/2)
            # with HRR's r^(-1/(n+1)) (Hutchinson 1968 singular plastic
            # field). Bounded by the same K-field at the boundary.
            if use_hrr_radial_rescale:
                sigma_eq = hrr_radial_rescale(
                    sigma_eq, sigma_y_MPa, r, r_p_local, n_workhardening
                )
                sigma_principal = hrr_radial_rescale(
                    sigma_principal, sigma_y_MPa, r, r_p_local, n_workhardening
                )
            U_max = patel_cohen_max_work(
                max(0.0, sigma_principal), gamma_0, eps_0, mode="tension"
            )
            dT_from_stress_K = 0.145 * U_max
            if M_s_offset_K <= 0:
                f_PC = 1.0 if U_max > 0 else 0.0
            else:
                f_PC = max(0.0, min(1.0, dT_from_stress_K / M_s_offset_K))
            eps_p = _local_plastic_strain(
                sigma_eq, sigma_y_MPa, n_workhardening=n_workhardening
            )
            ocp = olson_cohen_params or OlsonCohenParams(
                alpha=3.55, beta=0.30, n=4.5, T_celsius=22
            )
            f_OC = olson_cohen_volume_fraction(eps_p, ocp) if eps_p > 0 else 0.0
            if trigger_combiner == "max":
                f_T = max(f_PC, f_OC)
            else:
                f_T = min(1.0, f_PC + f_OC)
            # Polar area element ≈ r · dr · dθ (uniform-step approximation).
            dA = r * (r_p_local / n_radial) * (math.pi * 1.9 / n_theta)
            sum_area += dA
            sum_area_f_T += dA * f_T
            sum_area_f_PC += dA * f_PC
            sum_area_f_OC += dA * f_OC

    if sum_area <= 0:
        return 0.0, 0.0, 0.0, 0.0
    return (
        sum_area_f_T / sum_area,
        sum_area_f_PC / sum_area,
        sum_area_f_OC / sum_area,
        sum_area,
    )


def crack_tip_KIC_spatial(
    state: MicrostructuralState,
    K_matrix_MPa_m_half: float,
    *,
    E_GPa: float = DEFAULT_E_GPA,
    nu: float = DEFAULT_NU,
    epsilon_V: float = DEFAULT_EPS_V,
    gamma_0: float = DEFAULT_GAMMA_0,
    eps_0_deviatoric: float = DEFAULT_EPS_0_DEVIATORIC,
    M_s_offset_K: float = 0.0,
    olson_cohen_params: OlsonCohenParams | None = None,
    n_workhardening: float = DEFAULT_N_WORKHARDENING,
    A: float = A_BUDIANSKY_HUTCHINSON,
    h_over_rp: float = 0.5,
    n_radial: int = 24,
    n_theta: int = 36,
    constants: StrengtheningConstants | None = None,
    trigger_combiner: Literal["max", "sum_capped"] = "max",
    max_iter: int = 25,
    tol_MPa_m_half: float = 0.05,
    use_hrr_radial_rescale: bool = False,
) -> SpatialCrackTipResult:
    """Phase 3.6a — spatial integration of Patel-Cohen + Olson-Cohen over the
    crack-tip plastic zone, replacing the bulk-averaged trigger of
    `crack_tip_KIC`.

    Iterative loop:
      1. Use current K_total to define Ω_p via Williams K-field + Mises yield.
      2. At each (r, θ) in Ω_p, evaluate σ_eq, σ_principal, ε_p(σ_eq, σ_y).
      3. Map σ_principal → f_PC (Patel-Cohen) and ε_p → f_OC (Olson-Cohen).
      4. Area-weighted average <f_transformed> = max(<f_PC>, <f_OC>).
      5. Plug into McMeeking-Evans → ΔK_TRIP, update K_total, repeat.

    Compared to `crack_tip_KIC` (bulk-averaged), the spatial version
    distinguishes the kidney-lobe geometry of Ω_p (only ~70 % of a circular
    disk is above yield in plane strain), the higher-σ region near the tip
    where PC saturates faster, and the lower-σ outer region where OC
    dominates. For M54 reverted-γ levels (1-3 %), expect ΔK_TRIP within ~30 %
    of the bulk answer — this confirms the bulk version was order-of-
    magnitude correct without depending on its heuristic.
    """
    sigma_y_MPa = assemble_yield_strength(state, constants=constants).sigma_y_MPa

    if state.f_austenite <= 0 or epsilon_V <= 0:
        return SpatialCrackTipResult(
            K_matrix_MPa_m_half=K_matrix_MPa_m_half,
            delta_K_TRIP_MPa_m_half=0.0,
            K_total_MPa_m_half=K_matrix_MPa_m_half,
            plastic_zone_area_m2=0.0,
            f_transformed_avg=0.0,
            f_PC_avg=0.0,
            f_OC_avg=0.0,
            iterations_to_converge=0,
            sigma_y_matrix_MPa=sigma_y_MPa,
            n_radial=n_radial,
            n_theta=n_theta,
        )

    K_total = K_matrix_MPa_m_half
    f_T = f_PC = f_OC = 0.0
    area = 0.0

    for i in range(max_iter):
        f_T, f_PC, f_OC, area = _spatial_average_transformed_fraction(
            K_total,
            sigma_y_MPa,
            nu=nu,
            gamma_0=gamma_0,
            eps_0=eps_0_deviatoric,
            M_s_offset_K=M_s_offset_K,
            olson_cohen_params=olson_cohen_params,
            n_workhardening=n_workhardening,
            n_radial=n_radial,
            n_theta=n_theta,
            trigger_combiner=trigger_combiner,
            use_hrr_radial_rescale=use_hrr_radial_rescale,
        )
        # McMeeking-Evans wake height from r_p = (1/3π)(K/σ_y)² (Irwin avg).
        r_p_irwin = (K_total / sigma_y_MPa) ** 2 / (3.0 * math.pi)
        h = h_over_rp * r_p_irwin
        f_eff = state.f_austenite * f_T
        from m54model.toughening.mcmeeking_evans import mcmeeking_evans_delta_KIC

        delta_K = mcmeeking_evans_delta_KIC(
            E_GPa, epsilon_V, h, nu=nu, A=A, f_transformed=f_eff
        )
        K_new = K_matrix_MPa_m_half + delta_K
        if abs(K_new - K_total) < tol_MPa_m_half:
            return SpatialCrackTipResult(
                K_matrix_MPa_m_half=K_matrix_MPa_m_half,
                delta_K_TRIP_MPa_m_half=delta_K,
                K_total_MPa_m_half=K_new,
                plastic_zone_area_m2=area,
                f_transformed_avg=f_T,
                f_PC_avg=f_PC,
                f_OC_avg=f_OC,
                iterations_to_converge=i + 1,
                sigma_y_matrix_MPa=sigma_y_MPa,
                n_radial=n_radial,
                n_theta=n_theta,
            )
        K_total = K_new

    return SpatialCrackTipResult(
        K_matrix_MPa_m_half=K_matrix_MPa_m_half,
        delta_K_TRIP_MPa_m_half=K_total - K_matrix_MPa_m_half,
        K_total_MPa_m_half=K_total,
        plastic_zone_area_m2=area,
        f_transformed_avg=f_T,
        f_PC_avg=f_PC,
        f_OC_avg=f_OC,
        iterations_to_converge=max_iter,
        sigma_y_matrix_MPa=sigma_y_MPa,
        n_radial=n_radial,
        n_theta=n_theta,
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
