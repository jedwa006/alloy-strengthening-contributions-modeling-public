"""High-level XRD analysis for the M54 cw/cr workbook.

Pulls the spectra via `m54model.calibration.data_loaders.load_xrd_spectrum`,
fits all six BCC + three FCC peaks per CR condition, and returns
α′/γ lattice parameters + Modified Miller V_γ + Bain ε^V.

Phase 3.6b deliverable.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from m54model.xrd.bain import bain_volumetric_strain
from m54model.xrd.peak_analysis import (
    PeakWindow,
    bcc_alpha_a0_from_peak,
    fcc_gamma_a0_from_peak,
    integrate_peak,
    modified_miller_V_gamma,
    nelson_riley_extrapolation,
)

# Expected peaks for BCC α′ at Cu-equivalent 2θ (a₀ ≈ 2.866 Å).
ALPHA_PEAKS: list[tuple[PeakWindow, tuple[int, int, int]]] = [
    (PeakWindow(44.7, 0.6, "110-α"), (1, 1, 0)),
    (PeakWindow(65.0, 0.8, "200-α"), (2, 0, 0)),
    (PeakWindow(82.3, 0.8, "211-α"), (2, 1, 1)),
    (PeakWindow(99.0, 1.0, "220-α"), (2, 2, 0)),
    (PeakWindow(116.4, 1.2, "310-α"), (3, 1, 0)),
    (PeakWindow(137.2, 2.0, "222-α"), (2, 2, 2)),
]

# Expected peaks for FCC γ at Cu-equivalent 2θ (a₀ ≈ 3.60 Å).
GAMMA_PEAKS: list[tuple[PeakWindow, tuple[int, int, int]]] = [
    (PeakWindow(50.7, 0.8, "200-γ"), (2, 0, 0)),
    (PeakWindow(74.5, 0.8, "220-γ"), (2, 2, 0)),
    (PeakWindow(90.4, 0.9, "311-γ"), (3, 1, 1)),
]

# Per Zhu Eq. 1: I_α uses (200-α + 211-α); I_γ uses (200-γ + 220-γ).
ZHU_ALPHA_INDICES = (1, 2)
ZHU_GAMMA_INDICES = (0, 1)

# Minimum integrated counts to consider a γ peak "real" (above noise).
GAMMA_MIN_COUNTS = 100.0


@dataclass(frozen=True)
class PeakFit:
    label: str
    expected_2theta_deg: float
    fit_2theta_deg: float
    integrated_counts: float
    a0_A: float | None  # None if not strong enough to extract


@dataclass(frozen=True)
class XRDAnalysisResult:
    """Per-CR-condition: α + γ peak fits, lattice params, V_γ, Bain ε^V."""

    cw_pct: float
    alpha_peaks: list[PeakFit] = field(default_factory=list)
    gamma_peaks: list[PeakFit] = field(default_factory=list)
    a_alpha_A_NR_extrapolated: float | None = None
    """Nelson-Riley extrapolated α′ a₀ from the 4 highest-2θ peaks."""
    a_gamma_A_best: float | None = None
    """γ a₀ from the highest-2θ γ peak that exceeded the noise threshold."""
    V_gamma_pct: float = 0.0
    """Modified Miller bulk V_γ (%)."""
    bain_eps_V: float | None = None
    """γ → α′ volumetric Bain strain (None if γ too weak to fit a₀)."""

    def __repr__(self) -> str:
        bits = [
            f"  CR {self.cw_pct:4.0f}%:",
            f"    a_α′ (NR)   = {self.a_alpha_A_NR_extrapolated:.4f} Å"
            if self.a_alpha_A_NR_extrapolated
            else "    a_α′ (NR)   = (insufficient peaks)",
            f"    a_γ (best) = {self.a_gamma_A_best:.4f} Å"
            if self.a_gamma_A_best
            else "    a_γ (best) = (γ too weak)",
            f"    V_γ        = {self.V_gamma_pct:.2f} %",
            f"    Bain ε^V   = {self.bain_eps_V:+.4f}"
            if self.bain_eps_V is not None
            else "    Bain ε^V   = n/a",
        ]
        return "\n".join(bits)


def analyze_xrd_for_cr(cw_pct: float) -> XRDAnalysisResult:
    """Full Phase 3.6b analysis at one CR condition. Loads via
    `m54model.calibration.data_loaders.load_xrd_spectrum`."""
    from m54model.calibration.data_loaders import load_xrd_spectrum

    pts = load_xrd_spectrum(cw_pct)
    twos = [p.two_theta_deg for p in pts]
    ints = [p.intensity_counts for p in pts]

    alpha_fits: list[PeakFit] = []
    a_alpha_pairs: list[tuple[float, float]] = []  # (a, 2θ) for NR extrapolation
    for window, hkl in ALPHA_PEAKS:
        I, t_peak = integrate_peak(twos, ints, window)
        a = bcc_alpha_a0_from_peak(t_peak, hkl) if I > 0 else None
        alpha_fits.append(PeakFit(window.label, window.expected_2theta_deg, t_peak, I, a))
        if a is not None:
            a_alpha_pairs.append((a, t_peak))

    gamma_fits: list[PeakFit] = []
    a_gamma_pairs: list[tuple[float, float]] = []  # (a, 2θ) above noise
    for window, hkl in GAMMA_PEAKS:
        I, t_peak = integrate_peak(twos, ints, window)
        a = (
            fcc_gamma_a0_from_peak(t_peak, hkl)
            if I > GAMMA_MIN_COUNTS
            else None
        )
        gamma_fits.append(PeakFit(window.label, window.expected_2theta_deg, t_peak, I, a))
        if a is not None:
            a_gamma_pairs.append((a, t_peak))

    a_alpha_NR: float | None = None
    if len(a_alpha_pairs) >= 2:
        # Use the 4 highest-2θ α′ peaks (most precise via NR).
        top = sorted(a_alpha_pairs, key=lambda x: -x[1])[:4]
        a_alpha_NR, _ = nelson_riley_extrapolation(
            [a for a, _ in top], [t for _, t in top]
        )

    a_gamma_best: float | None = None
    if a_gamma_pairs:
        a_gamma_best = sorted(a_gamma_pairs, key=lambda x: -x[1])[0][0]

    # Modified Miller V_γ uses (200-α + 211-α) for I_α and (200-γ + 220-γ) for I_γ.
    I_alpha_total = sum(alpha_fits[i].integrated_counts for i in ZHU_ALPHA_INDICES)
    I_gamma_total = sum(gamma_fits[i].integrated_counts for i in ZHU_GAMMA_INDICES)
    V_gamma_pct = 100.0 * modified_miller_V_gamma(I_alpha_total, I_gamma_total)

    bain = (
        bain_volumetric_strain(a_alpha_NR, a_gamma_best)
        if (a_alpha_NR is not None and a_gamma_best is not None)
        else None
    )

    return XRDAnalysisResult(
        cw_pct=cw_pct,
        alpha_peaks=alpha_fits,
        gamma_peaks=gamma_fits,
        a_alpha_A_NR_extrapolated=a_alpha_NR,
        a_gamma_A_best=a_gamma_best,
        V_gamma_pct=V_gamma_pct,
        bain_eps_V=bain,
    )


def analyze_all_cr_conditions(
    cw_pcts: tuple[float, ...] = (0, 20, 40, 60),
) -> list[XRDAnalysisResult]:
    return [analyze_xrd_for_cr(cw) for cw in cw_pcts]
