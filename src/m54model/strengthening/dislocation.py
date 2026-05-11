"""Bailey-Hirsch / Taylor-Orowan dislocation strengthening."""

import math

from m54model.constants import B_NM, G_MATRIX_GPA, Convention, StrengtheningConstants


def sigma_dislocation(
    rho_per_m2: float,
    constants: StrengtheningConstants | None = None,
) -> float:
    """Bailey-Hirsch / Taylor-Orowan dislocation strengthening.

    Formula:  sigma_rho = alpha_eff * G * b * sqrt(rho)

    `alpha_eff` is the **Schmid-averaged effective prefactor** — the Taylor
    factor M is already absorbed into it. Conventions differ on how this is
    presented in papers:

    - **Sun 2022** (per Bhadeshia & Honeycombe Steels Ch. 14, Sun ref [23]):
      Writes sigma_rho = alpha * G * b * sqrt(rho) with **alpha = 0.38**. M is
      implicit. (DEFAULT here.)
    - **Wang 2024 / Zhu 2025**: Writes sigma_rho = alpha * M * G * b * sqrt(rho)
      with alpha = 0.25 and M = 2.5 — effective prefactor 0.625. Our Convention.WANG
      bakes this into alpha_eff = 0.625.

    Returns MPa.
    """
    c = constants or StrengtheningConstants.from_convention(Convention.SUN)
    if rho_per_m2 < 0:
        raise ValueError(f"dislocation density must be >=0, got {rho_per_m2}")
    G_MPa = G_MATRIX_GPA * 1e3
    b_m = B_NM * 1e-9
    return c.alpha_BH * G_MPa * b_m * math.sqrt(rho_per_m2)
