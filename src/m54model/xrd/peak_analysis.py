"""Peak fitting + lattice-parameter extraction from Cu-equivalent XRD spectra.

Equations:

  Bragg's law:        n·λ = 2·d·sin(θ)
  Cubic d-spacing:    1/d² = (h² + k² + l²)/a²
                       so   a = d · √(h² + k² + l²)

  Modified Miller (Zhu 2025 Eq. 1, ref [21]):
                        V_γ = 1.4 · I_γ / (I_α + 1.4 · I_γ)
                       where I_α = ∫ I(2θ) over (200-α + 211-α) windows
                             I_γ = ∫ I(2θ) over (200-γ + 220-γ) windows
                       The 1.4 factor is the texture/structure-factor correction
                       averaged over typical Fe austenite/martensite peak ratios.

Conventions: 2θ in degrees, λ in Å, a in Å.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

LAMBDA_CU_KA1_A = 1.5406
"""Wavelength of Cu Kα1 (Å). User's workbooks are converted to Cu-equivalent 2θ."""


def lattice_parameter_from_2theta(
    two_theta_deg: float,
    hkl: tuple[int, int, int],
    *,
    lambda_A: float = LAMBDA_CU_KA1_A,
) -> float:
    """Extract cubic lattice parameter a₀ (Å) from one peak position.

    Combines Bragg + cubic d-spacing:
        d = λ / (2 sin θ)
        a = d · √(h² + k² + l²)
    """
    if two_theta_deg <= 0 or two_theta_deg >= 180:
        raise ValueError(f"2θ must be in (0, 180), got {two_theta_deg}")
    h, k, l = hkl
    d = lambda_A / (2.0 * math.sin(math.radians(two_theta_deg / 2.0)))
    return d * math.sqrt(h * h + k * k + l * l)


def bcc_alpha_a0_from_peak(
    two_theta_deg: float,
    hkl: tuple[int, int, int],
    *,
    lambda_A: float = LAMBDA_CU_KA1_A,
) -> float:
    """Same as `lattice_parameter_from_2theta` but checks hkl is allowed for BCC.

    BCC reflection condition: h+k+l even.
    """
    if sum(hkl) % 2 != 0:
        raise ValueError(f"hkl={hkl} forbidden for BCC (h+k+l must be even)")
    return lattice_parameter_from_2theta(two_theta_deg, hkl, lambda_A=lambda_A)


def fcc_gamma_a0_from_peak(
    two_theta_deg: float,
    hkl: tuple[int, int, int],
    *,
    lambda_A: float = LAMBDA_CU_KA1_A,
) -> float:
    """Same but checks hkl is allowed for FCC (all even or all odd)."""
    h, k, l = hkl
    parities = {x % 2 for x in (h, k, l)}
    if len(parities) != 1:
        raise ValueError(f"hkl={hkl} forbidden for FCC (must be all-even or all-odd)")
    return lattice_parameter_from_2theta(two_theta_deg, hkl, lambda_A=lambda_A)


def nelson_riley_extrapolation(
    a_values_A: Sequence[float],
    two_theta_deg_values: Sequence[float],
) -> tuple[float, float]:
    """Nelson-Riley extrapolation: corrects for systematic 2θ errors (sample
    displacement, axial divergence) by extrapolating a₀ to θ → 90°.

    Plot a vs (½)·[cos²θ/sinθ + cos²θ/θ_radians], linear regression, intercept
    at f→0 is the corrected a₀. Returns (a₀_extrapolated, slope).

    Robust to ≥3 peaks; for 1-2 peaks the result is dominated by the highest
    angle peak (NR factor smallest there).
    """
    if len(a_values_A) != len(two_theta_deg_values):
        raise ValueError("a_values and two_theta_deg_values must be same length")
    if len(a_values_A) < 2:
        raise ValueError("need >= 2 peaks for NR extrapolation")
    xs: list[float] = []
    for two_theta in two_theta_deg_values:
        theta_rad = math.radians(two_theta / 2.0)
        nr = 0.5 * (
            math.cos(theta_rad) ** 2 / math.sin(theta_rad)
            + math.cos(theta_rad) ** 2 / theta_rad
        )
        xs.append(nr)
    # Linear regression a = m·x + a₀
    n = len(xs)
    sum_x = sum(xs)
    sum_y = sum(a_values_A)
    sum_xy = sum(x * y for x, y in zip(xs, a_values_A, strict=True))
    sum_x2 = sum(x * x for x in xs)
    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        return sum_y / n, 0.0  # all NR factors equal → just average
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    return intercept, slope


@dataclass(frozen=True)
class PeakWindow:
    """A 2θ window around an expected peak; integrate intensity above a
    linear baseline drawn from the window edges."""

    expected_2theta_deg: float
    half_width_deg: float
    label: str = ""


def integrate_peak(
    two_theta_deg: Sequence[float],
    intensity: Sequence[float],
    window: PeakWindow,
) -> tuple[float, float]:
    """Integrate one peak above a linear baseline drawn between the
    window edges.

    Returns (integrated_counts, peak_2theta_at_max).
    """
    if len(two_theta_deg) != len(intensity):
        raise ValueError("two_theta_deg and intensity must be same length")
    lo = window.expected_2theta_deg - window.half_width_deg
    hi = window.expected_2theta_deg + window.half_width_deg
    in_window = [
        (t, i) for t, i in zip(two_theta_deg, intensity, strict=True) if lo <= t <= hi
    ]
    if len(in_window) < 3:
        return 0.0, window.expected_2theta_deg
    in_window.sort(key=lambda x: x[0])
    # Linear baseline from edges (mean of leading/trailing 5% of points).
    n_edge = max(1, len(in_window) // 20)
    edge_lo = sum(p[1] for p in in_window[:n_edge]) / n_edge
    edge_hi = sum(p[1] for p in in_window[-n_edge:]) / n_edge
    t_lo = in_window[0][0]
    t_hi = in_window[-1][0]
    if t_hi == t_lo:
        baseline = lambda t: edge_lo  # noqa: E731
    else:
        slope = (edge_hi - edge_lo) / (t_hi - t_lo)

        def baseline(t: float) -> float:
            return edge_lo + slope * (t - t_lo)

    # Trapezoidal integration of (intensity − baseline), clipped to ≥ 0.
    total = 0.0
    peak_t = window.expected_2theta_deg
    peak_i = -math.inf
    for j in range(1, len(in_window)):
        t0, i0 = in_window[j - 1]
        t1, i1 = in_window[j]
        b0 = baseline(t0)
        b1 = baseline(t1)
        h = max(0.0, i0 - b0)
        k = max(0.0, i1 - b1)
        total += 0.5 * (h + k) * (t1 - t0)
        if i0 - b0 > peak_i:
            peak_i = i0 - b0
            peak_t = t0
    return total, peak_t


def modified_miller_V_gamma(
    I_alpha_total: float,
    I_gamma_total: float,
    *,
    R_factor: float = 1.4,
) -> float:
    """Modified Miller (Zhu Eq. 1, ref [21]) bulk austenite volume fraction:

        V_γ = R · I_γ / (I_α + R · I_γ)

    where R = 1.4 is the standard structure-factor / texture correction.
    Returns dimensionless fraction in [0, 1].

    `I_alpha_total` should be the SUM of integrated intensities over the
    chosen α′ peaks (typically 200-α + 211-α). `I_gamma_total` similarly
    for chosen γ peaks (typically 200-γ + 220-γ + 311-γ).
    """
    if I_alpha_total < 0 or I_gamma_total < 0:
        raise ValueError("integrated intensities must be >= 0")
    denom = I_alpha_total + R_factor * I_gamma_total
    if denom <= 0:
        return 0.0
    return R_factor * I_gamma_total / denom
