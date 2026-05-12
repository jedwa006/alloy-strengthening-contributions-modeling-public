"""Tests for the Phase 3.8a through-thickness mixture model."""

import pytest

from m54model.strengthening import (
    PLATE_THICKNESS_UM_BY_CR,
    ZONE_LABELS,
    interpolate_at_depth,
    microstructure_at_zone,
    predict_bulk_sigma_y_through_thickness,
    predict_zone_sigma_y,
    through_thickness_sweep,
    zone_volume_fraction,
)


def test_zone_volume_fractions_sum_to_one() -> None:
    """For any plate thickness ≥ 1 mm, the 5 zones should partition the
    half-plate volume exactly (sum of fractions = 1.0)."""
    for T in (3800.0, 3040.0, 2280.0, 1520.0):
        total = sum(zone_volume_fraction(z, T) for z in ZONE_LABELS)
        assert total == pytest.approx(1.0, abs=1e-9), f"T={T}: total={total}"


def test_zone_fractions_shift_with_plate_thinning() -> None:
    """As plate thins (CR increases), the surface-region zones occupy a
    larger fraction of the total volume."""
    z4_at_0pct = zone_volume_fraction("250-500 µm", 3800.0)
    z4_at_60pct = zone_volume_fraction("250-500 µm", 1520.0)
    assert z4_at_60pct > z4_at_0pct
    # At 0 % CR (3.8 mm): zone 4 = 250/1900 = 13.2 %
    # At 60 % CR (1.52 mm): zone 4 = 250/760 = 32.9 %
    assert z4_at_0pct == pytest.approx(0.132, abs=0.005)
    assert z4_at_60pct == pytest.approx(0.329, abs=0.005)


def test_interpolate_at_depth_endpoints() -> None:
    assert interpolate_at_depth(1.0, 5.0, 0.0) == 1.0
    assert interpolate_at_depth(1.0, 5.0, 1.0) == 5.0
    assert interpolate_at_depth(1.0, 5.0, 0.5) == 3.0


def test_interpolate_clips_outside_unit_interval() -> None:
    """Defensive: depth_normalized < 0 or > 1 clipped to endpoints."""
    assert interpolate_at_depth(1.0, 5.0, -0.1) == 1.0
    assert interpolate_at_depth(1.0, 5.0, 1.5) == 5.0


def test_microstructure_at_zone_1_recovers_surface_at_baseline() -> None:
    """Zone 1 (0-50 µm midpoint = 25 µm) at 0 % CR should be close to
    the user's surface ASTAR f_A = 0.013."""
    micro = microstructure_at_zone(0, "0-50 µm")
    # depth_normalized = 25/(3800/2) = 25/1900 ≈ 0.013, very near surface
    assert micro["depth_normalized"] == pytest.approx(0.013, abs=0.005)
    assert micro["f_A"] == pytest.approx(0.013, abs=0.005)  # user surface 0% value


def test_microstructure_at_core_recovers_core_value() -> None:
    """Core zone interpolation should hit the core measurement closely."""
    micro = microstructure_at_zone(60, "Core")
    # Core is deep — depth_normalized > 0.5
    assert micro["depth_normalized"] > 0.5
    # f_A core at 60 % CR per USER_M54_CW_AUSTENITE_CORE = 0.126
    assert micro["f_A"] == pytest.approx(0.126, abs=0.04)


def test_predict_zone_sigma_y_returns_reasonable_value_at_baseline() -> None:
    """0 % CR baseline: per-zone σ_y predictions should be in the ~1300-1500
    MPa range (close to the +9 % over-predicted bulk)."""
    z = predict_zone_sigma_y(0, "0-50 µm")
    assert 1200 < z.sigma_y_user_rate_MPa < 1600


def test_through_thickness_sweep_returns_four_rows() -> None:
    rows = through_thickness_sweep()
    assert len(rows) == 4
    cw_pcts = sorted(r["cw_pct"] for r in rows)
    assert cw_pcts == [0, 20, 40, 60]


def test_bulk_at_0pct_close_to_direct_core_prediction() -> None:
    """At 0 % CR with K_sub=150, the through-thickness bulk should be
    within ~10 % of the direct-core prediction (no cw, so the two should
    largely agree — only f_A differs slightly)."""
    from m54model.calibration import predict_cw_cr_sweep

    direct_core = next(
        r for r in predict_cw_cr_sweep(location="core", subblock_hp_K_MPa_um_half=150)
        if r["cw_pct"] == 0
    )
    bulk_tt = predict_bulk_sigma_y_through_thickness(0, subblock_hp_K_MPa_um_half=150)
    rel_diff = abs(
        bulk_tt["bulk_sigma_y_MPa"] - direct_core["sigma_y_user_rate_MPa"]
    ) / direct_core["sigma_y_user_rate_MPa"]
    assert rel_diff < 0.10


def test_tt_disagrees_with_direct_core_at_60pct() -> None:
    """Phase 3.8a key finding: at 60 % CR, the through-thickness mixture
    gives a different bulk σ_y than the direct-core+K_sub=150 prediction.
    The two simplifications are NOT mutually consistent — physics-based TT
    is softer than empirically-tuned direct-core. Lock the disagreement
    so future regressions are noticed."""
    from m54model.calibration import predict_cw_cr_sweep

    direct_core = next(
        r for r in predict_cw_cr_sweep(location="core", subblock_hp_K_MPa_um_half=150)
        if r["cw_pct"] == 60
    )
    bulk_tt = predict_bulk_sigma_y_through_thickness(60, subblock_hp_K_MPa_um_half=150)
    diff_MPa = direct_core["sigma_y_user_rate_MPa"] - bulk_tt["bulk_sigma_y_MPa"]
    # Direct-core ~1923 MPa; TT bulk ~1641 MPa; difference ~280 MPa
    assert diff_MPa > 200
    assert diff_MPa < 400


def test_plate_thickness_table_locks_chapter5_values() -> None:
    """Lock the Ch 5 plate-thickness values in the test."""
    expected = {0: 3800.0, 20: 3040.0, 40: 2280.0, 60: 1520.0}
    assert PLATE_THICKNESS_UM_BY_CR == expected
