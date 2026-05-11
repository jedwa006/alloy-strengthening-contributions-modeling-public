"""Ashby-Orowan precipitation strengthening for non-shearable carbides."""

import math

from m54model.constants import B_NM, G_MATRIX_GPA, Convention, StrengtheningConstants
from m54model.precipitates import PrecipitatePopulation


def sigma_orowan_carbide(
    pop: PrecipitatePopulation,
    constants: StrengtheningConstants | None = None,
) -> float:
    """Ashby-Orowan looping for incoherent / large precipitates.

    Form (Wang 2024 Eq. 9):
        sigma_p = M * (0.4 G b) / [pi * sqrt(1 - nu)] * (1/L) * ln(2 r_s / b)

    where L is mean inter-particle spacing in the slip plane and
    r_s = sqrt(2/3) * r_eq is the average planar radius.

    For populations missing spacing, falls back to f_v^(1/2) Ashby form
    (Zhu Eq. 13):
        sigma_p = 0.26 * (G b / r_eq) * f_v^(1/2) * ln(r_eq / b)

    Returns MPa, or 0 if the population is empty (no f_v, no spacing).
    """
    c = constants or StrengtheningConstants.from_convention(Convention.SUN)
    r_nm = pop.equivalent_radius_nm
    if r_nm is None or r_nm <= 0:
        return 0.0
    G_MPa = G_MATRIX_GPA * 1e3
    nu = 0.30  # Poisson, BCC-Fe

    if pop.spacing_nm is not None and pop.spacing_nm > 0:
        L_nm = pop.spacing_nm
        r_s_nm = math.sqrt(2.0 / 3.0) * r_nm
        return (
            c.M_taylor
            * 0.4
            * G_MPa
            * B_NM
            / (math.pi * math.sqrt(1.0 - nu))
            * (1.0 / L_nm)
            * math.log(2.0 * r_s_nm / B_NM)
        )

    f_v = pop.volume_fraction_inferred
    if f_v is None or f_v <= 0:
        return 0.0
    return 0.26 * G_MPa * B_NM / r_nm * math.sqrt(f_v) * math.log(r_nm / B_NM)
