"""As-quenched intrinsic-martensite strengthening (Bain + lath + supersaturation).

The simple HP(block) + Bailey-Hirsch + Fleischer decomposition under-predicts
yield strength in untempered martensitic states (DQ, AF) by 30-40 % because it
misses three coupled physical sources:

1. **Tetragonality of C-supersaturated BCT martensite** — Bain distortion
   creates a large internal strain that resists dislocation motion. Captured
   empirically by Speich-Leslie 1972 for plain-C steels.
2. **Lath-boundary strengthening** — block size badly under-counts effective
   boundary area in untempered laths (laths 70-200 nm vs blocks 1180 nm).
3. **Quench-induced internal stresses** — relax during tempering, so this
   contribution evaporates in tempered states.

We bundle all three into a single empirical term keyed on wt% C in solid
solution, calibrated against Sun 2022 DQ. After tempering when C drops from
~0.30 to ~0.003 wt%, the contribution shrinks below noise and we treat as
zero.
"""

import math

from m54model.constants import K_INTRINSIC_MARTENSITE_MPA_PER_SQRT_WTPCT
from m54model.states import MicrostructuralState

# States where the as-quenched intrinsic contribution survives.
_UNTEMPERED_STATES = frozenset(("direct_quench", "ausformed"))


def sigma_intrinsic_martensite(
    state: MicrostructuralState,
    K: float = K_INTRINSIC_MARTENSITE_MPA_PER_SQRT_WTPCT,
) -> float:
    """sigma_intrinsic = K * sqrt(wt% C in solid solution).

    Returns 0 for tempered states (the contribution is absorbed into the
    tempered Fleischer-C term and the residual is below noise).

    Returns MPa.
    """
    if state.state not in _UNTEMPERED_STATES:
        return 0.0
    wt_pct_C = state.wt_pct_C_in_solution
    if wt_pct_C <= 0:
        return 0.0
    return K * math.sqrt(wt_pct_C)
