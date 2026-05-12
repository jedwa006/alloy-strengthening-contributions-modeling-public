"""TRIP-toughening validation against original literature.

- Patel-Cohen 1953: reproduce Table I dM_s/dσ slopes for Fe-Ni-C alloys.
- Olson-Cohen 1975: reproduce 304 SS f_α′(ε) curves at -188 °C and 22 °C
  using Fig. 2 (a, b) parameters; verify fitter recovers Angel's input curves.
"""

import numpy as np

from m54model.toughening import (
    OlsonCohenParams,
    fit_olson_cohen,
    olson_cohen_volume_fraction,
    patel_cohen_max_work,
    patel_cohen_ms_shift,
    patel_cohen_optimal_orientation,
)

# ---- Patel-Cohen 1953 anchors (Table I) ----------------------------------------------

# Fe-Ni transformation strains from Patel-Cohen 1953 §3.2:
GAMMA_0_FE_NI = 0.20
EPS_0_FE_NI = 0.04

# Fe-Ni thermodynamics from Patel-Cohen 1953 Eq. 9 (Jones-Pumphrey):
DF_DT_CAL_PER_MOL_K_FE_NI_C = 1.33
DF_DT_CAL_PER_MOL_K_FE_NI = 1.23
MOLAR_VOLUME_FE_NI_M3_PER_MOL = 7.1e-6  # ~ for austenite

# 1000 psi = 6.895 MPa
ONE_KSI_MPA = 6.895


def test_patel_cohen_optimal_angle_fe_ni() -> None:
    """tan 2θ = γ₀/ε₀ = 5; 2θ ≈ 78.7°, θ ≈ 39.35°."""
    theta = patel_cohen_optimal_orientation(GAMMA_0_FE_NI, EPS_0_FE_NI)
    assert abs(np.degrees(2 * theta) - 78.69) < 0.5


def test_patel_cohen_tension_slope_fe_ni_c() -> None:
    """0.5 C - 20 Ni - bal Fe under uniaxial tension.
    Patel-Cohen 1953 Table I: dM_s/dσ_calc = +1.07 °C/ksi, exp = +1.0 °C/ksi.
    """
    dMs_per_ksi = patel_cohen_ms_shift(
        sigma_uniaxial_MPa=ONE_KSI_MPA,
        gamma_0=GAMMA_0_FE_NI,
        eps_0=EPS_0_FE_NI,
        dF_dT_cal_per_mol_K=DF_DT_CAL_PER_MOL_K_FE_NI_C,
        molar_volume_m3_per_mol=MOLAR_VOLUME_FE_NI_M3_PER_MOL,
        mode="tension",
    )
    assert 0.95 < dMs_per_ksi < 1.20, f"got {dMs_per_ksi:.2f} °C/ksi (PC reports +1.07)"


def test_patel_cohen_compression_smaller_than_tension() -> None:
    """Patel-Cohen Table I: tension dM_s/dσ > compression dM_s/dσ because in
    compression the normal-stress component opposes (σ_n × ε₀ negative)."""
    dMs_tension = patel_cohen_ms_shift(
        ONE_KSI_MPA,
        GAMMA_0_FE_NI,
        EPS_0_FE_NI,
        DF_DT_CAL_PER_MOL_K_FE_NI_C,
        MOLAR_VOLUME_FE_NI_M3_PER_MOL,
        mode="tension",
    )
    dMs_compression = patel_cohen_ms_shift(
        ONE_KSI_MPA,
        GAMMA_0_FE_NI,
        EPS_0_FE_NI,
        DF_DT_CAL_PER_MOL_K_FE_NI_C,
        MOLAR_VOLUME_FE_NI_M3_PER_MOL,
        mode="compression",
    )
    assert dMs_tension > dMs_compression > 0


def test_patel_cohen_hydrostatic_lowers_ms() -> None:
    """Hydrostatic pressure has only the dilatation coupling, which opposes
    a +4% volume-expanding transformation. Patel-Cohen Table I: -0.38 °C/ksi calc."""
    dMs = patel_cohen_ms_shift(
        ONE_KSI_MPA,
        GAMMA_0_FE_NI,
        EPS_0_FE_NI,
        DF_DT_CAL_PER_MOL_K_FE_NI,
        MOLAR_VOLUME_FE_NI_M3_PER_MOL,
        mode="hydrostatic",
    )
    assert -0.50 < dMs < -0.30, f"got {dMs:.2f} °C/ksi (PC reports -0.38)"


def test_patel_cohen_shear_dominates_for_high_aspect() -> None:
    """For γ₀ >> ε₀, tension and compression should approach each other (since
    shear-only contribution dominates and shear is symmetric)."""
    high_gamma = 0.50
    low_eps = 0.001
    U_tension = patel_cohen_max_work(100, high_gamma, low_eps, mode="tension")
    U_compression = patel_cohen_max_work(100, high_gamma, low_eps, mode="compression")
    assert abs(U_tension - U_compression) / max(U_tension, U_compression) < 0.05


# ---- Olson-Cohen 1975 anchors --------------------------------------------------------

# Olson-Cohen Fig. 2 (a, b) params for 304 SS at low T (saturation regime):
ANGEL_LOW_T = OlsonCohenParams(alpha=12.9, beta=2.0, n=4.5, T_celsius=-188)

# Olson-Cohen at room temp:
ANGEL_RT = OlsonCohenParams(alpha=3.55, beta=0.30, n=4.5, T_celsius=22)


def test_olson_cohen_zero_strain_zero_martensite() -> None:
    assert olson_cohen_volume_fraction(0.0, ANGEL_LOW_T) == 0.0


def test_olson_cohen_low_T_saturates_high() -> None:
    """At -188 °C with α=12.9, β=2.0 the curve saturates near f_α′ ≈ 0.86 by ε=0.6
    per Olson-Cohen Fig. 1."""
    f = olson_cohen_volume_fraction(epsilon=0.6, params=ANGEL_LOW_T)
    assert 0.80 < f < 0.92, f"got f={f:.3f} at ε=0.6, -188 °C"


def test_olson_cohen_RT_saturates_low() -> None:
    """At 22 °C with α=3.55, β=0.30 the curve saturates well below 1 — Olson-Cohen
    notes 304 SS at 22 °C reaches only ~0.25 by ε=0.6."""
    f = olson_cohen_volume_fraction(epsilon=0.6, params=ANGEL_RT)
    assert 0.10 < f < 0.40, f"got f={f:.3f} at ε=0.6, 22 °C"


def test_olson_cohen_monotonic_in_strain() -> None:
    eps_grid = np.linspace(0.0, 0.8, 20)
    fs = [olson_cohen_volume_fraction(e, ANGEL_LOW_T) for e in eps_grid]
    assert all(fs[i] <= fs[i + 1] + 1e-9 for i in range(len(fs) - 1))


def test_olson_cohen_fit_recovers_input_params() -> None:
    """Generate synthetic data from ANGEL_LOW_T, then fit α, β. Should recover
    the inputs to within a few percent."""
    eps = np.linspace(0.05, 0.6, 12)
    f_target = [olson_cohen_volume_fraction(e, ANGEL_LOW_T) for e in eps]
    fit = fit_olson_cohen(list(eps), f_target, n=4.5, T_celsius=-188)
    assert abs(fit.alpha - ANGEL_LOW_T.alpha) / ANGEL_LOW_T.alpha < 0.05
    assert abs(fit.beta - ANGEL_LOW_T.beta) / ANGEL_LOW_T.beta < 0.05
