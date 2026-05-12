"""Tests for the XRD peak-analysis + Bain-strain module (Phase 3.6b)."""

import math

import pytest

from m54model.xrd import (
    BAIN_EPSILON_V_FE_NI_TEXTBOOK,
    BAIN_EPSILON_V_M54_XRD,
    LAMBDA_CU_KA1_A,
    PeakWindow,
    analyze_xrd_for_cr,
    bain_volumetric_strain,
    bcc_alpha_a0_from_peak,
    fcc_a0_from_bcc_bain_correspondence,
    fcc_gamma_a0_from_peak,
    integrate_peak,
    lattice_parameter_from_2theta,
    modified_miller_V_gamma,
    nelson_riley_extrapolation,
)


def test_lattice_parameter_pure_alpha_iron() -> None:
    """α-Fe (110) at Cu Kα: 2θ ≈ 44.67° → a = 2.866 Å."""
    a = bcc_alpha_a0_from_peak(44.67, (1, 1, 0))
    assert a == pytest.approx(2.866, abs=0.005)


def test_lattice_parameter_pure_gamma_iron() -> None:
    """Fe-Ni γ at RT: a ≈ 3.589 Å → 2θ ≈ 50.78° (where the M54 200-γ peak is)."""
    a = fcc_gamma_a0_from_peak(50.78, (2, 0, 0))
    assert a == pytest.approx(3.589, abs=0.005)


def test_bcc_rejects_forbidden_hkl() -> None:
    """BCC reflection condition: h+k+l even. (1,0,0) is forbidden."""
    with pytest.raises(ValueError):
        bcc_alpha_a0_from_peak(40.0, (1, 0, 0))


def test_fcc_rejects_mixed_parity_hkl() -> None:
    """FCC needs all-even or all-odd. (1,2,0) is forbidden."""
    with pytest.raises(ValueError):
        fcc_gamma_a0_from_peak(40.0, (1, 2, 0))


def test_modified_miller_v_gamma_basic() -> None:
    """V_γ = 1.4·I_γ / (I_α + 1.4·I_γ). For equal intensities, V_γ = 1.4/2.4 = 0.583."""
    v = modified_miller_V_gamma(1.0, 1.0)
    assert v == pytest.approx(1.4 / 2.4)


def test_modified_miller_v_gamma_zero_gamma() -> None:
    assert modified_miller_V_gamma(100.0, 0.0) == 0.0


def test_bain_strain_self_consistency() -> None:
    """ε^V = 0 when 2·a_α³ = a_γ³ exactly."""
    a_alpha = 2.870
    a_gamma = a_alpha * (2.0 ** (1.0 / 3.0))  # = a_α · ∛2
    assert bain_volumetric_strain(a_alpha, a_gamma) == pytest.approx(0.0, abs=1e-9)


def test_bain_inverse_round_trip() -> None:
    """fcc_a0_from_bcc_bain_correspondence is the inverse of
    bain_volumetric_strain."""
    a_alpha = 2.870
    eps_V = 0.025
    a_gamma = fcc_a0_from_bcc_bain_correspondence(a_alpha, eps_V)
    assert bain_volumetric_strain(a_alpha, a_gamma) == pytest.approx(eps_V, abs=1e-9)


def test_bain_textbook_value_for_fe_ni() -> None:
    """a_γ ≈ 3.589, a_α ≈ 2.872 gives ε^V ≈ +0.022 — close to the M54
    measured value, NOT the often-quoted +0.04."""
    eps_V = bain_volumetric_strain(2.872, 3.589)
    assert eps_V == pytest.approx(0.022, abs=0.005)
    assert eps_V == pytest.approx(BAIN_EPSILON_V_M54_XRD, abs=0.005)


def test_textbook_constant_present_for_back_compat() -> None:
    """The Phase 3.5 default 0.04 stays exposed for cross-reference."""
    assert BAIN_EPSILON_V_FE_NI_TEXTBOOK == 0.04


def test_nelson_riley_intercept_recovers_known_a0() -> None:
    """Synthetic noise-free data: NR should recover a₀ exactly."""
    a0_true = 2.870
    # Pretend three peaks at known 2θ all give the same a (no systematic error).
    a_values = [a0_true, a0_true, a0_true]
    twos = [80.0, 100.0, 130.0]
    a0, slope = nelson_riley_extrapolation(a_values, twos)
    assert a0 == pytest.approx(a0_true, rel=1e-6)
    assert slope == pytest.approx(0.0, abs=1e-9)


def test_integrate_peak_above_baseline() -> None:
    """Synthetic Gaussian-ish peak with flat baseline: integration finds it."""
    twos = [44.0 + i * 0.01 for i in range(141)]  # 44.0 to 45.4
    # Rectangular peak from 44.6 to 44.8 with height 100 above baseline 10.
    ints = [10.0 + (90.0 if 44.6 <= t <= 44.8 else 0.0) for t in twos]
    I, t_peak = integrate_peak(twos, ints, PeakWindow(44.7, 0.5, "test"))
    assert I > 5  # something integrated (depends on baseline shape)
    assert 44.5 < t_peak < 44.9


def test_analyze_xrd_for_cr_0pct_baseline() -> None:
    """Phase 3.6b regression: 0 % CR XRD gives a_α′ ≈ 2.870 Å, V_γ ≈ 4.8 %,
    ε^V ≈ +0.022."""
    r = analyze_xrd_for_cr(0)
    assert r.a_alpha_A_NR_extrapolated == pytest.approx(2.870, abs=0.003)
    assert r.a_gamma_A_best == pytest.approx(3.589, abs=0.005)
    assert r.V_gamma_pct == pytest.approx(4.81, abs=0.5)
    assert r.bain_eps_V == pytest.approx(BAIN_EPSILON_V_M54_XRD, abs=0.005)


def test_analyze_xrd_for_cr_60pct_no_gamma() -> None:
    """At 60 % CR the bulk XRD shows essentially no γ — V_γ < 0.1 %."""
    r = analyze_xrd_for_cr(60)
    assert r.V_gamma_pct < 0.1
    assert r.a_gamma_A_best is None
    assert r.bain_eps_V is None
    # α′ a₀ contracts ~0.007 Å from 0 % to 60 % CR.
    assert r.a_alpha_A_NR_extrapolated < 2.870


def test_analyze_xrd_round_trip_lambda_cu() -> None:
    """Sanity: 110-α at 44.7° in Cu λ should reverse-Bragg to d ≈ 2.027 Å."""
    a = lattice_parameter_from_2theta(44.7, (1, 1, 0))
    expected_d = LAMBDA_CU_KA1_A / (2.0 * math.sin(math.radians(44.7 / 2.0)))
    assert a == pytest.approx(expected_d * math.sqrt(2), rel=1e-9)
