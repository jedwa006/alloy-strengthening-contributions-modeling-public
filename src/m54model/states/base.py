"""MicrostructuralState — what we know about the alloy after a processing path.

Independent of any specific predictive equation; this is just measured/inferred
microstructure that gets handed to the strengthening module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from m54model.precipitates import PrecipitatePopulation

ProcessingState = Literal[
    "mill_anneal",
    "direct_quench",  # post-quench + cryo, no temper
    "dq_tempered",
    "ausformed",  # post-AF + cryo, no temper
    "af_tempered",
]


@dataclass(frozen=True)
class MicrostructuralState:
    """Snapshot of microstructure after a processing path.

    Sizes in micrometers (block, packet, PAG) and nanometers (lath).
    Dislocation density in m^-2. f_austenite as fraction (0..1).
    """

    state: ProcessingState
    block_width_um: float
    packet_size_um: float | None = None
    pag_width_um: float | None = None
    lath_width_nm: float | None = None
    dislocation_density_per_m2: float = 0.0
    f_austenite: float = 0.0
    f_austenite_kind: Literal["retained", "reverted", "mixed", "unknown"] = "unknown"
    matrix_at_frac: dict[str, float] = field(default_factory=dict)
    """Substitutional + interstitial composition remaining in the BCC matrix
    after precipitation has consumed some elements. Used for Fleischer SS."""
    wt_pct_C_in_solution: float = 0.0
    """Carbon weight-percent remaining in the BCC matrix as supersaturated C
    (i.e. NOT bound up in carbides). Drives the as-quenched intrinsic-martensite
    strengthening term (Bain distortion + lath-boundary HP + quench stresses)
    via Speich-Leslie / Krauss correlation. Set to nominal alloy C for
    untempered states; ~0.003 wt% for fully-tempered states (Wang 2024 APT)."""
    precipitates: list[PrecipitatePopulation] = field(default_factory=list)
    """All precipitate populations (M2C, MC, ...) present in this state."""

    label: str = ""
    """Human-readable identifier (e.g., 'AF550/45 + T425/10')."""

    def precipitate(self, phase: str) -> PrecipitatePopulation | None:
        """Look up a precipitate population by phase name."""
        for p in self.precipitates:
            if p.phase == phase:
                return p
        return None
