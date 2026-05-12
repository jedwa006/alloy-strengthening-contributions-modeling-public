"""Tests for the Phase 3.9a Maresca-anchored tensile-toughness predictor."""

import pytest

from m54model.toughening import (
    DEFAULT_EPS_BASELINE_MATRIX,
    DEFAULT_KAPPA_FILM_DIMENSIONLESS,
    cw_cr_tensile_toughness_sweep,
    predict_tensile_toughness_maresca,
)


def test_default_constants_locked() -> None:
    """Lock the calibrated defaults so they don't drift silently."""
    assert DEFAULT_KAPPA_FILM_DIMENSIONLESS == 0.50
    assert DEFAULT_EPS_BASELINE_MATRIX == 0.11


def test_predict_at_zero_film_recovers_matrix_only() -> None:
    """f_film = 0 → U = ε_baseline · σ_avg, no transformation contribution."""
    pred = predict_tensile_toughness_maresca(
        sigma_y_MPa=1300, sigma_uts_MPa=2100, f_film=0.0
    )
    expected = 0.11 * (1300 + 2100) / 2
    assert pred.U_total_MPa == pytest.approx(expected, abs=0.5)
    assert pred.U_film_contribution_MPa == 0.0


def test_predict_user_baseline_matches_measured_within_10pct() -> None:
    """User 0 % CR baseline: σ_y=1300, σ_UTS=2100, f_A=0.026 → U≈209 MJ/m³.
    Measured 219 ± 13 — within 10 %."""
    pred = predict_tensile_toughness_maresca(
        sigma_y_MPa=1300, sigma_uts_MPa=2100, f_film=0.026
    )
    measured = 219.0
    assert abs(pred.U_total_MPa - measured) / measured < 0.10


def test_predict_60pct_cr_within_10pct() -> None:
    """60 % CR: σ_y=1900, σ_UTS=2700, f_film=0.126 → U≈398 MJ/m³.
    Measured 434 ± 23 — within 10 %."""
    pred = predict_tensile_toughness_maresca(
        sigma_y_MPa=1900, sigma_uts_MPa=2700, f_film=0.126
    )
    measured = 434.0
    assert abs(pred.U_total_MPa - measured) / measured < 0.10


def test_kappa_film_scales_film_contribution_linearly() -> None:
    """U_film = κ_film · f_film · σ_avg — doubling κ doubles U_film."""
    p1 = predict_tensile_toughness_maresca(
        sigma_y_MPa=1900, sigma_uts_MPa=2700, f_film=0.10, kappa_film=0.5
    )
    p2 = predict_tensile_toughness_maresca(
        sigma_y_MPa=1900, sigma_uts_MPa=2700, f_film=0.10, kappa_film=1.0
    )
    assert p2.U_film_contribution_MPa == pytest.approx(
        2 * p1.U_film_contribution_MPa, rel=1e-9
    )


def test_invalid_inputs_rejected() -> None:
    with pytest.raises(ValueError):
        predict_tensile_toughness_maresca(
            sigma_y_MPa=-100, sigma_uts_MPa=2000, f_film=0.05
        )
    with pytest.raises(ValueError):
        predict_tensile_toughness_maresca(
            sigma_y_MPa=1500, sigma_uts_MPa=2000, f_film=1.5
        )
    with pytest.raises(ValueError):
        predict_tensile_toughness_maresca(
            sigma_y_MPa=1500, sigma_uts_MPa=2000, f_film=-0.05
        )


def test_sweep_returns_four_rows_with_predictions_and_misses() -> None:
    rows = cw_cr_tensile_toughness_sweep()
    assert len(rows) == 4
    expected_keys = {
        "cw_pct", "f_film", "sigma_y_MPa", "sigma_uts_MPa", "sigma_avg_MPa",
        "eps_baseline", "eps_film", "eps_total_pred",
        "U_matrix_MJ_per_m3", "U_film_MJ_per_m3", "U_total_pred_MJ_per_m3",
        "U_meas_MJ_per_m3", "U_meas_std_MJ_per_m3", "miss_pct",
    }
    assert expected_keys <= set(rows[0].keys())


def test_sweep_calibration_quality_RMSE_under_30pct() -> None:
    """At default κ_film=0.5, RMSE across the four user CR conditions
    should be under 30 % (calibration check)."""
    rows = cw_cr_tensile_toughness_sweep()
    misses = [r["miss_pct"] for r in rows if r["miss_pct"] is not None]
    rmse = (sum(m * m for m in misses) / len(misses)) ** 0.5
    assert rmse < 30.0  # actual ~15 %


def test_sweep_individual_predictions_within_30pct() -> None:
    """Per-CR misses all within ±30 % at default κ_film. The 53 % CR
    point has a known +26 % over-prediction that we don't try to fix
    (open question in FINDINGS Phase 3.9a — morphology dependence)."""
    rows = cw_cr_tensile_toughness_sweep()
    for r in rows:
        if r["miss_pct"] is not None:
            assert abs(r["miss_pct"]) < 30.0
