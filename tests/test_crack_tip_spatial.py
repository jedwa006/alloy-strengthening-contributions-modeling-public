"""Tests for the Phase 3.6a spatial K-field integration of PC + OC."""

import pytest

from m54model.calibration import m54_af550_45_t516_10, sun_2022_dq_t516_10
from m54model.toughening import (
    SpatialCrackTipResult,
    crack_tip_KIC,
    crack_tip_KIC_spatial,
)


def test_no_austenite_no_increment() -> None:
    """f_A = 0 → ΔK_TRIP = 0, K_total = K_matrix. Same contract as bulk version."""
    state = sun_2022_dq_t516_10()
    r = crack_tip_KIC_spatial(state, K_matrix_MPa_m_half=70.0)
    assert isinstance(r, SpatialCrackTipResult)
    assert r.delta_K_TRIP_MPa_m_half == 0.0
    assert r.K_total_MPa_m_half == 70.0


def test_spatial_matches_bulk_when_PC_saturates_everywhere() -> None:
    """With M_s_offset_K = 0 (default), Patel-Cohen triggers everywhere with
    σ > 0 → both bulk and spatial give f_transformed ≈ 1.0 → same ΔK_TRIP."""
    state = m54_af550_45_t516_10()
    bulk = crack_tip_KIC(state, K_matrix_MPa_m_half=100.0, M_s_offset_K=0)
    spatial = crack_tip_KIC_spatial(state, K_matrix_MPa_m_half=100.0, M_s_offset_K=0)
    assert spatial.delta_K_TRIP_MPa_m_half == pytest.approx(
        bulk.delta_K_TRIP_MPa_m_half, rel=0.05
    )


def test_spatial_higher_than_bulk_with_M_s_offset() -> None:
    """With non-zero M_s offset, the bulk version uses σ ≈ σ_y as the PC driver
    (the low end of the plastic zone). Spatial averages over the kidney lobe
    where σ peaks ABOVE σ_y near the tip → spatial sees larger driving force,
    so <f_PC>_spatial > f_PC_bulk and ΔK_TRIP_spatial > ΔK_TRIP_bulk."""
    state = m54_af550_45_t516_10()
    bulk = crack_tip_KIC(state, K_matrix_MPa_m_half=100.0, M_s_offset_K=50.0)
    spatial = crack_tip_KIC_spatial(state, K_matrix_MPa_m_half=100.0, M_s_offset_K=50.0)
    assert spatial.delta_K_TRIP_MPa_m_half > bulk.delta_K_TRIP_MPa_m_half
    assert spatial.f_PC_avg > 0  # some part of the zone triggered
    assert spatial.f_PC_avg < 1.0  # but not everything (offset gates the low-σ region)


def test_spatial_fractions_in_unit_interval() -> None:
    """Sanity: averaged fractions stay in [0, 1]."""
    state = m54_af550_45_t516_10()
    r = crack_tip_KIC_spatial(state, K_matrix_MPa_m_half=80.0, M_s_offset_K=80.0)
    assert 0.0 <= r.f_transformed_avg <= 1.0
    assert 0.0 <= r.f_PC_avg <= 1.0
    assert 0.0 <= r.f_OC_avg <= 1.0


def test_spatial_converges_in_few_iterations() -> None:
    state = m54_af550_45_t516_10()
    r = crack_tip_KIC_spatial(state, K_matrix_MPa_m_half=100.0)
    assert r.iterations_to_converge < 10


def test_spatial_grid_resolution_independence() -> None:
    """Doubling the grid should change the answer by < 5 % (numerical
    integration converged for this problem)."""
    state = m54_af550_45_t516_10()
    coarse = crack_tip_KIC_spatial(
        state,
        K_matrix_MPa_m_half=100.0,
        M_s_offset_K=50.0,
        n_radial=12,
        n_theta=18,
    )
    fine = crack_tip_KIC_spatial(
        state,
        K_matrix_MPa_m_half=100.0,
        M_s_offset_K=50.0,
        n_radial=24,
        n_theta=36,
    )
    rel_err = abs(coarse.delta_K_TRIP_MPa_m_half - fine.delta_K_TRIP_MPa_m_half) / max(
        fine.delta_K_TRIP_MPa_m_half, 1e-9
    )
    assert rel_err < 0.05


def test_hrr_rescale_reduces_PC_trigger_under_M_s_offset() -> None:
    """Phase 3.6c — HRR's slower σ_eq decay inside Ω_p means fewer points
    exceed the M_s-offset PC threshold than under Williams-K. <f_PC> drops
    by ~30-40 % at moderate offsets."""
    state = m54_af550_45_t516_10()
    K_field = crack_tip_KIC_spatial(
        state, K_matrix_MPa_m_half=100.0, M_s_offset_K=50.0,
        use_hrr_radial_rescale=False,
    )
    HRR = crack_tip_KIC_spatial(
        state, K_matrix_MPa_m_half=100.0, M_s_offset_K=50.0,
        use_hrr_radial_rescale=True,
    )
    assert HRR.f_PC_avg < K_field.f_PC_avg
    assert HRR.delta_K_TRIP_MPa_m_half < K_field.delta_K_TRIP_MPa_m_half
    # ~30 % drop expected; loose bounds.
    ratio = HRR.delta_K_TRIP_MPa_m_half / K_field.delta_K_TRIP_MPa_m_half
    assert 0.4 < ratio < 0.9


def test_hrr_and_K_agree_at_zero_M_s_offset() -> None:
    """With M_s_offset=0, PC saturates at 1.0 everywhere in Ω_p regardless of
    σ_eq magnitude — so HRR vs K-field agree."""
    state = m54_af550_45_t516_10()
    K_field = crack_tip_KIC_spatial(
        state, K_matrix_MPa_m_half=100.0, M_s_offset_K=0.0,
        use_hrr_radial_rescale=False,
    )
    HRR = crack_tip_KIC_spatial(
        state, K_matrix_MPa_m_half=100.0, M_s_offset_K=0.0,
        use_hrr_radial_rescale=True,
    )
    assert HRR.delta_K_TRIP_MPa_m_half == pytest.approx(
        K_field.delta_K_TRIP_MPa_m_half, rel=0.01
    )


def test_spatial_repr_includes_fractions() -> None:
    state = m54_af550_45_t516_10()
    r = crack_tip_KIC_spatial(state, K_matrix_MPa_m_half=80.0, M_s_offset_K=50.0)
    s = repr(r)
    assert "K_matrix" in s
    assert "f_PC" in s
    assert "f_OC" in s
    assert "K_total" in s
