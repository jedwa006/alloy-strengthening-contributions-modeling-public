"""TRIP-toughening submodel — stress-assisted (Patel-Cohen) + strain-induced
(Olson-Cohen) gamma → alpha' martensitic transformation.

Phase 3 v1 implements the standalone equations + Olson-Cohen fitter. K_IC at
the crack tip (which combines both regimes plus a stress-shielding model) is
deferred to Phase 3.5.
"""

from m54model.toughening.olson_cohen import (
    OlsonCohenParams,
    fit_olson_cohen,
    olson_cohen_volume_fraction,
)
from m54model.toughening.patel_cohen import (
    patel_cohen_max_work,
    patel_cohen_ms_shift,
    patel_cohen_optimal_orientation,
)

__all__ = [
    "patel_cohen_max_work",
    "patel_cohen_ms_shift",
    "patel_cohen_optimal_orientation",
    "olson_cohen_volume_fraction",
    "fit_olson_cohen",
    "OlsonCohenParams",
]
