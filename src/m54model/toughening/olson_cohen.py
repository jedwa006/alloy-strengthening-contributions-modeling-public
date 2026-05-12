"""Olson & Cohen 1975 — kinetics of strain-induced martensitic nucleation.

Master equation (Eq. 7):

    f_α′ = 1 − exp{−β · [1 − exp(−α · ε)]^n}

with:
- ε    = plastic strain in austenite
- α    = shear-band-formation rate parameter (depends on stacking-fault energy
         and strain rate; decreases with increasing T)
- β    = probability that a shear-band intersection forms a martensitic embryo
         (sigmoidal in T centered around M_d^σ; saturates near 2.0 at low T,
         decays to ~0 at high T)
- n    = empirical exponent (≈ 4.5 for Angel's 304 SS data per Olson-Cohen Fig. 1)

Validation: against Angel 1954 304 SS at T ∈ {-188, -70, -30, 0, 22} °C with
Olson-Cohen Fig. 2 (a, b) parameters: α(-188°C) = 12.9, β(-188°C) = 2.0,
α(22°C) = 3.55, β(22°C) ≈ 0.3. Reproduces the sigmoidal transformation curves
to within plot-reading precision.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class OlsonCohenParams:
    """Olson-Cohen fit parameters at a specific temperature."""

    alpha: float
    """Shear-band formation rate (dimensionless)."""

    beta: float
    """Probability of intersection → embryo (dimensionless)."""

    n: float = 4.5
    """Empirical exponent. Default 4.5 from Angel 1954 / 304 SS fit."""

    T_celsius: float | None = None
    """Temperature at which alpha, beta were fit (informational)."""


def olson_cohen_volume_fraction(
    epsilon: float,
    params: OlsonCohenParams,
) -> float:
    """f_α′(ε) = 1 − exp{−β · [1 − exp(−α · ε)]^n}.

    Returns volume fraction of martensite in [0, 1].
    """
    if epsilon < 0:
        raise ValueError(f"plastic strain must be >= 0, got {epsilon}")
    if epsilon == 0:
        return 0.0
    inner = 1.0 - math.exp(-params.alpha * epsilon)
    return 1.0 - math.exp(-params.beta * inner**params.n)


def fit_olson_cohen(
    epsilon: Sequence[float],
    f_alpha_prime: Sequence[float],
    *,
    n: float = 4.5,
    T_celsius: float | None = None,
    initial_alpha: float = 4.0,
    initial_beta: float = 1.0,
) -> OlsonCohenParams:
    """Fit (α, β) from measured (ε, f_α′) pairs at a single temperature.

    Uses scipy.optimize.least_squares with bounds [0.01, 50] on both parameters.
    `n` is fixed (default 4.5 per Olson-Cohen 304 SS); fit it separately if a
    different alloy/regime suggests a different exponent.

    Returns an OlsonCohenParams. If the fit fails (bad data / divergence),
    raises a RuntimeError.
    """
    try:
        from scipy.optimize import least_squares
    except ImportError as e:
        raise ImportError("fit_olson_cohen requires scipy") from e

    eps = list(epsilon)
    fa = list(f_alpha_prime)
    if len(eps) != len(fa):
        raise ValueError("epsilon and f_alpha_prime must be same length")
    if len(eps) < 3:
        raise ValueError("need at least 3 points to fit two parameters")

    def residuals(params_array: list[float]) -> list[float]:
        a, b = params_array
        guess = OlsonCohenParams(alpha=a, beta=b, n=n)
        return [
            olson_cohen_volume_fraction(e, guess) - m for e, m in zip(eps, fa, strict=True)
        ]

    result = least_squares(
        residuals,
        x0=[initial_alpha, initial_beta],
        bounds=([0.01, 0.01], [50.0, 50.0]),
    )
    if not result.success:
        raise RuntimeError(f"olson-cohen fit failed: {result.message}")
    a_fit, b_fit = result.x
    return OlsonCohenParams(alpha=float(a_fit), beta=float(b_fit), n=n, T_celsius=T_celsius)
