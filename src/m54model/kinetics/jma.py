"""Johnson-Mehl-Avrami (JMA) precipitation kinetics."""

import math

R_GAS = 8.314  # J/(mol·K)


def jma_volume_fraction(k: float, n: float, t_seconds: float) -> float:
    """f(t) = 1 - exp(-k * t^n).

    `k` and `n` are temperature-specific parameters fit from experimental data.
    `t_seconds` is the isothermal hold time. Returns volume fraction in [0, 1]
    (effectively the fraction of available C/M2C-formers that have precipitated).
    """
    if t_seconds <= 0:
        return 0.0
    return 1.0 - math.exp(-k * t_seconds**n)


def arrhenius_rate_scale(
    Q_kJ_per_mol: float,
    T_celsius: float,
    T_ref_celsius: float,
) -> float:
    """Return the multiplicative factor on a rate constant going from T_ref to T.

    k(T) = k(T_ref) * arrhenius_rate_scale(Q, T, T_ref)
         = k(T_ref) * exp(-Q/R * (1/T_K - 1/T_ref_K))

    Q in kJ/mol, T in Celsius. Higher Q → stronger T-dependence (faster
    growth as T rises).
    """
    T_K = T_celsius + 273.15
    T_ref_K = T_ref_celsius + 273.15
    return math.exp(-Q_kJ_per_mol * 1000.0 / R_GAS * (1.0 / T_K - 1.0 / T_ref_K))
