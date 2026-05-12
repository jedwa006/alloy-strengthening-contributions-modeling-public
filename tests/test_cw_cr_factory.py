"""Tests for the Phase 3.6d cw/cr state factory + sweep helper."""

import pytest

from m54model.calibration import (
    m54_af550_45_t516_10,
    m54_af_t516_10_cw,
    predict_cw_cr_sweep,
)
from m54model.strengthening import assemble_yield_strength


def test_factory_at_cw_0_surface_matches_baseline_f_A() -> None:
    """At cw_pct=0, location=surface, the factory should pick up the
    surface ASTAR f_A = 0.013 (matching the baseline `m54_af550_45_t516_10`)."""
    state = m54_af_t516_10_cw(0, location="surface")
    base = m54_af550_45_t516_10()
    assert state.f_austenite == pytest.approx(base.f_austenite, rel=1e-3)


def test_factory_uses_user_GND_density() -> None:
    """ρ in the state should be the user's measured BCC median GND."""
    s0 = m54_af_t516_10_cw(0, location="surface")
    s40 = m54_af_t516_10_cw(40, location="surface")
    assert s0.dislocation_density_per_m2 == pytest.approx(1.6e15, rel=0.05)
    assert s40.dislocation_density_per_m2 == pytest.approx(7.9e15, rel=0.05)
    # GND peaks at 40 % CR, drops back at 60 %.
    s60 = m54_af_t516_10_cw(60, location="surface")
    assert s40.dislocation_density_per_m2 > s60.dislocation_density_per_m2


def test_factory_surface_vs_core_f_A_at_40_cr() -> None:
    """40 % CR: surface f_A = 26.4 %, core = 9.9 % per ASTAR."""
    sf = m54_af_t516_10_cw(40, location="surface")
    cr = m54_af_t516_10_cw(40, location="core")
    assert sf.f_austenite == pytest.approx(0.264, rel=0.05)
    assert cr.f_austenite == pytest.approx(0.099, rel=0.05)


def test_factory_invalid_cw_raises() -> None:
    with pytest.raises(KeyError):
        m54_af_t516_10_cw(99, location="surface")


def test_factory_invalid_location_raises() -> None:
    with pytest.raises(ValueError):
        m54_af_t516_10_cw(0, location="middle")


def test_predict_sweep_default_core() -> None:
    rows = predict_cw_cr_sweep(location="core")
    assert len(rows) == 4
    cw0 = next(r for r in rows if r["cw_pct"] == 0)
    cw60 = next(r for r in rows if r["cw_pct"] == 60)
    assert cw0["sigma_y_meas_MPa"] == 1300
    assert cw60["sigma_y_meas_MPa"] == 1900
    # 0 % CR: model over-predicts by ~10 %; 60 % CR: under-predicts by ~15-20 %.
    assert cw0["miss_pct"] is not None and cw0["miss_pct"] > 0
    assert cw60["miss_pct"] is not None and cw60["miss_pct"] < -10


def test_predict_sweep_no_strain_rate_correction() -> None:
    """When apply_strain_rate_correction=False, sigma_y_qs == sigma_y_user_rate."""
    rows = predict_cw_cr_sweep(apply_strain_rate_correction=False)
    for r in rows:
        assert r["sigma_y_qs_MPa"] == r["sigma_y_user_rate_MPa"]


def test_sigma_y_responds_to_GND() -> None:
    """σ_y at 20 % CR (ρ_GND = 6.3e15) should exceed σ_y at 0 % (ρ_GND = 1.6e15)
    by ~300 MPa from σ_ρ alone, in the absence of countervailing f_A change."""
    s0 = m54_af_t516_10_cw(0, location="core")
    s20 = m54_af_t516_10_cw(20, location="core")
    res0 = assemble_yield_strength(s0)
    res20 = assemble_yield_strength(s20)
    # Both have low f_A so the rule-of-mix correction is small;
    # the σ_ρ rise should dominate.
    delta = res20.contributions_MPa["sigma_rho"] - res0.contributions_MPa["sigma_rho"]
    assert delta > 250  # ~300 expected
    assert delta < 350


def test_ssd_multiplier_default_is_one() -> None:
    """Default ssd_multiplier = 1.0 → uses GND directly as total ρ."""
    s = m54_af_t516_10_cw(60, location="core")
    # 60 % CR core BCC GND = 6.3e15.
    assert s.dislocation_density_per_m2 == pytest.approx(6.3e15, rel=0.05)


def test_ssd_multiplier_scales_dislocation_density() -> None:
    """ssd_multiplier = 2.5 → ρ_total = 2.5 × ρ_GND."""
    s1 = m54_af_t516_10_cw(60, location="core", ssd_multiplier=1.0)
    s25 = m54_af_t516_10_cw(60, location="core", ssd_multiplier=2.5)
    assert s25.dislocation_density_per_m2 == pytest.approx(
        2.5 * s1.dislocation_density_per_m2, rel=1e-6
    )


def test_ssd_multiplier_lower_than_one_rejected() -> None:
    """ssd_multiplier < 1.0 means subtracting from GND, which is unphysical."""
    with pytest.raises(ValueError):
        m54_af_t516_10_cw(60, location="core", ssd_multiplier=0.5)


def test_ssd_multiplier_label_changes() -> None:
    """A non-default ssd_multiplier should appear in the state label so
    downstream plots/tables don't conflate the two."""
    s_default = m54_af_t516_10_cw(40, location="surface")
    s_with_ssd = m54_af_t516_10_cw(40, location="surface", ssd_multiplier=2.0)
    assert "SSD" not in s_default.label  # default doesn't advertise the knob
    assert "SSD" in s_with_ssd.label.upper() or "×" in s_with_ssd.label


def test_predict_sweep_with_ssd_multiplier_closes_60pct_gap() -> None:
    """Sensitivity check: ssd_multiplier ≈ 2.5 brings 60 % CR miss to <2 %.
    Doesn't fix 0 % CR (separate issue — block size). See FINDINGS Phase 3.6e."""
    rows = predict_cw_cr_sweep(location="core", ssd_multiplier=2.5)
    r60 = next(r for r in rows if r["cw_pct"] == 60)
    assert abs(r60["miss_pct"]) < 2.0
    # And 0 % CR is *more* over-predicted, not fixed.
    r0 = next(r for r in rows if r["cw_pct"] == 0)
    assert r0["miss_pct"] > 20.0


def test_subblock_hp_default_disabled() -> None:
    """Default subblock_hp_K_MPa_um_half = 0 → no sub-block contribution
    (preserves Phase 3.6d/e behavior)."""
    s = m54_af_t516_10_cw(60, location="core")
    assert getattr(s, "_subblock_HP_increment_MPa", 0.0) == 0.0


def test_subblock_hp_zero_at_baseline_by_construction() -> None:
    """Sub-block HP increment is computed RELATIVE to 0 % CR — so at 0 %
    it's identically zero regardless of K_sub."""
    s = m54_af_t516_10_cw(0, location="core", subblock_hp_K_MPa_um_half=200)
    assert getattr(s, "_subblock_HP_increment_MPa", 0.0) == 0.0


def test_subblock_hp_increment_at_60pct_core() -> None:
    """K_sub = 150 with core baseline d=212 nm → d=51 nm at 60% CR.
    Δσ = 150 × (1/√0.054 - 1/√0.212) ≈ 150 × 2.13 ≈ 320 MPa."""
    s = m54_af_t516_10_cw(60, location="core", subblock_hp_K_MPa_um_half=150)
    delta = getattr(s, "_subblock_HP_increment_MPa", 0.0)
    assert delta == pytest.approx(320.0, abs=20.0)


def test_subblock_hp_negative_K_rejected() -> None:
    with pytest.raises(ValueError):
        m54_af_t516_10_cw(60, location="core", subblock_hp_K_MPa_um_half=-50)


def test_predict_sweep_subblock_hp_closes_60pct_without_touching_baseline() -> None:
    """K_sub = 150 with default CR-engaged refinement fraction (Phase 3.7b)
    closes the 60 % gap to <2 % AND keeps the 0 % miss unchanged at +9 %.
    f_engaged(60%) = 1.0 so this matches Phase 3.6f uniform behavior at 60 %."""
    rows = predict_cw_cr_sweep(location="core", subblock_hp_K_MPa_um_half=150)
    r0 = next(r for r in rows if r["cw_pct"] == 0)
    r60 = next(r for r in rows if r["cw_pct"] == 60)
    assert r0["miss_pct"] == pytest.approx(9.2, abs=0.5)  # unchanged from default
    assert abs(r60["miss_pct"]) < 2.0


def test_default_engagement_fraction_table() -> None:
    """Phase 3.7b: lock the empirical knot points so they don't drift silently."""
    from m54model.calibration.anchors import (
        DEFAULT_REFINEMENT_ENGAGEMENT_FRACTION_BY_CR,
    )

    expected = {0: 0.0, 20: 0.0, 40: 0.7, 60: 1.0}
    assert DEFAULT_REFINEMENT_ENGAGEMENT_FRACTION_BY_CR == expected


def test_engagement_fraction_zero_at_20pct_keeps_default_sigma_y() -> None:
    """Phase 3.7b key claim: with K_sub=150 and the default f_engaged(20%)=0,
    σ_y at 20 % CR matches the K_sub=0 prediction (no sub-block contribution
    yet at 20 %, refinement still surface-localized per Chapter 4)."""
    rows_default = predict_cw_cr_sweep(location="core")
    rows_kSub_engaged = predict_cw_cr_sweep(
        location="core", subblock_hp_K_MPa_um_half=150
    )
    r20_default = next(r for r in rows_default if r["cw_pct"] == 20)
    r20_engaged = next(r for r in rows_kSub_engaged if r["cw_pct"] == 20)
    assert r20_default["sigma_y_user_rate_MPa"] == r20_engaged["sigma_y_user_rate_MPa"]


def test_explicit_engagement_fraction_1_recovers_uniform_K_sub() -> None:
    """Passing refinement_engagement_fraction=1.0 explicitly recovers the
    Phase 3.6f uniform-K_sub behavior (which over-predicted H_α′(20%) by
    +17 % per Phase 3.7a forward-calc)."""
    state_engaged = m54_af_t516_10_cw(
        20, location="core", subblock_hp_K_MPa_um_half=150
    )
    state_uniform = m54_af_t516_10_cw(
        20, location="core", subblock_hp_K_MPa_um_half=150,
        refinement_engagement_fraction=1.0,
    )
    delta_engaged = getattr(state_engaged, "_subblock_HP_increment_MPa", 0.0)
    delta_uniform = getattr(state_uniform, "_subblock_HP_increment_MPa", 0.0)
    # f_engaged(20%) = 0 default → delta = 0; uniform = full Phase-3.6f delta.
    assert delta_engaged == 0.0
    assert delta_uniform > 200  # ~235 MPa per Phase 3.6f


def test_engagement_fraction_at_60pct_matches_uniform() -> None:
    """f_engaged(60%) = 1.0 so default engagement and uniform K_sub agree at 60 %."""
    state_engaged = m54_af_t516_10_cw(
        60, location="core", subblock_hp_K_MPa_um_half=150
    )
    state_uniform = m54_af_t516_10_cw(
        60, location="core", subblock_hp_K_MPa_um_half=150,
        refinement_engagement_fraction=1.0,
    )
    delta_engaged = getattr(state_engaged, "_subblock_HP_increment_MPa", 0.0)
    delta_uniform = getattr(state_uniform, "_subblock_HP_increment_MPa", 0.0)
    assert delta_engaged == pytest.approx(delta_uniform, rel=1e-9)


def test_f_A_source_default_is_astar_surface() -> None:
    """Default behavior unchanged from Phase 3.6d/e/f."""
    s = m54_af_t516_10_cw(0, location="surface")  # no f_A_source
    assert s.f_austenite == pytest.approx(0.013, rel=0.01)


def test_f_A_source_xrd_bulk_at_baseline() -> None:
    """XRD-bulk Modified Miller V_γ at 0 % CR = 4.81 % (Phase 3.6b)."""
    s = m54_af_t516_10_cw(0, location="core", f_A_source="xrd_bulk")
    assert s.f_austenite == pytest.approx(0.0481, rel=0.01)


def test_f_A_source_xrd_bulk_falls_back_at_higher_cr() -> None:
    """At 20/40/60 % CR the bulk XRD γ peaks are at noise — fallback to
    ASTAR core (Phase 3.6h)."""
    from m54model.calibration.user_trip_data import USER_M54_CW_AUSTENITE_CORE

    s = m54_af_t516_10_cw(60, location="core", f_A_source="xrd_bulk")
    expected = next(p for p in USER_M54_CW_AUSTENITE_CORE if p.cw_pct == 60).f_austenite
    assert s.f_austenite == pytest.approx(expected, rel=0.01)


def test_f_A_source_invalid_raises() -> None:
    with pytest.raises(ValueError):
        m54_af_t516_10_cw(0, location="core", f_A_source="banana")


def test_f_A_source_xrd_bulk_reduces_baseline_miss() -> None:
    """XRD-bulk f_A pushes 0 % CR miss DOWN from +10 % to ~+7 %.
    Documents Phase 3.6h finding that bulk γ-content is a meaningful
    contributor to the +10 % baseline over-prediction."""
    rows_default = predict_cw_cr_sweep(location="core")
    rows_xrd = predict_cw_cr_sweep(location="core", f_A_source="xrd_bulk")
    r0_default = next(r for r in rows_default if r["cw_pct"] == 0)
    r0_xrd = next(r for r in rows_xrd if r["cw_pct"] == 0)
    assert r0_xrd["miss_pct"] < r0_default["miss_pct"]
    assert r0_xrd["miss_pct"] < 8.0  # ~7.4 % expected
