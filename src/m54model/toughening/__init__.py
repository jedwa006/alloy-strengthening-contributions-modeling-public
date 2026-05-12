"""TRIP-toughening submodel — stress-assisted (Patel-Cohen) + strain-induced
(Olson-Cohen) gamma → alpha' martensitic transformation.

Phase 3 v1 implements the standalone equations + Olson-Cohen fitter. K_IC at
the crack tip (which combines both regimes plus a stress-shielding model) is
deferred to Phase 3.5.
"""

from m54model.toughening.crack_tip import (
    CrackTipResult,
    K_matrix_for_target,
    SpatialCrackTipResult,
    crack_tip_KIC,
    crack_tip_KIC_spatial,
)
from m54model.toughening.williams_field import (
    StressTensor2D,
    angular_g_factor,
    hrr_radial_rescale,
    irwin_zone_boundary_m,
    williams_k_field,
)
from m54model.toughening.mcmeeking_evans import (
    A_BUDIANSKY_HUTCHINSON,
    irwin_plastic_zone_m,
    mcmeeking_evans_delta_KIC,
    steady_state_KIC_iterative,
)
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
    # Patel-Cohen 1953
    "patel_cohen_max_work",
    "patel_cohen_ms_shift",
    "patel_cohen_optimal_orientation",
    # Olson-Cohen 1975
    "olson_cohen_volume_fraction",
    "fit_olson_cohen",
    "OlsonCohenParams",
    # McMeeking-Evans 1982 transformation toughening
    "mcmeeking_evans_delta_KIC",
    "irwin_plastic_zone_m",
    "steady_state_KIC_iterative",
    "A_BUDIANSKY_HUTCHINSON",
    # High-level crack-tip integration
    "crack_tip_KIC",
    "K_matrix_for_target",
    "CrackTipResult",
    # Phase 3.6a — spatial K-field integration
    "crack_tip_KIC_spatial",
    "SpatialCrackTipResult",
    "williams_k_field",
    "StressTensor2D",
    "angular_g_factor",
    "irwin_zone_boundary_m",
    "hrr_radial_rescale",
]
