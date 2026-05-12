"""User's measured austenite-content data from cold-rolling experiments.

These are the calibration target for the Olson-Cohen (α, β) parameters of
M54 reverted austenite. Replace the PLACEHOLDER values with your actual
measurements, then run `m54_olson_cohen_fit_from_user_data()` to get the
fitted parameters.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from m54model.toughening import OlsonCohenParams, fit_olson_cohen


@dataclass(frozen=True)
class CWAustenitePoint:
    """One (cold-work %, austenite vol fraction) measurement at a given starting state."""

    cw_pct: float
    """Cumulative cold-rolling reduction in %. 0% = baseline, 60% = 60 % thickness reduction."""

    f_austenite: float
    """Measured austenite volume fraction (XRD or similar). 0..1."""


# PLACEHOLDER VALUES — replace with the user's actual measurements.
# Test data here matches a typical TRIP-steel response just so the fitter runs;
# the fitted params will be meaningless until real values are dropped in.
USER_CW_AUSTENITE_DATA_PLACEHOLDER: list[CWAustenitePoint] = [
    CWAustenitePoint(cw_pct=0.0, f_austenite=0.04),  # baseline post-temper austenite
    CWAustenitePoint(cw_pct=20.0, f_austenite=0.02),
    CWAustenitePoint(cw_pct=40.0, f_austenite=0.01),
    CWAustenitePoint(cw_pct=60.0, f_austenite=0.005),
]


def cw_pct_to_true_strain(cw_pct: float) -> float:
    """Convert cumulative cold-rolling reduction (%) to von Mises equivalent
    true strain.

    For uniaxial cold rolling: ε = -ln(1 - r), where r = cw_pct/100.
    For 60% reduction: ε ≈ 0.916.
    """
    if cw_pct < 0 or cw_pct >= 100:
        raise ValueError(f"cw_pct must be in [0, 100), got {cw_pct}")
    r = cw_pct / 100.0
    return -math.log(1.0 - r)


def m54_olson_cohen_fit_from_user_data(
    data: Sequence[CWAustenitePoint] | None = None,
    *,
    n: float = 4.5,
    T_celsius: float = 22.0,
) -> OlsonCohenParams:
    """Convert (cw%, austenite vf) measurements to (ε, f_α′) and fit Olson-Cohen.

    Steps:
    1. cw_pct → true strain ε via -ln(1 - r).
    2. f_α′(ε) = f_A(baseline) - f_A(ε)  — assumes austenite-to-martensite
       conversion is the only mechanism reducing f_A under deformation.
    3. Drop the baseline point (ε=0, f_α′=0) and fit α, β.

    Default n=4.5 (Olson-Cohen 304 SS); change if data suggests differently.
    """
    pts = list(data or USER_CW_AUSTENITE_DATA_PLACEHOLDER)
    if not pts:
        raise ValueError("no data points")
    pts = sorted(pts, key=lambda p: p.cw_pct)
    baseline = pts[0]
    if baseline.cw_pct != 0:
        raise ValueError(f"first point must be cw=0% baseline, got cw={baseline.cw_pct}")

    eps: list[float] = []
    f_ap: list[float] = []
    for p in pts[1:]:
        eps.append(cw_pct_to_true_strain(p.cw_pct))
        # Normalise: how much of the AVAILABLE austenite has converted?
        # f_α′ as a fraction of total parent austenite, so we divide by f_A(0).
        if baseline.f_austenite <= 0:
            raise ValueError("baseline f_austenite must be > 0 to normalise")
        delta = (baseline.f_austenite - p.f_austenite) / baseline.f_austenite
        f_ap.append(max(0.0, min(1.0, delta)))
    return fit_olson_cohen(eps, f_ap, n=n, T_celsius=T_celsius)
