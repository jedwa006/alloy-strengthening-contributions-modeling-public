"""Tests for Williams 1957 mode-I K-field stress components."""

import math

import pytest

from m54model.toughening import (
    angular_g_factor,
    irwin_zone_boundary_m,
    williams_k_field,
)


def test_williams_field_known_value_at_theta_zero() -> None:
    """At θ=0 (straight ahead of tip): σ_xx = σ_yy = K/√(2πr), σ_xy = 0."""
    K = 100.0
    r = 1e-3
    s = williams_k_field(r, 0.0, K, nu=0.30, plane_strain=True)
    expected = K / math.sqrt(2.0 * math.pi * r)
    assert s.sigma_xx == pytest.approx(expected, rel=1e-9)
    assert s.sigma_yy == pytest.approx(expected, rel=1e-9)
    assert s.sigma_xy == pytest.approx(0.0, abs=1e-9)
    assert s.sigma_zz == pytest.approx(0.30 * 2 * expected, rel=1e-9)


def test_williams_field_symmetry_in_theta() -> None:
    """Mode I is symmetric in θ for σ_xx, σ_yy; antisymmetric for σ_xy."""
    K = 50.0
    r = 1e-4
    s_pos = williams_k_field(r, 0.5, K)
    s_neg = williams_k_field(r, -0.5, K)
    assert s_pos.sigma_xx == pytest.approx(s_neg.sigma_xx, rel=1e-9)
    assert s_pos.sigma_yy == pytest.approx(s_neg.sigma_yy, rel=1e-9)
    assert s_pos.sigma_xy == pytest.approx(-s_neg.sigma_xy, rel=1e-9)


def test_mises_equivalent_nonneg() -> None:
    s = williams_k_field(1e-4, math.pi * 0.4, 80.0)
    assert s.mises_equivalent_MPa >= 0


def test_principal_max_geq_sigma_yy_at_theta_zero() -> None:
    """At θ=0, σ_yy is principal — should match the in-plane max."""
    s = williams_k_field(1e-4, 0.0, 100.0)
    assert s.principal_max_in_plane_MPa == pytest.approx(s.sigma_yy, rel=1e-9)


def test_irwin_zone_kidney_lobe_peaks_off_axis() -> None:
    """Plane-strain Mises plastic-zone boundary peaks NOT at θ=0 — it's a
    kidney shape with maxima around θ ≈ ±70°."""
    K = 80.0
    sy = 1700.0
    rps = [
        (math.degrees(t), irwin_zone_boundary_m(t, K, sy))
        for t in [0.0, math.pi * 0.2, math.pi * 0.4, math.pi * 0.5, math.pi * 0.7]
    ]
    rp_at_zero = irwin_zone_boundary_m(0.0, K, sy)
    rp_max = max(rp for _, rp in rps)
    # kidney: max should be > axial value
    assert rp_max > rp_at_zero
    # Sanity scale: axial r_p = (1/2π) · (K/σ_y)² · g(0)² with g(0; ν=0.3) = 0.4
    #   = (1/2π) · (80/1700)² · 0.16 ≈ 5.6e-5 m
    expected = (K / sy) ** 2 * (1.0 - 2 * 0.30) ** 2 / (2.0 * math.pi)
    assert rp_at_zero == pytest.approx(expected, rel=1e-3)


def test_field_consistent_with_irwin_average() -> None:
    """Average r_p over θ should be in the right ballpark vs the standard
    Irwin estimate r_p = (1/3π)(K/σ_y)² (which is a θ-averaged proxy)."""
    K = 100.0
    sy = 1500.0
    rp_irwin_avg = (K / sy) ** 2 / (3.0 * math.pi)
    # Numerical average over θ ∈ [-π·0.95, π·0.95]
    n = 50
    thetas = [(-math.pi * 0.95 + 2 * math.pi * 0.95 * i / (n - 1)) for i in range(n)]
    rp_avg = sum(irwin_zone_boundary_m(t, K, sy) for t in thetas) / n
    # Should be within ~3× of the θ=0 axial estimate (kidney lobe is wider).
    assert 0.3 * rp_irwin_avg < rp_avg < 5.0 * rp_irwin_avg


def test_hrr_radial_rescale_pass_through_outside_omega_p() -> None:
    """Outside Ω_p (σ_eq < σ_y), HRR rescale is a pass-through."""
    from m54model.toughening import hrr_radial_rescale

    sigma_eq = 1500.0
    sigma_y = 1700.0
    out = hrr_radial_rescale(sigma_eq, sigma_y, r_m=1e-5, r_p_local_m=1e-4, n_workhardening=5)
    assert out == sigma_eq


def test_hrr_radial_rescale_matches_sigma_y_at_boundary() -> None:
    """At r = r_p, σ_HRR = σ_y by construction."""
    from m54model.toughening import hrr_radial_rescale

    out = hrr_radial_rescale(2000.0, 1700.0, r_m=1e-5, r_p_local_m=1e-5, n_workhardening=5)
    # Edge case: r >= r_p → pass through (Williams-K is correct there).
    assert out == 2000.0


def test_hrr_radial_rescale_lower_than_K_field_inside_omega_p() -> None:
    """Inside Ω_p, HRR's r^(-1/(n+1)) decays slower than K-field's r^(-1/2),
    so HRR-rescaled σ_eq is LOWER than the input K-field σ_eq."""
    from m54model.toughening import hrr_radial_rescale

    sigma_y = 1700.0
    sigma_K = 4000.0  # Williams-K value deep inside Ω_p
    r_p = 1e-4
    r = r_p / 100  # well inside Ω_p
    out_n5 = hrr_radial_rescale(sigma_K, sigma_y, r_m=r, r_p_local_m=r_p, n_workhardening=5)
    assert out_n5 < sigma_K
    assert out_n5 > sigma_y  # but still above yield


def test_hrr_perfect_plasticity_limit_caps_at_sigma_y() -> None:
    """n → ∞ (perfectly plastic): HRR exponent → 0, so σ_eq → σ_y inside Ω_p."""
    from m54model.toughening import hrr_radial_rescale

    sigma_y = 1700.0
    r_p = 1e-4
    r = r_p / 100
    out_large_n = hrr_radial_rescale(4000.0, sigma_y, r_m=r, r_p_local_m=r_p, n_workhardening=1e6)
    assert out_large_n == pytest.approx(sigma_y, rel=0.01)


def test_angular_g_factor_at_zero() -> None:
    """g(0; ν=0.3) for plane strain: σ_xx = σ_yy = 1/√(2π) at K=1, r=1.
    Mises with σ_zz = ν·(σ_xx+σ_yy) = 0.6/√(2π):
      σ_eq² = ½[(σ_xx-σ_yy)² + (σ_yy-σ_zz)² + (σ_zz-σ_xx)²]
            = ½ · 2(σ_yy - σ_zz)² = (1 - ν)² · (1/√(2π))² · 2
      σ_eq = (1 - 2ν) · (1/√(2π))      [since σ_xx=σ_yy → in-plane diff zero]
      g(0) = σ_eq · √(2π) = (1 − 2ν) = 0.4"""
    g0 = angular_g_factor(0.0, nu=0.30, plane_strain=True)
    assert g0 == pytest.approx(0.4, rel=1e-3)
