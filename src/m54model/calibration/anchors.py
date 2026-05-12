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
