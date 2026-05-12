"""Lifshitz-Slyozov-Wagner (LSW) coarsening — r grows as t^(1/3) past peak."""


def lsw_radius(
    r0_nm: float,
    K_LSW_m3_per_s: float,
    t_seconds: float,
) -> float:
    """LSW coarsening law: r^3(t) = r0^3 + K_LSW * t.

    K_LSW depends on diffusivity, surface energy, equilibrium concentration —
    typical for M2C in steel: 1e-31 to 1e-29 m^3/s. Returns r in nm.
    """
    if t_seconds <= 0:
        return r0_nm
    r0_m = r0_nm * 1e-9
    r_m = (r0_m**3 + K_LSW_m3_per_s * t_seconds) ** (1.0 / 3.0)
    return r_m * 1e9
