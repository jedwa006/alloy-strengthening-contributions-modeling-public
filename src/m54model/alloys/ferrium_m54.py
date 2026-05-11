"""Ferrium M54 nominal composition + commercial reference properties."""

from __future__ import annotations

from dataclasses import dataclass

from m54model.alloys.compositions import Composition

# Composition per Mondière 2018 Table 1 (matches Sun 2022, QuesTek QPI-M54).
FERRIUM_M54 = Composition(
    name="Ferrium M54",
    wt_pct={
        "C": 0.30,
        "Cr": 1.00,
        "Ni": 10.0,
        "Co": 7.00,
        "Mo": 2.00,
        "W": 1.30,
        "V": 0.10,
        "Ti": 0.013,
    },
)


@dataclass(frozen=True)
class CommercialReference:
    """Anchor properties for a known M54 condition (validation targets)."""

    label: str
    source: str
    YS_MPa: float
    UTS_MPa: float
    EL_pct: float
    HV: float | None = None
    KIC_MPa_m_half: float | None = None


# Calibration anchors — see MODEL_PLAN.md §6.
SUN_2022_DQ = CommercialReference(
    label="DQ (post-cryo, no temper)",
    source="sun_main",
    YS_MPa=1420,
    UTS_MPa=1916,
    EL_pct=14.9,
    HV=560,
)

SUN_2022_DQ_T516_10 = CommercialReference(
    label="DQ + T516/10 (commercial)",
    source="sun_main",
    YS_MPa=1762,
    UTS_MPa=2050,
    EL_pct=14.9,
    HV=618,
    KIC_MPa_m_half=126,  # 126 from QuesTek/NAVAIR; Mondière reports 110
)

SUN_2022_AF550_45 = CommercialReference(
    label="AF550/45 (post-cryo, no temper)",
    source="sun_main",
    YS_MPa=1830,
    UTS_MPa=2291,
    EL_pct=14.4,
    HV=659,
)

SUN_2022_AF550_45_T425_10 = CommercialReference(
    label="AF550/45 + T425/10 (enhanced)",
    source="sun_main",
    YS_MPa=1726,
    UTS_MPa=2222,
    EL_pct=15.5,
    HV=629,
)

WANG_2024_T520_8 = CommercialReference(
    label="DQ + T520/8 (Wang peak)",
    source="zhu41_Wang_2024",
    YS_MPa=1747,
    UTS_MPa=2037,
    EL_pct=14.0,  # EL not reported, ~typical
)
