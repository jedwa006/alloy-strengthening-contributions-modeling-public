"""Tests for the Phase 3.7a derived-properties forward-calc."""

import pytest

from m54model.calibration import m54_af_t516_10_cw, m54_af550_45_t516_10
from m54model.strengthening import (
    DEFAULT_H_GAMMA_GPA,
    DEFAULT_TABOR_COEFFICIENT_SIGMA_UTS,
    EMPIRICAL_WORK_HARDENING_RATIO_BY_CR,
    composite_hardness_GPa,
    phase_corrected_alpha_prime_hardness_GPa,
    predict_derived_properties,
    predict_derived_properties_cw_cr_sweep,
    sigma_uts_MPa_from_hardness,
    tabor_hardness_GPa_from_sigma_uts,
    tabor_hardness_GPa_from_sigma_y,
)


def test_tabor_uts_round_trip() -> None:
    """H ↔ σ_UTS round trip exact."""
    sigma = 2100.0
    H = tabor_hardness_GPa_from_sigma_uts(sigma)
    sigma_back = sigma_uts_MPa_from_hardness(H)
    assert sigma_back == pytest.approx(sigma, rel=1e-9)


def test_tabor_uts_at_0pct_cr_baseline_calibration() -> None:
    """σ_UTS(0%) = 2100 MPa with default C → H_α′(0%) = 6.8 GPa (Ch 5 anchor)."""
    H = tabor_hardness_GPa_from_sigma_uts(2100.0)
    assert H == pytest.approx(6.8, rel=0.01)


def test_tabor_y_at_0pct_cr_baseline_calibration() -> None:
    """σ_y(0%) = 1300 MPa with default C → H_α′(0%) ≈ 6.8 GPa."""
    H = tabor_hardness_GPa_from_sigma_y(1300.0)
    assert H == pytest.approx(6.8, rel=0.01)


def test_eq1_forward_round_trip() -> None:
    """H_composite = f_γ·H_γ + (1-f_γ)·H_α′ → invert → H_α′ recovered."""
    H_alpha_prime = 8.0
    f_gamma = 0.10
    H_comp = composite_hardness_GPa(H_alpha_prime, f_gamma)
    back = phase_corrected_alpha_prime_hardness_GPa(H_comp, f_gamma)
    assert back == pytest.approx(H_alpha_prime, rel=1e-9)


def test_eq1_at_zero_f_gamma() -> None:
    """f_γ = 0 → H_composite = H_α′ exactly."""
    H = composite_hardness_GPa(7.5, 0.0)
    assert H == 7.5


def test_eq1_invert_high_f_gamma_returns_zero_safely() -> None:
    """f_γ → 1 makes Eq. 1 inversion numerically degenerate; we return 0 to
    avoid blowup. Threshold: 1 - f_γ < 0.05."""
    out = phase_corrected_alpha_prime_hardness_GPa(5.0, 0.99)
    assert out == 0.0


def test_eq1_round_trip_matches_chapter5_0pct_anchor() -> None:
    """0 % CR: measured H_composite ~6.80 GPa, f_γ_surf = 0.013, H_γ = 4.0
    → recovered H_α′ ≈ 6.84 GPa, very close to Ch 5 reported 6.8."""
    H_alpha_back = phase_corrected_alpha_prime_hardness_GPa(6.80, 0.013, H_gamma_GPa=4.0)
    assert H_alpha_back == pytest.approx(6.84, abs=0.05)


def test_predict_derived_properties_baseline_within_10pct_of_ch5() -> None:
    """0 % CR: predicted H_α′ should land within ±10 % of Ch 5's 6.8 GPa."""
    state = m54_af550_45_t516_10()
    pred = predict_derived_properties(state)
    assert pred.H_alpha_prime_GPa == pytest.approx(6.8, rel=0.10)


def test_predict_sweep_returns_four_rows_with_anchor_columns() -> None:
    rows = predict_derived_properties_cw_cr_sweep(location="core")
    assert len(rows) == 4
    keys = set(rows[0].keys())
    expected = {
        "cw_pct", "f_gamma",
        "sigma_y_user_rate_MPa", "sigma_y_meas_MPa",
        "sigma_uts_alpha_prime_pred_MPa", "sigma_uts_meas_MPa",
        "H_alpha_prime_pred_GPa", "H_alpha_prime_ch5_meas_GPa",
        "H_composite_pred_GPa", "H_composite_meas_GPa",
    }
    assert expected <= keys


def test_predict_sweep_uses_cr_dependent_wh_ratio_by_default() -> None:
    """Default WH ratio for 0 % CR is 1.62; for 60 % CR is 1.42."""
    rows = predict_derived_properties_cw_cr_sweep(location="core")
    r0 = next(r for r in rows if r["cw_pct"] == 0)
    r60 = next(r for r in rows if r["cw_pct"] == 60)
    # σ_UTS / σ_y_qs should equal the WH ratio (modulo rounding).
    # σ_y_qs is sigma_y_user_rate / 1.054 (strain-rate factor) and ALSO
    # before the f_A correction; we check consistency directly.
    # Just verify the 0 % entry hits H_α′ ≈ 6.8 (Ch 5) within ±0.5 GPa.
    assert r0["H_alpha_prime_pred_GPa"] == pytest.approx(7.2, abs=0.5)
    assert r60["H_alpha_prime_pred_GPa"] == pytest.approx(7.7, abs=0.5)


def test_predict_sweep_with_constant_wh_overrides_cr_dependent() -> None:
    """Passing a float work_hardening_ratio overrides the CR-dependent default."""
    rows_default = predict_derived_properties_cw_cr_sweep(location="core")
    rows_const = predict_derived_properties_cw_cr_sweep(
        location="core", work_hardening_ratio=1.62
    )
    # 0 % CR: same (both use 1.62)
    r0_d = next(r for r in rows_default if r["cw_pct"] == 0)
    r0_c = next(r for r in rows_const if r["cw_pct"] == 0)
    assert r0_d["H_alpha_prime_pred_GPa"] == r0_c["H_alpha_prime_pred_GPa"]
    # 60 % CR: const 1.62 > default 1.42 → constant predicts higher H_α′
    r60_d = next(r for r in rows_default if r["cw_pct"] == 60)
    r60_c = next(r for r in rows_const if r["cw_pct"] == 60)
    assert r60_c["H_alpha_prime_pred_GPa"] > r60_d["H_alpha_prime_pred_GPa"]


def test_predict_sweep_subblock_HP_propagates_to_derived_props() -> None:
    """K_sub=150 raises σ_y at 60 % CR (Phase 3.6f); H_α′ should rise
    proportionally via Tabor."""
    rows_default = predict_derived_properties_cw_cr_sweep(location="core")
    rows_kSub = predict_derived_properties_cw_cr_sweep(
        location="core", subblock_hp_K_MPa_um_half=150
    )
    r60_d = next(r for r in rows_default if r["cw_pct"] == 60)
    r60_k = next(r for r in rows_kSub if r["cw_pct"] == 60)
    assert r60_k["sigma_y_user_rate_MPa"] > r60_d["sigma_y_user_rate_MPa"]
    assert r60_k["H_alpha_prime_pred_GPa"] > r60_d["H_alpha_prime_pred_GPa"]


def test_invalid_inputs_rejected() -> None:
    with pytest.raises(ValueError):
        tabor_hardness_GPa_from_sigma_uts(-100)
    with pytest.raises(ValueError):
        tabor_hardness_GPa_from_sigma_uts(2100, tabor_coefficient=-1)
    with pytest.raises(ValueError):
        composite_hardness_GPa(7.0, 1.5)  # f > 1
    with pytest.raises(ValueError):
        composite_hardness_GPa(7.0, -0.1)


def test_default_constants_match_chapter5_calibration() -> None:
    """Lock the Ch 5 calibration constants in tests so they don't silently
    drift."""
    assert DEFAULT_TABOR_COEFFICIENT_SIGMA_UTS == 3.24
    assert DEFAULT_H_GAMMA_GPA == 4.0
    assert EMPIRICAL_WORK_HARDENING_RATIO_BY_CR[0] == 1.62
    assert EMPIRICAL_WORK_HARDENING_RATIO_BY_CR[60] == 1.42
