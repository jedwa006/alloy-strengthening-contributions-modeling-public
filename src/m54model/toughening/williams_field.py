"""Williams 1957 K-field — small-scale-yielding stress components ahead of a
mode I crack tip in an isotropic linear-elastic continuum.

Polar coordinates (r, θ) centered on the crack tip; θ measured from the
crack-plane ahead of the tip (θ = 0 is straight ahead, θ = ±π is the
crack flanks).

  σ_xx = (K / √(2πr)) · cos(θ/2) · [1 − sin(θ/2) sin(3θ/2)]
  σ_yy = (K / √(2πr)) · cos(θ/2) · [1 + sin(θ/2) sin(3θ/2)]
  σ_xy = (K / √(2πr)) · cos(θ/2) · sin(θ/2) cos(3θ/2)
  σ_zz = ν (σ_xx + σ_yy)        [plane strain]

Validity: r ≪ crack length and r outside the process zone (the K-field
is the leading singular term of the elastic field; the elastic-plastic
field inside the plastic zone differs but is bounded by it). For Phase
3.6a we use the K-field as a usable proxy throughout Ω_p; HRR-based
refinement is a Phase 3.6+ option.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class StressTensor2D:
    """In-plane Cauchy stress at a single (r, θ) point. MPa."""

    sigma_xx: float
    sigma_yy: float
    sigma_xy: float
    sigma_zz: float  # plane-strain out-of-plane component (= ν(σ_xx + σ_yy))

    @property
    def hydrostatic_MPa(self) -> float:
        """σ_m = (σ_xx + σ_yy + σ_zz)/3."""
        return (self.sigma_xx + self.sigma_yy + self.sigma_zz) / 3.0

    @property
    def mises_equivalent_MPa(self) -> float:
        """σ_eq = √(3/2 · s_ij s_ij), s_ij = σ_ij − σ_m δ_ij. In-plane principal
        + out-of-plane σ_zz are sufficient since σ_xz = σ_yz = 0 in plane strain.
        """
        sxx, syy, szz, sxy = self.sigma_xx, self.sigma_yy, self.sigma_zz, self.sigma_xy
        # Direct from σ_ij in this 2D-plane-strain situation:
        # σ_eq² = ½[(σ_xx − σ_yy)² + (σ_yy − σ_zz)² + (σ_zz − σ_xx)²] + 3 σ_xy²
        return math.sqrt(
            0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2) + 3.0 * sxy**2
        )

    @property
    def principal_max_in_plane_MPa(self) -> float:
        """Largest in-plane principal stress (mode I → most-tensile direction).
        Use this as the driver for Patel-Cohen 'effective uniaxial' loading.
        """
        avg = 0.5 * (self.sigma_xx + self.sigma_yy)
        diff = 0.5 * (self.sigma_xx - self.sigma_yy)
        radius = math.sqrt(diff**2 + self.sigma_xy**2)
        return avg + radius


def williams_k_field(
    r_m: float,
    theta_rad: float,
    K_MPa_m_half: float,
    *,
    nu: float = 0.30,
    plane_strain: bool = True,
) -> StressTensor2D:
    """Mode-I Williams asymptotic stress field at (r, θ).

    `r_m` in metres, `K` in MPa·m^½ → returned σ in MPa (units consistent).
    For plane stress, σ_zz = 0; for plane strain, σ_zz = ν (σ_xx + σ_yy).
    """
    if r_m <= 0:
        raise ValueError(f"r_m must be > 0, got {r_m}")
    prefactor = K_MPa_m_half / math.sqrt(2.0 * math.pi * r_m)
    half = 0.5 * theta_rad
    three_half = 1.5 * theta_rad
    cos_h = math.cos(half)
    sin_h = math.sin(half)
    cos_3h = math.cos(three_half)
    sin_3h = math.sin(three_half)

    sigma_xx = prefactor * cos_h * (1.0 - sin_h * sin_3h)
    sigma_yy = prefactor * cos_h * (1.0 + sin_h * sin_3h)
    sigma_xy = prefactor * cos_h * sin_h * cos_3h
    sigma_zz = nu * (sigma_xx + sigma_yy) if plane_strain else 0.0
    return StressTensor2D(sigma_xx, sigma_yy, sigma_xy, sigma_zz)


def irwin_zone_boundary_m(
    theta_rad: float,
    K_MPa_m_half: float,
    sigma_y_MPa: float,
    *,
    nu: float = 0.30,
    plane_strain: bool = True,
) -> float:
    """Angle-resolved plastic-zone boundary r_p(θ) where σ_eq = σ_y.

    Found by solving σ_eq(r, θ; K) = σ_y for r, given σ_eq ∝ 1/√r:

      σ_eq(r, θ) = (K / √(2πr)) · g(θ; ν)
      r_p(θ)     = (1 / 2π) · (K / σ_y)² · g(θ; ν)²

    where g(θ; ν) is the angular factor in σ_eq from the Williams field.
    The classical kidney-shaped Mises lobe falls out automatically.
    """
    if sigma_y_MPa <= 0:
        raise ValueError(f"sigma_y_MPa must be > 0, got {sigma_y_MPa}")
    # Evaluate σ_eq at unit r via the field, extract the angular factor.
    s = williams_k_field(1.0, theta_rad, K_MPa_m_half, nu=nu, plane_strain=plane_strain)
    # σ_eq(r=1, θ; K) = K · g(θ; ν) / √(2π) · r^(-1/2) so g²(θ) follows.
    sigma_eq_at_unit_r = s.mises_equivalent_MPa  # has K and √(2π) baked in
    # σ_eq(r, θ) = sigma_eq_at_unit_r / √r ⇒ at σ_y: r = (sigma_eq_at_unit_r / σ_y)²
    return (sigma_eq_at_unit_r / sigma_y_MPa) ** 2


def angular_g_factor(
    theta_rad: float,
    *,
    nu: float = 0.30,
    plane_strain: bool = True,
) -> float:
    """Pure angular dependence of σ_eq in the K-field, normalized so that
    σ_eq(r, θ) = (K / √(2πr)) · g(θ; ν).

    Useful for plotting the kidney-shaped lobe directly.
    """
    s = williams_k_field(1.0, theta_rad, 1.0, nu=nu, plane_strain=plane_strain)
    return s.mises_equivalent_MPa * math.sqrt(2.0 * math.pi)


def hrr_radial_rescale(
    sigma_eq_K_field_MPa: float,
    sigma_y_MPa: float,
    r_m: float,
    r_p_local_m: float,
    n_workhardening: float,
) -> float:
    """Phase 3.6c — replace the Williams-K elastic radial scaling
    (σ ∝ r^(−½)) with the HRR singular-plastic-field scaling
    (σ ∝ r^(−1/(n+1))) INSIDE the plastic zone, while preserving the
    K-field's angular shape.

    Outside Ω<sub>p</sub> (where K-field is correct): pass-through.

    Inside Ω<sub>p</sub>: rescale so that σ<sub>eq</sub> = σ<sub>y</sub>
    at r = r<sub>p</sub>(θ), and scales as (r<sub>p</sub>/r)^(1/(n+1))
    going inward (HRR singular-plastic field; Hutchinson 1968).

    For n → ∞ (perfectly plastic): σ_eq → σ_y everywhere inside Ω_p
    (perfect plateau). For n → 1 (no hardening): scaling → r^(−½),
    which recovers the K-field. Typical M54 tempered martensite:
    n ≈ 5 - 10.
    """
    if r_m <= 0 or r_p_local_m <= 0 or n_workhardening <= 0:
        return sigma_eq_K_field_MPa
    if sigma_eq_K_field_MPa <= sigma_y_MPa:
        return sigma_eq_K_field_MPa  # outside Ω_p, K-field is fine
    if r_m >= r_p_local_m:
        return sigma_eq_K_field_MPa
    # Inside Ω_p: σ_eq(r) = σ_y · (r_p / r)^(1/(n+1))
    return sigma_y_MPa * (r_p_local_m / r_m) ** (1.0 / (n_workhardening + 1.0))
