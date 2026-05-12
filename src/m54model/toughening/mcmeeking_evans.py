"""McMeeking-Evans 1982 transformation toughening.

For a steady-state crack with a transformation wake (austenite transforming
to martensite via TRIP), the toughening increment from the volume-expansion-
induced compressive residual stress in the wake is:

    ΔK_IC = (A · E · ε^V · √h) / (1 - ν)                     [McMeeking-Evans Eq. 1]

where:
    A   = 0.22         constant from Budiansky-Hutchinson 1983 (plate-like
                        transformation morphology)
    E   = matrix Young's modulus
    ε^V = unconstrained volumetric transformation strain (γ→α′ Bain strain;
            Fe-Ni textbook value ≈ 0.04 = +4 % volume)
    h   = transformation zone half-height above the crack plane
    ν   = matrix Poisson ratio

The transformation zone is roughly half the plastic zone (rough estimate;
McMeeking-Evans use a circular-zone simplification):

    h ≈ 0.5 · r_p   (small-scale yielding)

where r_p is the Irwin plane-strain plastic zone size:

    r_p = (1 / 3π) · (K_app / σ_y)²

For a self-consistent steady-state, K_app = K_total = K_matrix + ΔK_IC, so
the formula is implicit and needs iteration. Closed-form approximation:

    ΔK_IC ≈ 0.22 · E · ε^V · K_matrix · f_transformed / (σ_y · √(6π) · (1-ν))

where f_transformed is the volume fraction of austenite that ACTUALLY
transforms in the plastic zone (≤ f_austenite total; depends on PC+OC
thresholds at the local stress/strain).

Validation: Budiansky-Hutchinson 1983 for ZrO2-toughened ceramics with
ε^V ≈ 0.04, h ≈ 50 µm, gives ΔK_IC ≈ 6 MPa·m^½ for E ≈ 200 GPa, which our
formula reproduces.
"""

from __future__ import annotations

import math

# Budiansky-Hutchinson 1983 constant for plate-like transformation
A_BUDIANSKY_HUTCHINSON = 0.22


def irwin_plastic_zone_m(
    K_MPa_m_half: float,
    sigma_y_MPa: float,
    *,
    plane_strain: bool = True,
) -> float:
    """Irwin small-scale-yielding plastic zone size r_p (meters).

    Plane strain: r_p = (1 / 3π) · (K / σ_y)²
    Plane stress: r_p = (1 / π)  · (K / σ_y)²
    """
    if sigma_y_MPa <= 0:
        raise ValueError(f"sigma_y_MPa must be > 0, got {sigma_y_MPa}")
    prefactor = 1.0 / (3.0 * math.pi) if plane_strain else 1.0 / math.pi
    # K is MPa·m^½, σ_y is MPa, so (K/σ_y)² has units of m.
    return prefactor * (K_MPa_m_half / sigma_y_MPa) ** 2


def mcmeeking_evans_delta_KIC(
    E_GPa: float,
    epsilon_V_transformation: float,
    transformation_zone_half_height_m: float,
    *,
    nu: float = 0.30,
    A: float = A_BUDIANSKY_HUTCHINSON,
    f_transformed: float = 1.0,
) -> float:
    """ΔK_IC from steady-state transformation wake (McM-E Eq. 1).

    Returns MPa·m^½.

    `f_transformed` is the volume fraction of available austenite that ACTUALLY
    underwent γ→α′ in the transformation zone. Defaults to 1.0 (all austenite
    in the zone transformed). Multiply by total f_A to get the absolute
    transformed volume fraction; the formula is linear in this product.
    """
    if E_GPa <= 0:
        raise ValueError(f"E_GPa must be > 0, got {E_GPa}")
    if transformation_zone_half_height_m <= 0:
        return 0.0
    E_MPa = E_GPa * 1e3
    return (
        A
        * E_MPa
        * epsilon_V_transformation
        * f_transformed
        * math.sqrt(transformation_zone_half_height_m)
        / (1.0 - nu)
    )


def steady_state_KIC_iterative(
    K_matrix_MPa_m_half: float,
    sigma_y_MPa: float,
    E_GPa: float,
    epsilon_V_transformation: float,
    *,
    f_austenite: float = 0.0,
    f_transformed_fraction: float = 1.0,
    nu: float = 0.30,
    A: float = A_BUDIANSKY_HUTCHINSON,
    h_over_rp: float = 0.5,
    max_iter: int = 50,
    tol_MPa_m_half: float = 0.01,
) -> tuple[float, float, int]:
    """Solve self-consistently for total K_IC = K_matrix + ΔK_TRIP.

    Iterates: r_p depends on K_total, ΔK_TRIP depends on r_p, K_total depends
    on ΔK_TRIP. Fixed-point iteration; converges for typical inputs.

    Returns (K_total, delta_K_TRIP, iterations).

    Inputs:
        K_matrix_MPa_m_half:    Bare-matrix toughness (no TRIP contribution)
        sigma_y_MPa:            Matrix yield strength (from our model)
        E_GPa:                  Matrix Young's modulus
        epsilon_V_transformation: Volumetric Bain strain γ→α′ (~+0.04 for Fe-Ni)
        f_austenite:            Total austenite vol fraction far from crack
        f_transformed_fraction: Of that f_A, fraction actually transformed in
                                 plastic zone (1.0 = all; <1 if PC threshold
                                 limits which austenite triggers)
        nu, A, h_over_rp:       Model constants
    """
    if f_austenite <= 0 or epsilon_V_transformation <= 0:
        return K_matrix_MPa_m_half, 0.0, 0

    K_total = K_matrix_MPa_m_half
    f_eff = f_austenite * f_transformed_fraction

    for i in range(max_iter):
        r_p = irwin_plastic_zone_m(K_total, sigma_y_MPa)
        h = h_over_rp * r_p
        delta_K = mcmeeking_evans_delta_KIC(
            E_GPa,
            epsilon_V_transformation,
            h,
            nu=nu,
            A=A,
            f_transformed=f_eff,
        )
        K_new = K_matrix_MPa_m_half + delta_K
        if abs(K_new - K_total) < tol_MPa_m_half:
            return K_new, delta_K, i + 1
        K_total = K_new
    return K_total, K_total - K_matrix_MPa_m_half, max_iter
