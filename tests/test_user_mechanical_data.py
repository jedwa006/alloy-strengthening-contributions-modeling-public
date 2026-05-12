"""Smoke tests for the user mechanical-data dataclasses."""

import pytest

from m54model.calibration import (
    USER_M54_NANOINDENTATION,
    USER_M54_TENSILE,
    USER_M54_TOUGHNESS,
    nanoindent_for_cr,
    tensile_for_cr,
    toughness_for_cr,
)


def test_tensile_lookup_round_trip() -> None:
    p = tensile_for_cr(0)
    assert p.cw_pct == 0
    assert p.sigma_y_MPa == 1300
    assert p.UTS_MPa == 2100


def test_tensile_60pct_is_strongest_and_most_ductile() -> None:
    """The 60 % CR sample has BOTH the highest σ_y AND the highest EL —
    opposite of the typical CW strength-ductility trade-off. Worth pinning."""
    p_60 = tensile_for_cr(60)
    others = [p for p in USER_M54_TENSILE if p.cw_pct != 60]
    assert p_60.sigma_y_MPa == max(p.sigma_y_MPa for p in USER_M54_TENSILE)
    assert p_60.elongation_pct == max(p.elongation_pct for p in USER_M54_TENSILE)


def test_toughness_increases_4x_to_2x_over_baseline() -> None:
    base = toughness_for_cr(0)
    high = toughness_for_cr(60)
    assert high.K_IC_MPa_m_half / base.K_IC_MPa_m_half > 1.5  # actually ≈ 2.0


def test_nanoindent_five_zones_per_cr() -> None:
    for cr in (0, 20, 40, 60):
        zones = nanoindent_for_cr(cr)
        assert len(zones) == 5
        labels = {z.zone_label for z in zones}
        assert labels == {"0-50 µm", "50-100 µm", "100-250 µm", "250-500 µm", "Core"}


def test_nanoindent_60pct_has_surface_to_core_gradient() -> None:
    """60 % CR: surface H ≈ 8 GPa, core ≈ 7.2 GPa — the surface-localized
    cumulative-shear story. Other CR conditions are flatter."""
    zones = nanoindent_for_cr(60)
    surf = zones[0].H_GPa
    core = zones[-1].H_GPa
    assert surf - core > 0.5  # at least 0.5 GPa drop


def test_nanoindent_modulus_dips_at_intermediate_cr() -> None:
    """The non-monotonic Er(CR) pattern: 0 % ~ 250, 20 % ~ 224, 40 % ~ 207,
    60 % rebounds to ~261. Pin the qualitative trend."""
    er0 = sum(z.Er_GPa for z in nanoindent_for_cr(0)) / 5
    er40 = sum(z.Er_GPa for z in nanoindent_for_cr(40)) / 5
    er60 = sum(z.Er_GPa for z in nanoindent_for_cr(60)) / 5
    assert er40 < er0
    assert er60 > er40


def test_unknown_cr_raises() -> None:
    with pytest.raises(KeyError):
        tensile_for_cr(99)
    with pytest.raises(KeyError):
        toughness_for_cr(99)
    with pytest.raises(KeyError):
        nanoindent_for_cr(99)
