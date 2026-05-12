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
