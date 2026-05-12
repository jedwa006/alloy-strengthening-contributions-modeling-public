"""End-to-end smoke tests against Sun 2022 anchors.

These verify the pipeline runs and returns sane numbers. They do NOT yet
require predictions to match measured YS within calibration tolerance —
the Fleischer placeholder coefficients for W, V, C are uncalibrated, so
expect ~10–25 % miss until Phase 1 calibration completes.
"""

from m54model import (
    FERRIUM_M54,
    MicrostructuralState,
    PrecipitatePopulation,
    assemble_yield_strength,
)
from m54model.alloys.ferrium_m54 import (
    SUN_2022_DQ,
    SUN_2022_DQ_T516_10,
)


def _matrix_at_frac_dq() -> dict[str, float]:
    """At-fraction matrix composition for the DQ state.

    All alloying elements still in solid solution (no carbide precipitation
    has happened yet — only minor undissolved Ti-MC pinners).
    """
    return FERRIUM_M54.at_frac()


def _matrix_at_frac_tempered() -> dict[str, float]:
    """At-fraction matrix after M2C precipitation has consumed Mo, Cr, W, V, C.

    Approximates Wang 2024 / Mondière APT measurements: M2C composition
    (Mo 0.50 + Cr 0.125 + W 0.10 + Fe 0.10 + Ni 0.10 + V 0.025)2C means
    ~1.5 vol% M2C consumes the bulk of these elements and most of the C.
    Quick rule-of-thumb: 80 % of Mo/Cr/W/V and 99 % of C consumed.
    """
    af = FERRIUM_M54.at_frac()
    consumed = {"Mo": 0.80, "Cr": 0.80, "W": 0.80, "V": 0.80, "C": 0.99}
    matrix = {k: v * (1.0 - consumed.get(k, 0.0)) for k, v in af.items()}
    # renormalise so total is 1
    total = sum(matrix.values())
    return {k: v / total for k, v in matrix.items()}


def test_dq_state_predicts_in_range() -> None:
    """DQ baseline: anchor YS = 1420 MPa (Sun 2022)."""
    state = MicrostructuralState(
        state="direct_quench",
        block_width_um=1.18,
        dislocation_density_per_m2=2.08e15,
        f_austenite=0.0,
        matrix_at_frac=_matrix_at_frac_dq(),
        precipitates=[],
        label="Sun 2022 DQ",
    )
    result = assemble_yield_strength(state)
    assert "sigma_0" in result.contributions_MPa
    assert "sigma_HP" in result.contributions_MPa
    assert "sigma_rho" in result.contributions_MPa
    assert "sigma_ss" in result.contributions_MPa
    # Sane range — placeholder Fleischer betas mean we may be off by 100-300 MPa.
    assert 800 < result.sigma_y_MPa < 2000, (
        f"DQ prediction {result.sigma_y_MPa:.0f} MPa is outside sanity range"
    )
    # Anchor for record-keeping
    miss_MPa = result.sigma_y_MPa - SUN_2022_DQ.YS_MPa
    print(
        f"DQ: predicted {result.sigma_y_MPa:.0f}, anchor {SUN_2022_DQ.YS_MPa}, "
        f"miss {miss_MPa:+.0f} MPa"
    )


def test_dq_tempered_state_with_m2c() -> None:
    """DQ + T516/10: anchor YS = 1762 MPa. Uses Wang 520/8 M2C population
    as the closest measured anchor for 516/10."""
    m2c = PrecipitatePopulation(
        phase="M2C",
        length_nm=4.0,
        width_nm=0.8,
        number_density_per_m3=6.5e20,
        spacing_nm=12.3,
        coherency="coherent",
        composition_at_frac={
            "Mo": 0.50,
            "Cr": 0.125,
            "W": 0.10,
            "Fe": 0.10,
            "Ni": 0.10,
            "V": 0.025,
        },
    )
    state = MicrostructuralState(
        state="dq_tempered",
        block_width_um=1.18,
        dislocation_density_per_m2=1.12e15,
        f_austenite=0.0,
        matrix_at_frac=_matrix_at_frac_tempered(),
        precipitates=[m2c],
        label="Sun 2022 DQ + T516/10",
    )
    result = assemble_yield_strength(state)
    assert "sigma_M2C" in result.contributions_MPa
    assert result.contributions_MPa["sigma_M2C"] > 0
    assert 1000 < result.sigma_y_MPa < 2500, (
        f"DQ+T prediction {result.sigma_y_MPa:.0f} MPa is outside sanity range"
    )
    miss_MPa = result.sigma_y_MPa - SUN_2022_DQ_T516_10.YS_MPa
    print(
        f"DQ+T516/10: predicted {result.sigma_y_MPa:.0f}, "
        f"anchor {SUN_2022_DQ_T516_10.YS_MPa}, miss {miss_MPa:+.0f} MPa"
    )


def test_austenite_correction_lowers_ys() -> None:
    """Adding f_A=0.10 should lower YS (austenite is softer)."""
    state_no_a = MicrostructuralState(
        state="dq_tempered",
        block_width_um=1.18,
        dislocation_density_per_m2=1.12e15,
        f_austenite=0.0,
        matrix_at_frac=_matrix_at_frac_tempered(),
    )
    state_with_a = MicrostructuralState(
        state="dq_tempered",
        block_width_um=1.18,
        dislocation_density_per_m2=1.12e15,
        f_austenite=0.10,
        matrix_at_frac=_matrix_at_frac_tempered(),
    )
    r0 = assemble_yield_strength(state_no_a)
    r1 = assemble_yield_strength(state_with_a)
    assert r1.sigma_y_austenite_corrected_MPa < r0.sigma_y_MPa
    # No correction in the no-austenite case
    assert r0.sigma_y_austenite_corrected_MPa == r0.sigma_y_MPa


def test_summation_strategies_diverge() -> None:
    """Linear sum > Pythagorean sum (when both rho and p are non-zero)."""
    m2c = PrecipitatePopulation(
        phase="M2C",
        length_nm=4.0,
        width_nm=0.8,
        number_density_per_m3=6.5e20,
        spacing_nm=12.3,
    )
    state = MicrostructuralState(
        state="dq_tempered",
        block_width_um=1.18,
        dislocation_density_per_m2=1.12e15,
        matrix_at_frac=_matrix_at_frac_tempered(),
        precipitates=[m2c],
    )
    r_lin = assemble_yield_strength(state, strategy="linear")
    r_dp = assemble_yield_strength(state, strategy="pythagorean_dp")
    assert r_lin.sigma_y_MPa > r_dp.sigma_y_MPa


def test_orowan_subcritical_clamp_vs_raw() -> None:
    """For a sub-Burgers M2C population the Orowan formula goes negative.
    Clamp mode (default) returns 0; raw mode returns the negative value.

    Pinpoints the bug Plot 3 surfaced: m2c_population_dq_tempered at very
    low T / short t can produce r_eq << b, which the bare Ashby-Orowan
    formula treats as a negative strengthening (subtractive). Clamp mode
    is the physically sensible default.
    """
    # r=0.05 nm is sub-Burgers (b=0.25): 2 * sqrt(2/3) * 0.05 / 0.25 = 0.33,
    # ln(0.33) is negative → σ_Orowan < 0 in raw mode.
    tiny_m2c = PrecipitatePopulation(
        phase="M2C",
        radius_nm=0.05,
        number_density_per_m3=1e23,
        spacing_nm=14.0,
    )
    state = MicrostructuralState(
        state="dq_tempered",
        block_width_um=1.18,
        dislocation_density_per_m2=1.12e15,
        matrix_at_frac=_matrix_at_frac_tempered(),
        precipitates=[tiny_m2c],
    )
    r_clamp = assemble_yield_strength(state, orowan_sub_critical="clamp")
    r_raw = assemble_yield_strength(state, orowan_sub_critical="raw")

    assert r_clamp.contributions_MPa["sigma_M2C"] == 0.0, (
        "clamp mode should zero out sub-critical Orowan contribution"
    )
    assert r_raw.contributions_MPa["sigma_M2C"] < 0.0, (
        "raw mode should expose the unphysical negative value (formula limit)"
    )
    assert r_clamp.sigma_y_MPa > r_raw.sigma_y_MPa, (
        "clamp prediction should exceed raw because raw subtracts the bad value"
    )
