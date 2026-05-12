"""Tests for the empirical strain-rate correction helper."""

import math

import pytest

from m54model.calibration import (
    EPS_DOT_SUN_2022_S_INV,
    EPS_DOT_USER_TENSILE_S_INV,
    M_TEMPERED_M54_DEFAULT,
    explain_strain_rate_correction,
    strain_rate_correction,
)


def test_correction_at_default_user_vs_sun_rates() -> None:
    """200× rate ratio at m=0.01 → ~5.4 % bump. Matches FINDINGS.md §3.5.1."""
    factor = strain_rate_correction(
        EPS_DOT_USER_TENSILE_S_INV,
        EPS_DOT_SUN_2022_S_INV,
        m=M_TEMPERED_M54_DEFAULT,
    )
    assert factor == pytest.approx(1.0544, abs=1e-3)


def test_correction_unity_when_rates_equal() -> None:
    assert strain_rate_correction(1e-3, 1e-3, m=0.01) == pytest.approx(1.0)


def test_correction_unity_when_m_zero() -> None:
    assert strain_rate_correction(1e0, 1e-6, m=0.0) == pytest.approx(1.0)


def test_explain_includes_algebra_pieces() -> None:
    text = explain_strain_rate_correction()
    assert "ε̇_ref" in text
    assert "200" in text
    assert "exp(m" in text


def test_negative_rate_rejected() -> None:
    with pytest.raises(ValueError):
        strain_rate_correction(-0.1, 5e-4, m=0.01)


def test_negative_m_rejected() -> None:
    with pytest.raises(ValueError):
        strain_rate_correction(1e-1, 5e-4, m=-0.01)


def test_correction_inverse_consistency() -> None:
    """Going up in rate then down by the same ratio recovers identity."""
    up = strain_rate_correction(1e-1, 5e-4, m=0.01)
    down = strain_rate_correction(5e-4, 1e-1, m=0.01)
    assert up * down == pytest.approx(1.0, abs=1e-9)
    assert math.log(up) == pytest.approx(-math.log(down), abs=1e-9)
