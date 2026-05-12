"""User's measured austenite-content data from cold-rolling experiments.

These are the calibration target for the Olson-Cohen (α, β) parameters of
M54 reverted austenite — though see the **non-monotonic finding** below.

Data source: ASTAR precession diffraction mapping, FCC γ phase fractions
by CR (cold-rolling) condition and through-thickness cross-section position.
Surface RA (%) values are mean ± std of multiple ASTAR maps; core RA (%)
are median values along the ND-midplane (assumed homogeneous along that
plane).

CR % | Surface RA (%) | Core RA (%) | Trend
-----|----------------|-------------|--------------------------------
  0  | 1.3 ± 0.9      | 2.6         | Trace; as-quenched baseline
 20  | 0.5 ± 0.3      | 1.3         | Heterogeneous onset
 40  | 26.4 ± 9       | 9.9         | Peak cellular network; 4:1 surface:core
 60  | 17.6 ± 8       | 12.6        | Partial retransformation


===============================================================================
**KEY FINDING — non-monotonic f_A(ε) breaks classical Olson-Cohen.**
===============================================================================

Classical Olson-Cohen (1975) predicts f_α′(ε) is monotonically increasing
in plastic strain → therefore f_A(ε) = f_A(0) − f_α′(ε) is monotonically
DECREASING. Standard 304 SS / TRIP-steel behavior.

The user's M54 data shows the opposite story between 20 % and 40 % CR:
austenite **goes UP** by ~25 percentage points (surface) / ~9 (core) before
partially retransforming at 60 % CR.

Pattern: 0 → 20 % CR matches classical TRIP (austenite drops). Above 20 %,
some mechanism CREATES or STABILIZES austenite — possibly:
  - Adiabatic-heating-induced reverse transformation (γ ← α′) near the
    rolling surface where shear strain rate peaks
  - Mechanical austenite formation in the "cellular network" the user notes
    at 40 % CR (deformation-induced shear bands acting as nucleation sites
    for reverse transformation)
  - Strain-partitioning that stabilizes pre-existing austenite films at the
    expense of bulk martensite plasticity

Implication: Olson-Cohen alone is INSUFFICIENT for M54 reverted austenite
under cold rolling. We need either (a) a competing austenite-formation
term, (b) a cw-CR-specific kinetic model decoupled from monotonic plastic
strain, or (c) treat the 0→20 % CR segment as the only "classical TRIP"
regime and fit OC to that subset alone.

For now: data is recorded here verbatim; OC fitting on the 0→20 % subset
is the only well-defined operation. Higher-CR points are kept for plotting
and downstream modeling extensions.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from m54model.toughening import OlsonCohenParams, fit_olson_cohen


@dataclass(frozen=True)
class CWAustenitePoint:
    """One (cold-work %, austenite vol fraction) measurement."""

    cw_pct: float
    """Cumulative cold-rolling reduction in %. 0% = baseline, 60% = 60 % thickness reduction."""

    f_austenite: float
    """Measured austenite volume fraction (XRD or similar). 0..1."""

    f_austenite_std: float | None = None
    """One-sigma standard deviation, if reported. None if median only."""

    location: str = "surface"
    """Cross-section location: 'surface' or 'core' (or 'bulk-XRD')."""


# ---------- Real M54 data — ASTAR precession diffraction --------------------------------

USER_M54_CW_AUSTENITE_SURFACE: list[CWAustenitePoint] = [
    CWAustenitePoint(cw_pct=0.0, f_austenite=0.013, f_austenite_std=0.009, location="surface"),
    CWAustenitePoint(cw_pct=20.0, f_austenite=0.005, f_austenite_std=0.003, location="surface"),
    CWAustenitePoint(cw_pct=40.0, f_austenite=0.264, f_austenite_std=0.090, location="surface"),
    CWAustenitePoint(cw_pct=60.0, f_austenite=0.176, f_austenite_std=0.080, location="surface"),
]

USER_M54_CW_AUSTENITE_CORE: list[CWAustenitePoint] = [
    CWAustenitePoint(cw_pct=0.0, f_austenite=0.026, location="core"),
    CWAustenitePoint(cw_pct=20.0, f_austenite=0.013, location="core"),
    CWAustenitePoint(cw_pct=40.0, f_austenite=0.099, location="core"),
    CWAustenitePoint(cw_pct=60.0, f_austenite=0.126, location="core"),
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


def is_monotonic_decreasing(data: Sequence[CWAustenitePoint]) -> bool:
    """Quick sanity check: does f_A monotonically decrease with cw_pct?

    Classical Olson-Cohen TRIP requires this. For M54 the answer is NO —
    f_A jumps up at 40 % CR. Use this to pick a fittable subset.
    """
    pts = sorted(data, key=lambda p: p.cw_pct)
    return all(
        b.f_austenite <= a.f_austenite + 1e-6 for a, b in zip(pts, pts[1:], strict=True)
    )


def m54_olson_cohen_fit_from_user_data(
    data: Sequence[CWAustenitePoint] | None = None,
    *,
    n: float = 4.5,
    T_celsius: float = 22.0,
    fit_only_monotonic_prefix: bool = True,
) -> OlsonCohenParams:
    """Convert (cw%, austenite vf) measurements to (ε, f_α′) and fit Olson-Cohen.

    Steps:
    1. cw_pct → true strain ε via -ln(1 - r).
    2. f_α′(ε) = (f_A(0) - f_A(ε)) / f_A(0) — fraction of available austenite
       that has converted.
    3. Drop the baseline point (ε=0) and fit α, β.

    `fit_only_monotonic_prefix`: if True (default), trim data to the longest
    initial monotonic-decreasing prefix (classical TRIP regime). For M54
    this means {0 %, 20 %} only — not enough points to fit two parameters
    well, but the trim avoids feeding the non-monotonic 40/60 % data to
    Olson-Cohen which doesn't model austenite formation.
    """
    pts = list(data or USER_M54_CW_AUSTENITE_SURFACE)
    if not pts:
        raise ValueError("no data points")
    pts = sorted(pts, key=lambda p: p.cw_pct)

    if fit_only_monotonic_prefix:
        trimmed = [pts[0]]
        for p in pts[1:]:
            if p.f_austenite > trimmed[-1].f_austenite + 1e-6:
                break
            trimmed.append(p)
        pts = trimmed

    if len(pts) < 3:
        raise ValueError(
            f"need >=3 points to fit (α, β); got {len(pts)}. "
            "M54 data has only 2 monotonic points (0 → 20 % CR); use "
            "`fit_only_monotonic_prefix=False` to fit all data and accept the bad fit, "
            "or supply a finer-resolution dataset."
        )

    baseline = pts[0]
    if baseline.cw_pct != 0:
        raise ValueError(f"first point must be cw=0% baseline, got cw={baseline.cw_pct}")
    if baseline.f_austenite <= 0:
        raise ValueError("baseline f_austenite must be > 0 to normalise")

    eps_list = [cw_pct_to_true_strain(p.cw_pct) for p in pts[1:]]
    f_ap_list = [
        max(0.0, min(1.0, (baseline.f_austenite - p.f_austenite) / baseline.f_austenite))
        for p in pts[1:]
    ]
    return fit_olson_cohen(eps_list, f_ap_list, n=n, T_celsius=T_celsius)
