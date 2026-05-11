"""Calibration anchors — MicrostructuralState factories matching published M54 data.

Each factory returns a state that exactly mirrors the microstructure measurements
from the source paper, so the model's prediction can be compared against that
paper's reported YS.
"""

from __future__ import annotations

from m54model.alloys import FERRIUM_M54
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
        precipitates=[],
        label="Sun 2022 AF550/45",
    )


# AF550/45 + T425/10 is deferred to Phase 2 — needs the Cho 2015 → M54 kinetics
# transfer to estimate the M2C population at 425 °C/10 h after ausforming.
