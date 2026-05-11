"""Bailey-Hirsch dislocation strengthening."""

import math

from m54model.constants import B_NM, G_MATRIX_GPA, Convention, StrengtheningConstants


def sigma_dislocation(
    rho_per_m2: float,
    constants: StrengtheningConstants | None = None,
) -> float:
    """sigma_rho = alpha * M * G * b * sqrt(rho).

    Defaults to Sun's alpha = 0.38 (per Bhadeshia-Honeycombe). Wang/Zhu use 0.25.
    Returns MPa.
    """
    c = constants or StrengtheningConstants.from_convention(Convention.SUN)
    if rho_per_m2 < 0:
        raise ValueError(f"dislocation density must be >=0, got {rho_per_m2}")
    G_MPa = G_MATRIX_GPA * 1e3
    b_m = B_NM * 1e-9
    return c.alpha_BH * c.M_taylor * G_MPa * b_m * math.sqrt(rho_per_m2)
