"""Tests for the Williamson-Hall ρ_total extraction (Phase 3.6g)."""

import math

import pytest

from m54model.xrd import (
    LAMBDA_CU_KA1_A,
    PeakWindow,
    analyze_williamson_hall_for_cr,
    dislocation_density_from_microstrain,
    estimate_fwhm_deg,
    wh_vs_gnd_for_all_cr,
    williamson_hall_regression,
)
from m54model.xrd.williamson_hall import (
    BURGERS_VECTOR_ALPHA_FE_M,
    GAUSSIAN_FWHM_TO_BETA,
    K_ALPHA_BCC_SCREW,
    SCHERRER_K,
)

# ---- Unit-level tests on synthetic data ------------------------------------------------


def test_estimate_fwhm_recovers_known_gaussian_fwhm() -> None:
    """A pure Gaussian with σ = 0.10° has FWHM = 2·σ·√(2 ln 2) ≈ 0.2355°.
    The half-max-width estimator should recover this to <2 % on a fine grid."""
    sigma = 0.10  # deg
    x0 = 44.7
    twos = [44.0 + i * 0.005 for i in range(281)]
    ints = [100.0 * math.exp(-((t - x0) ** 2) / (2 * sigma * sigma)) for t in twos]
    fwhm, peak_t, max_h = estimate_fwhm_deg(twos, ints, PeakWindow(x0, 0.6, "test"))
    expected = 2.0 * sigma * math.sqrt(2.0 * math.log(2.0))
    assert fwhm == pytest.approx(expected, rel=0.02)
    assert peak_t == pytest.approx(x0, abs=0.01)
    assert max_h == pytest.approx(100.0, rel=0.05)


def test_estimate_fwhm_returns_zero_when_no_peak() -> None:
    """Flat (no peak) → FWHM 0, max height 0."""
    twos = [44.0 + i * 0.05 for i in range(50)]
    ints = [100.0 for _ in twos]  # flat
    fwhm, _, max_h = estimate_fwhm_deg(twos, ints, PeakWindow(45.0, 0.5, "flat"))
    assert fwhm == 0.0
    assert max_h == 0.0


def test_williamson_hall_recovers_known_strain_and_size() -> None:
    """Build noise-free WH inputs from a known (D, ε) and verify regression
    recovers them exactly. Inverts:

        β · cos θ = K λ / D + 4 ε sin θ

    where β is in radians (Gaussian integral breadth = FWHM_rad · √(π/(4 ln 2))).
    """
    D_nm_true = 50.0
    eps_true = 3.0e-3
    D_A = D_nm_true * 10.0
    peaks = [44.7, 65.0, 82.3, 99.0, 116.4, 137.2]
    fwhm_inputs = []
    for t in peaks:
        th = math.radians(t / 2.0)
        # Generate β (radians, integral breadth) from the WH equation, then
        # convert to FWHM in degrees so the regression can re-derive β.
        size_term = SCHERRER_K * LAMBDA_CU_KA1_A / (D_A * math.cos(th))
        strain_term = 4.0 * eps_true * math.tan(th)
        beta_int = size_term + strain_term
        fwhm_rad = beta_int / GAUSSIAN_FWHM_TO_BETA
        fwhm_inputs.append(math.degrees(fwhm_rad))

    eps_rec, D_rec = williamson_hall_regression(peaks, fwhm_inputs)
    assert eps_rec == pytest.approx(eps_true, rel=1e-6)
    assert D_rec == pytest.approx(D_nm_true, rel=1e-6)


def test_williamson_hall_pure_size_no_strain() -> None:
    """If broadening is purely size (ε = 0), regression should give ε ≈ 0
    and recover D."""
    D_nm_true = 30.0
    D_A = D_nm_true * 10.0
    peaks = [44.7, 65.0, 82.3, 99.0]
    fwhm_inputs = []
    for t in peaks:
        th = math.radians(t / 2.0)
        beta_int = SCHERRER_K * LAMBDA_CU_KA1_A / (D_A * math.cos(th))
        fwhm_rad = beta_int / GAUSSIAN_FWHM_TO_BETA
        fwhm_inputs.append(math.degrees(fwhm_rad))
    eps, D_nm = williamson_hall_regression(peaks, fwhm_inputs)
    assert eps == pytest.approx(0.0, abs=1e-9)
    assert D_nm == pytest.approx(D_nm_true, rel=1e-6)


def test_williamson_hall_requires_at_least_two_peaks() -> None:
    with pytest.raises(ValueError):
        williamson_hall_regression([44.7], [0.4])


def test_williamson_hall_mismatched_lengths() -> None:
    with pytest.raises(ValueError):
        williamson_hall_regression([44.7, 65.0], [0.4])


def test_dislocation_density_formula_for_alpha_fe() -> None:
    """ρ ≈ 2.34 × 10²⁰ · ε² (m⁻²) for K_α=14.4, b=0.248 nm.
    ε = 3e-3 → ρ ≈ 2.1 × 10¹⁵."""
    eps = 3.0e-3
    rho = dislocation_density_from_microstrain(eps)
    expected_prefactor = K_ALPHA_BCC_SCREW / (BURGERS_VECTOR_ALPHA_FE_M ** 2)
    assert rho == pytest.approx(expected_prefactor * eps * eps, rel=1e-9)
    assert 1e15 < rho < 5e15


def test_dislocation_density_rejects_negative_strain() -> None:
    with pytest.raises(ValueError):
        dislocation_density_from_microstrain(-1e-3)


# ---- Real-data smoke tests (require the user's XRD workbook) ---------------------------


def test_real_data_zero_cr_smoke() -> None:
    """0 % CR XRD: WH should give a finite, physically-sensible ε and ρ_WH.

    Acceptance: ε in [1e-4, 5e-3] and ρ_WH in [1e13, 1e16] (very wide
    physical band — classical WH on cold-rolled BCC can be off by ~3× from
    modified WH, see module docstring caveat). The trend tests below are
    far more important than these absolute bounds."""
    r = analyze_williamson_hall_for_cr(0)
    assert r.n_peaks_used >= 4  # all 6 alpha peaks should be visible at 0 % CR
    assert 1e-4 < r.epsilon_microstrain < 5e-3
    assert 1e13 < r.rho_WH_per_m2 < 1e16


def test_real_data_strain_increases_from_baseline() -> None:
    """Cold-rolling adds defect content. Microstrain at 20 % CR should
    exceed the 0 % baseline (the strongest single-direction trend in the
    data — 60 % shows partial recovery in the WH fit, see FINDINGS.md
    Phase 3.6g)."""
    r0 = analyze_williamson_hall_for_cr(0)
    r20 = analyze_williamson_hall_for_cr(20)
    assert r20.epsilon_microstrain > r0.epsilon_microstrain


def test_real_data_rho_wh_increases_with_first_cw_step() -> None:
    """ρ_WH (∝ ε²) should jump from 0 → 20 % CR — that's the strongest signal
    in the cold-work series and is a sanity check the WH machinery wires up."""
    r0 = analyze_williamson_hall_for_cr(0)
    r20 = analyze_williamson_hall_for_cr(20)
    assert r20.rho_WH_per_m2 > r0.rho_WH_per_m2


def test_real_data_all_cr_runs_without_error() -> None:
    """Smoke: no CR condition raises and all return positive ρ_WH and finite ε."""
    for cw in (0, 20, 40, 60):
        r = analyze_williamson_hall_for_cr(cw)
        assert math.isfinite(r.epsilon_microstrain)
        assert r.epsilon_microstrain >= 0.0
        assert math.isfinite(r.rho_WH_per_m2)
        assert r.rho_WH_per_m2 >= 0.0


def test_wh_vs_gnd_table_structure() -> None:
    """The high-level comparison helper produces one row per CR with the
    expected keys, and k = ρ_WH / ρ_GND is finite and non-negative."""
    table = wh_vs_gnd_for_all_cr()
    assert len(table) == 4
    for row in table:
        assert {"cw_pct", "rho_GND_per_m2", "rho_WH_per_m2",
                "multiplier_k", "epsilon_microstrain", "n_peaks_used"} <= row.keys()
        assert row["rho_GND_per_m2"] > 0
        assert math.isfinite(row["multiplier_k"])
        assert row["multiplier_k"] >= 0.0


def test_wh_inst_broadening_huge_kills_all_peaks() -> None:
    """Sanity: if β_inst exceeds every observed FWHM, all sample broadening
    goes to zero and the regression has no usable peaks → ε = 0, ρ_WH = 0."""
    r = analyze_williamson_hall_for_cr(20, beta_inst_deg=10.0)
    assert r.epsilon_microstrain == 0.0
    assert r.rho_WH_per_m2 == 0.0
    assert r.n_peaks_used == 0


def test_wh_K_alpha_prefactor_scales_rho_linearly() -> None:
    """ρ_WH ∝ K_α at fixed ε. Doubling K_α should double ρ_WH (same ε)."""
    r1 = analyze_williamson_hall_for_cr(20, K_alpha=14.4)
    r2 = analyze_williamson_hall_for_cr(20, K_alpha=28.8)
    assert r2.rho_WH_per_m2 == pytest.approx(2.0 * r1.rho_WH_per_m2, rel=1e-9)
    assert r1.epsilon_microstrain == pytest.approx(r2.epsilon_microstrain, rel=1e-9)
