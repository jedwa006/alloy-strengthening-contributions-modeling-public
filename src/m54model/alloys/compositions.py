"""Alloy composition with wt% / at% conversion."""

from __future__ import annotations

from dataclasses import dataclass, field

# Atomic weights (g/mol). Standard values, sufficient for our composition arithmetic.
ATOMIC_WEIGHT_G_PER_MOL: dict[str, float] = {
    "Fe": 55.845,
    "C": 12.011,
    "Co": 58.933,
    "Ni": 58.693,
    "Cr": 51.996,
    "Mo": 95.95,
    "W": 183.84,
    "V": 50.942,
    "Al": 26.982,
    "Ti": 47.867,
    "Mn": 54.938,
    "Si": 28.085,
    "Nb": 92.906,
    "Cu": 63.546,
    "N": 14.007,
}


@dataclass(frozen=True)
class Composition:
    """Alloy composition stored as wt% with on-demand at% conversion.

    Iron is balance — supply only the alloying elements as wt%; Fe is computed.
    """

    name: str
    wt_pct: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        unknown = set(self.wt_pct) - set(ATOMIC_WEIGHT_G_PER_MOL)
        if unknown:
            raise ValueError(f"unknown elements in composition: {sorted(unknown)}")
        non_fe_total = sum(v for k, v in self.wt_pct.items() if k != "Fe")
        if non_fe_total > 100.0:
            raise ValueError(f"non-Fe wt% sum {non_fe_total} exceeds 100")

    @property
    def wt_pct_full(self) -> dict[str, float]:
        """wt% of every element with Fe as balance."""
        non_fe_total = sum(v for k, v in self.wt_pct.items() if k != "Fe")
        full = dict(self.wt_pct)
        full["Fe"] = 100.0 - non_fe_total
        return full

    def at_frac(self) -> dict[str, float]:
        """Atomic fractions (sum = 1)."""
        wt_full = self.wt_pct_full
        moles = {k: v / ATOMIC_WEIGHT_G_PER_MOL[k] for k, v in wt_full.items()}
        total = sum(moles.values())
        return {k: m / total for k, m in moles.items()}

    def at_pct(self) -> dict[str, float]:
        """Atomic percentages (sum = 100)."""
        return {k: v * 100.0 for k, v in self.at_frac().items()}
