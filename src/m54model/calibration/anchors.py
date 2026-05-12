"""Calibration anchors — MicrostructuralState factories matching published M54 data.

Each factory returns a state that exactly mirrors the microstructure measurements
from the source paper, so the model's prediction can be compared against that
paper's reported YS.
"""

from __future__ import annotations

from m54model.alloys import FERRIUM_M54
from m54model.kinetics import m2c_population_af_tempered
from m54model.precipitates import PrecipitatePopulation
from m54model.states import MicrostructuralState


def _matrix_dq() -> dict[str, float]:
    """At-fraction matrix for the DQ state — all alloying still in solid solution."""
    return FERRIUM_M54.at_frac()


def _matrix_tempered(consumed: dict[str, float] | None = None) -> dict[str, float]:
    """At-fraction matrix after carbide precipitation has consumed certain elements.

    Default consumption fractions reflect Wang 2024 / Mondière APT measurements
    of M2C composition: M2C is dominantly Mo (50 at%) with Cr/W/V/Fe/Ni shares.
    Ti is consumed by undissolved MC pinners (most of the 0.013 wt% goes there).
    """
    consumed = consumed or {
        "Mo": 0.80,
        "Cr": 0.80,
        "W": 0.80,
        "V": 0.80,
        "Ti": 0.95,
        "C": 0.99,
    }
    af = FERRIUM_M54.at_frac()
    matrix = {k: v * (1.0 - consumed.get(k, 0.0)) for k, v in af.items()}
    total = sum(matrix.values())
    return {k: v / total for k, v in matrix.items()}


def sun_2022_dq() -> MicrostructuralState:
    """Sun 2022 direct-quench (no temper). Anchor: YS = 1420 MPa."""
    return MicrostructuralState(
        state="direct_quench",
        block_width_um=1.18,
        packet_size_um=13.1,
        pag_width_um=100.0,
        lath_width_nm=135.0,  # midpoint of 70-200 nm range
        dislocation_density_per_m2=2.08e15,
        f_austenite=0.0,
        matrix_at_frac=_matrix_dq(),
        wt_pct_C_in_solution=0.30,  # nominal alloy C, all in supersaturation
        precipitates=[],
        label="Sun 2022 DQ",
    )


def sun_2022_dq_t516_10() -> MicrostructuralState:
    """Sun 2022 direct-quench + 516 °C / 10 h temper (commercial spec).
    Anchor: YS = 1762 MPa, UTS = 2050 MPa.

    Uses Wang 2024's measured M2C population at 520 °C / 8 h (peak hardening,
    closest available datapoint to commercial 516/10 spec). Mondière 2018
    reports M2C at 516/10 as 9.6 nm × 1.2 nm rod but does not give number
    density or volume fraction — Wang's data is more complete.
    """
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
    return MicrostructuralState(
        state="dq_tempered",
        block_width_um=1.18,
        packet_size_um=13.1,
        pag_width_um=100.0,
        lath_width_nm=135.0,
        dislocation_density_per_m2=1.12e15,
        f_austenite=0.0,
        matrix_at_frac=_matrix_tempered(),
        wt_pct_C_in_solution=0.003,  # Wang 2024 APT: 99% of C consumed by M2C
        precipitates=[m2c],
        label="Sun 2022 DQ + T516/10",
    )


def sun_2022_af550_45() -> MicrostructuralState:
    """Sun 2022 AF550/45 — ausformed at 550 °C with 45 % reduction, post-cryo.
    Anchor: YS = 1830 MPa.

    No tempering, no carbide precipitation (just the as-ausformed structure).
    """
    return MicrostructuralState(
        state="ausformed",
        block_width_um=0.48,
        packet_size_um=6.7,
        pag_width_um=47.0,
        lath_width_nm=135.0,  # similar to DQ; ausforming refines block more than lath
        dislocation_density_per_m2=7.81e15,
        f_austenite=0.0,
        matrix_at_frac=_matrix_dq(),
        wt_pct_C_in_solution=0.30,  # ausforming doesn't consume C (no temper yet)
        precipitates=[],
        label="Sun 2022 AF550/45",
    )


def m54_af_t516_10_cw(
    cw_pct: float,
    *,
    location: str = "surface",
) -> MicrostructuralState:
    """**Phase 3.6d** — M54 AF + T516/10 + N % cold-rolling state factory.

    Builds on `m54_af550_45_t516_10()` (the cw/cr starting state) and swaps
    in the user's measured cw/cr inputs:

    - **Dislocation density**: from `USER_M54_GND_DENSITY` BCC median ρ at
      this CR. NOTE this is GND only; total ρ = ρ<sub>GND</sub> + ρ<sub>SSD</sub>
      is likely higher by ~2× to ~10× depending on CR. So predicted σ<sub>ρ</sub>
      from this factory is a LOWER BOUND on the dislocation contribution.
    - **Reverted austenite fraction**: from `USER_M54_CW_AUSTENITE_SURFACE`
      (or `_CORE` if `location='core'`).
    - **Block width**: held at 0.48 µm (Sun AF baseline) — cold rolling
      fragments at the sub-block scale, not the block scale. The
      sub-block (cell) refinement that ASTAR sees is not captured by
      block-based Hall-Petch; this is a known under-prediction at high
      CR (Phase 3.6d gap analysis).
    - **M2C population**: held at the 516 °C / 10 h post-temper state —
      cold rolling at room temp (T_max ≈ 80 °C) is too cold for further
      M2C precipitation/coarsening on the rolling timescale.
    - **Matrix at-fraction + C in solid solution**: held at tempered values.

    `cw_pct` must be in {0, 20, 40, 60} (the user's ASTAR/GND
    measurement points). Use 0 to recover `m54_af550_45_t516_10()`
    directly with the location-specific f_A.
    """
    from m54model.calibration.user_microstructure_data import gnd_for_cr
    from m54model.calibration.user_trip_data import (
        USER_M54_CW_AUSTENITE_CORE,
        USER_M54_CW_AUSTENITE_SURFACE,
    )

    if location not in ("surface", "core"):
        raise ValueError(f"location must be 'surface' or 'core', got {location!r}")

    cw_int = int(cw_pct)
    austenite_dataset = (
        USER_M54_CW_AUSTENITE_SURFACE if location == "surface" else USER_M54_CW_AUSTENITE_CORE
    )
    f_A_pt = next((p for p in austenite_dataset if p.cw_pct == cw_int), None)
    if f_A_pt is None:
        raise KeyError(f"no f_A data at cw_pct={cw_pct}, location={location!r}")

    rho_BCC_GND = gnd_for_cr(cw_int, location_phase="BCC_median")

    m2c = m2c_population_af_tempered(T_celsius=516.0, t_hours=10.0)
    return MicrostructuralState(
        state="af_tempered_cw",
        block_width_um=0.48,
        packet_size_um=6.7,
        pag_width_um=47.0,
        lath_width_nm=135.0,
        dislocation_density_per_m2=rho_BCC_GND,  # GND lower-bound; see docstring
        f_austenite=f_A_pt.f_austenite,
        f_austenite_kind="reverted",
        matrix_at_frac=_matrix_tempered(),
        wt_pct_C_in_solution=0.003,
        precipitates=[m2c],
        label=f"M54 AF + T516/10 + {cw_int} % CR ({location})",
    )


def predict_cw_cr_sweep(
    *,
    location: str = "core",
    cw_pcts: tuple[int, ...] = (0, 20, 40, 60),
    apply_strain_rate_correction: bool = True,
) -> list[dict[str, float | str | None]]:
    """Phase 3.6d sweep: predict σ_y at each CR condition and compare to
    measured tensile (where available).

    Returns list of dicts with keys:
        cw_pct, sigma_y_qs_MPa, sigma_y_user_rate_MPa, sigma_y_meas_MPa,
        sigma_y_meas_std_MPa, miss_pct, f_austenite, rho_GND_per_m2.

    `location='core'` is the right default for cross-comparing to a bulk
    tensile bar (the surface f_A measurement is too localized to
    represent bulk material). Use `location='surface'` to see the
    extreme-end prediction at the rolling face.
    """
    from m54model.calibration.strain_rate import (
        EPS_DOT_SUN_2022_S_INV,
        EPS_DOT_USER_TENSILE_S_INV,
        strain_rate_correction,
    )
    from m54model.calibration.user_mechanical_data import tensile_for_cr
    from m54model.strengthening import assemble_yield_strength

    factor = (
        strain_rate_correction(
            EPS_DOT_USER_TENSILE_S_INV, EPS_DOT_SUN_2022_S_INV, m=0.01
        )
        if apply_strain_rate_correction
        else 1.0
    )

    rows: list[dict[str, float | str | None]] = []
    for cw in cw_pcts:
        state = m54_af_t516_10_cw(float(cw), location=location)
        res = assemble_yield_strength(state)
        sigma_qs = res.sigma_y_austenite_corrected_MPa
        sigma_user = sigma_qs * factor
        try:
            m = tensile_for_cr(float(cw))
            meas = m.sigma_y_MPa
            meas_std = m.sigma_y_std_MPa
            miss = (sigma_user - meas) / meas * 100.0
        except KeyError:
            meas = None
            meas_std = None
            miss = None
        rows.append(
            {
                "cw_pct": float(cw),
                "location": location,
                "sigma_y_qs_MPa": round(sigma_qs, 1),
                "sigma_y_user_rate_MPa": round(sigma_user, 1),
                "sigma_y_meas_MPa": meas,
                "sigma_y_meas_std_MPa": meas_std,
                "miss_pct": round(miss, 1) if miss is not None else None,
                "f_austenite": state.f_austenite,
                "rho_GND_per_m2": state.dislocation_density_per_m2,
            }
        )
    return rows


def m54_af550_45_t516_10() -> MicrostructuralState:
    """M54 AF550/45 + commercial 516 °C / 10 h temper — the **user's cw/cr baseline**.

    NOTE: This is NOT a Sun 2022 anchor (Sun used T425/10). It's the actual
    starting state for the user's cold-rolling series.

    **Prior history:** the strip was cross-rolled to achieve the ausformed form
    (or to reach the target geometry post-ausforming) BEFORE the 516 °C / 10 h
    temper. Cross-rolling means multi-axial deformation in two perpendicular
    directions before tempering, not the simple uniaxial AF550/45 of Sun 2022.
    Microstructural impact of the cross-rolling is largely reset by the long
    high-T temper (M2C precipitation, dislocation recovery), so we use Sun's
    AF550/45 block + Wang's tempering-invariant block-size assumption as a
    reasonable proxy. The 0 % CR ASTAR microstructure (Table 3 of user data)
    confirms this is a fine-block-fine-lath structure consistent with AF.

    Microstructural inputs:
    - Block width 0.48 µm: from Sun's AF state; tempering doesn't refine block
      (Wang 2024 confirms block invariant in DQ across 2-10 h tempering).
    - Dislocation density 1.6 × 10¹⁵ m⁻²: directly from the user's ASTAR-PED
      measurement at 0 % CR baseline (Table 4). Slightly higher than Sun's
      AF+T425/10 (1.18 × 10¹⁵), consistent with the longer/hotter 516 °C / 10 h
      temper retaining slightly more dislocation density via M2C-pinning.
    - M2C: predicted via `m2c_population_af_tempered(516, 10)` — past peak,
      LSW-coarsened, V_f at M54-stoichiometry-scaled saturation.
    - Reverted austenite: 0.013 (= 1.3 % surface) per user's ASTAR phase
      fraction at 0 % CR. f_austenite_kind set to 'reverted' since cryo
      removes most retained γ and 516 °C / 10 h is long enough for lath-
      boundary Ni-enriched reversion.
    - C in solid solution: ~0.003 wt% (M2C precipitation depletes matrix C).

    No published YS anchor — anchor will come from the user's measurements
    when available (tensile-tested at 0 % CR baseline). NB: those tests are
    at strain rate 10⁻¹ s⁻¹ vs Sun's 5×10⁻⁴ s⁻¹ (200× faster). For tempered
    M54 with strain-rate sensitivity m ≈ 0.01, expect measured σ_y to be
    ~5 % above Sun-equivalent quasi-static value. The model predicts
    quasi-static; remember to multiply by ~1.05 when comparing to user
    tensile data.
    """
    m2c = m2c_population_af_tempered(T_celsius=516.0, t_hours=10.0)
    return MicrostructuralState(
        state="af_tempered",
        block_width_um=0.48,
        packet_size_um=6.7,
        pag_width_um=47.0,
        lath_width_nm=135.0,
        dislocation_density_per_m2=1.6e15,
        f_austenite=0.013,
        f_austenite_kind="reverted",
        matrix_at_frac=_matrix_tempered(),
        wt_pct_C_in_solution=0.003,
        precipitates=[m2c],
        label="M54 AF550/45 + T516/10 (user's cw/cr baseline)",
    )


def sun_2022_af550_45_t425_10() -> MicrostructuralState:
    """Sun 2022 enhanced commercial route: AF550/45 then 425 °C / 10 h temper.
    Anchor: YS = 1726 MPa.

    Microstructure inputs from Sun 2022 measurements (block, dislocation
    density, lath). M2C population is **predicted** from Cho 2015 → M54
    transferred kinetics via `m2c_population_af_tempered(425, 10)` —
    Sun 2022 did not characterize M2C in this state, so this is the first
    quantitative estimate.
    """
    m2c = m2c_population_af_tempered(T_celsius=425.0, t_hours=10.0)
    return MicrostructuralState(
        state="af_tempered",
        block_width_um=0.48,  # ausforming refines from 1.18 to 0.48 µm
        packet_size_um=6.7,
        pag_width_um=47.0,
        lath_width_nm=135.0,
        dislocation_density_per_m2=1.18e15,  # post-temper recovered to ~DQ+T levels
        f_austenite=0.0,
        matrix_at_frac=_matrix_tempered(),
        wt_pct_C_in_solution=0.003,  # tempered — C consumed by M2C
        precipitates=[m2c],
        label="Sun 2022 AF550/45 + T425/10",
    )
