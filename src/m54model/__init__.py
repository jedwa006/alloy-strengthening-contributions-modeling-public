"""m54model — Strengthening + toughening model for Ferrium M54.

Phase 1 scaffold: alloy/state/precipitate dataclasses + strengthening contributions.
"""

from m54model.alloys import FERRIUM_M54, Composition
from m54model.constants import (
    Convention,
    StrengtheningConstants,
    SummationStrategy,
)
from m54model.precipitates import PrecipitatePopulation
from m54model.states import MicrostructuralState
from m54model.strengthening import StrengtheningResult, assemble_yield_strength

__version__ = "0.1.0"

__all__ = [
    "Composition",
    "FERRIUM_M54",
    "MicrostructuralState",
    "PrecipitatePopulation",
    "StrengtheningResult",
    "StrengtheningConstants",
    "Convention",
    "SummationStrategy",
    "assemble_yield_strength",
    "__version__",
]
