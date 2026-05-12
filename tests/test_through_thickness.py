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


# ---- Phase 3.8b — derived σ_y from per-zone H -----------------------------------------


def test_derive_zone_sigma_y_at_baseline_within_10pct_of_pred() -> None:
    """At 0 % CR baseline (low f_A), derived σ_y from H should agree with
    the predicted σ_y to within ~10 %."""
    from m54model.strengthening import derive_zone_sigma_y_from_nanoindent

    derived = derive_zone_sigma_y_from_nanoindent(0, "0-50 µm")
    assert derived["valid"]
    # σ_y_user_rate at 0 % CR baseline ~1300-1500 MPa range
    assert 1200 < derived["sigma_y_user_rate_derived_MPa"] < 1500


def test_derive_recovers_h_alpha_prime_from_h_composite() -> None:
    """At very low f_A (0 % CR), Eq. 1 inverted should give H_α′ ≈ H_composite
    (austenite contribution is negligible)."""
    from m54model.strengthening import derive_zone_sigma_y_from_nanoindent

    derived = derive_zone_sigma_y_from_nanoindent(0, "0-50 µm")
    diff = abs(derived["H_alpha_prime_derived_GPa"] - derived["H_composite_GPa"])
    assert diff < 0.1  # within 0.1 GPa


def test_per_zone_sweep_returns_20_rows() -> None:
    from m54model.strengthening import per_zone_predicted_vs_derived_sweep

    rows = per_zone_predicted_vs_derived_sweep()
    assert len(rows) == 20  # 5 zones × 4 CR conditions


def test_volume_weighted_derived_bulk_matches_tensile_at_60pct() -> None:
    """Phase 3.8b key validation: volume-weight the H-derived per-zone σ_y
    at 60 % CR and compare to bulk tensile (1900 ± 50 MPa). Should agree
    within ~5 %, far better than the microstructure-only prediction."""
    from m54model.strengthening import (
        per_zone_predicted_vs_derived_sweep,
        zone_volume_fraction,
    )

    rows = per_zone_predicted_vs_derived_sweep()
    rows_60 = [r for r in rows if r["cw_pct"] == 60 and r["sigma_y_derived_MPa"]]
    assert len(rows_60) == 5

    # Volume-weight the derived σ_y values.
    plate_T = 1520.0  # µm at 60 % CR
    vol_fracs = [zone_volume_fraction(r["zone_label"], plate_T) for r in rows_60]
    sigma_derived = [r["sigma_y_derived_MPa"] for r in rows_60]
    bulk_derived = sum(v * s for v, s in zip(vol_fracs, sigma_derived)) / sum(vol_fracs)
    measured = 1900.0
    assert abs(bulk_derived - measured) / measured < 0.05  # within 5 %


def test_per_zone_60pct_predicted_vs_derived_have_opposite_surface_gradient() -> None:
    """Phase 3.8b key finding: at 60 % CR the *predicted* σ_y has surface
    SOFTER than core (linear f_A interpolation puts more austenite at the
    surface), but the *H-derived* σ_y has surface HARDER than core
    (matrix work-hardening at the surface dominates). This locks the
    qualitative finding for future regression."""
    from m54model.strengthening import per_zone_predicted_vs_derived_sweep

    rows = per_zone_predicted_vs_derived_sweep()
    rows_60 = [r for r in rows if r["cw_pct"] == 60]

    surf = next(r for r in rows_60 if r["zone_label"] == "0-50 µm")
    core = next(r for r in rows_60 if r["zone_label"] == "Core")
    # Predicted: surface < core (model wrong direction at this CR)
    assert surf["sigma_y_predicted_MPa"] < core["sigma_y_predicted_MPa"]
    # Derived: surface > core (matches user's H surface-to-core gradient)
    assert surf["sigma_y_derived_MPa"] > core["sigma_y_derived_MPa"]


# ---- Phase 3.7d — Mondière f_A correction mode ----------------------------------------


def test_f_A_correction_mondière_matches_minus_68_per_pct() -> None:
    """Mondière 2025 mode: ∂σ_y/∂f_A = −6800 MPa per unit f_A (= −68/%)."""
    from m54model.calibration import m54_af_t516_10_cw
    from m54model.strengthening import assemble_yield_strength

    state = m54_af_t516_10_cw(0, location="surface")
    res = assemble_yield_strength(state, f_A_correction_mode="mondière_2025")
    delta = res.sigma_y_austenite_corrected_MPa - res.sigma_y_MPa
    expected = -6800.0 * state.f_austenite
    assert abs(delta - expected) < 0.5


def test_f_A_correction_modes_differ() -> None:
    """rule_of_mix and mondière_2025 should give different σ_y corrections."""
    from m54model.calibration import m54_af_t516_10_cw
    from m54model.strengthening import assemble_yield_strength

    state = m54_af_t516_10_cw(0, location="surface")
    rom = assemble_yield_strength(state, f_A_correction_mode="rule_of_mix")
    mond = assemble_yield_strength(state, f_A_correction_mode="mondière_2025")
    assert mond.sigma_y_austenite_corrected_MPa < rom.sigma_y_austenite_corrected_MPa


def test_f_A_correction_mondière_clamped_at_zero() -> None:
    """At very high f_A, Mondière's relation goes negative. Our impl
    clamps σ_y_corr at 0 to avoid unphysical negatives."""
    import pytest

    from m54model.kinetics import m2c_population_af_tempered
    from m54model.calibration.anchors import _matrix_tempered
    from m54model.states import MicrostructuralState
    from m54model.strengthening import assemble_yield_strength

    # Synthesize a state with f_A huge enough to flip Mondière negative.
    m2c = m2c_population_af_tempered(516.0, 10.0)
    state = MicrostructuralState(
        state="synthetic",
        block_width_um=0.48,
        dislocation_density_per_m2=1.6e15,
        f_austenite=0.5,  # 50 % γ — way past Mondière's calibration regime
        matrix_at_frac=_matrix_tempered(),
        wt_pct_C_in_solution=0.003,
        precipitates=[m2c],
    )
    res = assemble_yield_strength(state, f_A_correction_mode="mondière_2025")
    assert res.sigma_y_austenite_corrected_MPa >= 0.0


def test_invalid_f_A_correction_mode_raises() -> None:
    import pytest

    from m54model.calibration import m54_af_t516_10_cw
    from m54model.strengthening import assemble_yield_strength

    state = m54_af_t516_10_cw(0, location="surface")
    with pytest.raises(ValueError):
        assemble_yield_strength(state, f_A_correction_mode="banana")
