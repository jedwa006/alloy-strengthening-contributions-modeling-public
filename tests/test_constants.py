"""Verify the universal constants table values."""

from m54model.constants import (
    B_NM,
    FLEISCHER_BETA_MPA,
    G_MATRIX_GPA,
    SIGMA_0_MPA,
    Convention,
    StrengtheningConstants,
)


def test_basic_constants() -> None:
    assert SIGMA_0_MPA == 50.0
    assert G_MATRIX_GPA == 80.0
    assert B_NM == 0.25


def test_sun_convention() -> None:
    sun = StrengtheningConstants.from_convention(Convention.SUN)
    assert sun.M_taylor == 2.5
    assert sun.alpha_BH == 0.38
    assert sun.K_HP_MPa_um_half == 230.0


def test_wang_convention() -> None:
    wang = StrengtheningConstants.from_convention(Convention.WANG)
    assert wang.M_taylor == 2.5
    # Wang's original (alpha=0.25, M=2.5) is collapsed into effective alpha_eff=0.625
    # since dislocation.py absorbs M into alpha to match Sun's convention.
    assert wang.alpha_BH == 0.625
    assert wang.K_HP_MPa_um_half == 300.0


def test_fleischer_table_has_core_elements() -> None:
    for elem in ("Co", "Ni", "Cr", "Mo"):
        assert elem in FLEISCHER_BETA_MPA
        assert FLEISCHER_BETA_MPA[elem] > 0
