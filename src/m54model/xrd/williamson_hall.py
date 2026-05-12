"""Classical Williamson-Hall analysis on the user's M54 Cu-equivalent XRD spectra.

Goal (Phase 3.6g)
-----------------
Extract a per-CR-condition total dislocation density ρ_WH from the BCC α′
peak broadening, and compare to the ASTAR-PED-derived ρ_GND already in the
codebase (`USER_M54_GND_DENSITY`). The ratio k = ρ_WH / ρ_GND is the SSD
multiplier that Phase 3.6e left as a free knob (defaulted k = 1.0).

Method
------
For each α′ peak (1 1 0), (2 0 0), (2 1 1), (2 2 0), (3 1 0), (2 2 2) we:

1. Fit FWHM by half-max width above a linear baseline drawn from the window
   edges (same baseline scheme as `peak_analysis.integrate_peak`). This is a
   first-cut: a full Gaussian/Voigt fit would be more accurate but the
   workbook step is ~0.043° and the FWHMs we see are 0.4 - 2.0°, so the
   half-max-width estimate is well-resolved.

2. Subtract instrumental broadening β_inst (default 0.08° in 2θ — a typical
   value for a well-aligned lab Cu-Kα diffractometer; see CAVEAT below).
   Subtraction is in quadrature for Gaussian profiles:
       β_sample² = β_obs² − β_inst²

3. Convert FWHM-deg to Gaussian integral breadth in radians:
       β_int = FWHM_rad · √(π / (4 ln 2))
   so the standard Williamson-Hall variable β·cos θ has the right units.

4. Linear regression of (β·cos θ) versus (sin θ):
       β · cos θ = K λ / D + 4 · ε · sin θ
   slope = 4 ε  → microstrain ε
   intercept = K λ / D → column-length crystallite size D (K = 0.9 Scherrer).

5. Dislocation density:
       ρ_WH ≈ k_α · ε² / b²
   with k_α = 14.4 for screw-dominated α-Fe (BCC), b = 0.248 nm.
   For α-Fe this gives ρ ≈ 2.34 × 10²⁰ · ε² (m⁻²), so ε ≈ 2 × 10⁻³ → ρ ≈ 1 × 10¹⁵.

CAVEATS (read me before quoting absolute ρ_WH numbers)
------------------------------------------------------
- **Classical (isotropic) WH** assumes strain broadening has no hkl dependence.
  For BCC steels with strong rolling texture and anisotropic dislocation
  contrast factors (Borbely 2022, `pdf-archive/zhu22_Borbely_2022_WH_dislocation.pdf`),
  the **modified** WH (mWH) with hkl-dependent C̄ is more accurate. Absolute ρ
  here may differ from mWH by a factor of ~2.

- **Instrumental broadening β_inst** is set to a typical 0.08° in 2θ. The user's
  workbook does NOT include a Si or LaB₆ standard reference scan in the same
  geometry, so this is an estimate, not a measured quantity. The 0% CR 110-α
  peak FWHM is 0.39° — well above 0.08°, so the result is not very sensitive
  to the exact β_inst choice as long as it is < ~0.15°. For the lower-counts
  high-angle peaks (where FWHM is naturally larger), β_inst contributes <5%.

- **K_α prefactor** (14.4 vs 16.1) reflects screw-dominated vs edge-dominated
  α-Fe; we use 14.4 as the BCC-martensite default (Williamson-Smallman 1956).
  Either choice changes ρ by ±10%.

- **Peak quality filter**: peaks with max-above-baseline < `min_peak_height`
  (default 50 counts) are excluded from the regression — a few high-angle
  peaks at 60% CR are essentially in the noise floor.

These caveats compound: absolute ρ_WH could easily be off by ×2-3, but the
**trend with CR** and the **ratio to ρ_GND** are far more robust than the
absolute numbers because most systematic errors cancel in the ratio.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

from m54model.xrd.analysis import ALPHA_PEAKS
from m54model.xrd.peak_analysis import LAMBDA_CU_KA1_A, PeakWindow

# ---- Physical constants for α-Fe / M54 BCC matrix --------------------------------------

BURGERS_VECTOR_ALPHA_FE_M = 0.248e-9
"""Burgers vector magnitude for α-Fe (BCC), b = a₀·√3/2 ≈ 0.248 nm."""

K_ALPHA_BCC_SCREW = 14.4
"""Williamson-Smallman prefactor for screw-dominated BCC: ρ = k_α · ε² / b².
Edge-dominated would be 16.1; we use the screw value as the M54 default
because cold-rolled lath martensite is dominated by screw a/2<111>."""

SCHERRER_K = 0.9
"""Crystallite-size shape factor for the column-length D (typical spheroidal
to slightly anisotropic shape; Klug & Alexander 1974). Used only for D, not ρ."""

DEFAULT_BETA_INST_DEG = 0.08
"""Default instrumental broadening (FWHM in degrees 2θ). See module docstring
caveat: workbook has no Si/LaB₆ standard, so this is estimated for a typical
lab Cu-Kα diffractometer with reasonable optics."""

DEFAULT_MIN_PEAK_HEIGHT = 50.0
"""Minimum max-above-baseline counts to include a peak in the WH regression.
Below this, the FWHM measurement is dominated by noise."""

# Conversion: FWHM → Gaussian integral breadth.
# For a Gaussian, β_int = FWHM · √(π / (4 ln 2)) ≈ 1.0645 · FWHM.
GAUSSIAN_FWHM_TO_BETA = math.sqrt(math.pi / (4.0 * math.log(2.0)))


# ---- Per-peak FWHM extraction -----------------------------------------------------------


def estimate_fwhm_deg(
    two_theta_deg: Sequence[float],
    intensity: Sequence[float],
    window: PeakWindow,
) -> tuple[float, float, float]:
    """Estimate FWHM (in degrees 2θ), peak position, and max height above
    a linear baseline drawn between the window edges.

    Returns (fwhm_deg, peak_2theta_deg, max_above_baseline).
    If the peak is empty / non-existent (no points above baseline), returns
    (0.0, window.expected_2theta_deg, 0.0).
    """
    if len(two_theta_deg) != len(intensity):
        raise ValueError("two_theta_deg and intensity must be same length")
    lo = window.expected_2theta_deg - window.half_width_deg
    hi = window.expected_2theta_deg + window.half_width_deg
    in_window = [
        (t, i) for t, i in zip(two_theta_deg, intensity, strict=True) if lo <= t <= hi
    ]
    if len(in_window) < 5:
        return 0.0, window.expected_2theta_deg, 0.0
    in_window.sort(key=lambda x: x[0])

    # Linear baseline from edge averages (mean of leading/trailing 5% of points).
    n_edge = max(1, len(in_window) // 20)
    edge_lo = sum(p[1] for p in in_window[:n_edge]) / n_edge
    edge_hi = sum(p[1] for p in in_window[-n_edge:]) / n_edge
    t_lo = in_window[0][0]
    t_hi = in_window[-1][0]
    if t_hi == t_lo:
        return 0.0, window.expected_2theta_deg, 0.0
    slope = (edge_hi - edge_lo) / (t_hi - t_lo)

    def baseline(t: float) -> float:
        return edge_lo + slope * (t - t_lo)

    heights = [(t, i - baseline(t)) for t, i in in_window]
    max_h = max(h for _, h in heights)
    if max_h <= 0.0:
        return 0.0, window.expected_2theta_deg, 0.0

    # Find the 2θ at the maximum.
    peak_t = max(heights, key=lambda x: x[1])[0]

    # FWHM by linear interpolation between adjacent samples that bracket
    # the half-max threshold on each side of the peak.
    half = max_h / 2.0
    # Walk left from peak.
    t_left = heights[0][0]
    for j in range(len(heights) - 1):
        t0, h0 = heights[j]
        t1, h1 = heights[j + 1]
        if t1 > peak_t:
            break
        if (h0 < half <= h1) or (h0 <= half < h1):
            # Linear interp on (t, h).
            t_left = t0 if h1 == h0 else t0 + (half - h0) * (t1 - t0) / (h1 - h0)
    # Walk right from peak.
    t_right = heights[-1][0]
    for j in range(len(heights) - 1):
        t0, h0 = heights[j]
        t1, h1 = heights[j + 1]
        if t0 < peak_t:
            continue
        if (h0 >= half > h1) or (h0 > half >= h1):
            t_right = t1 if h1 == h0 else t0 + (half - h0) * (t1 - t0) / (h1 - h0)
            break

    fwhm = max(0.0, t_right - t_left)
    return fwhm, peak_t, max_h


# ---- Williamson-Hall regression ---------------------------------------------------------


@dataclass(frozen=True)
class PeakBroadening:
    """Per-peak inputs to the Williamson-Hall regression."""

    label: str
    two_theta_deg: float
    fwhm_obs_deg: float  # observed FWHM (raw, before instrumental subtraction)
    max_above_baseline: float  # used for the noise filter
    fwhm_sample_deg: float  # after quadrature subtraction of β_inst
    beta_int_rad: float  # Gaussian integral breadth in radians
    sin_theta: float  # sin(θ), θ in radians (note: θ = 2θ/2)
    cos_theta: float  # cos(θ)
    used_in_regression: bool  # False if filtered (low intensity, etc.)


@dataclass(frozen=True)
class WHResult:
    """Williamson-Hall analysis result for one CR condition."""

    cw_pct: float
    peaks: list[PeakBroadening] = field(default_factory=list)

    epsilon_microstrain: float = 0.0
    """Lattice microstrain (dimensionless), from regression slope = 4·ε."""

    D_size_nm: float | None = None
    """Column-length crystallite size from intercept = K·λ/D. None if intercept
    is non-physical (zero/negative — means the regression has no size term)."""

    rho_WH_per_m2: float = 0.0
    """Total dislocation density (m⁻²) from ρ ≈ K_α · ε² / b²."""

    n_peaks_used: int = 0
    """How many peaks survived the noise filter."""

    beta_inst_deg: float = DEFAULT_BETA_INST_DEG
    K_alpha: float = K_ALPHA_BCC_SCREW
    burgers_m: float = BURGERS_VECTOR_ALPHA_FE_M

    notes: str = ""

    def __repr__(self) -> str:
        bits = [
            f"  CR {self.cw_pct:4.0f}%:",
            f"    ε (microstrain) = {self.epsilon_microstrain:.2e}",
            "    D (size, nm)    = "
            + (f"{self.D_size_nm:.1f}" if self.D_size_nm is not None else "(non-physical)"),
            f"    ρ_WH (m⁻²)     = {self.rho_WH_per_m2:.2e}",
            f"    n peaks used   = {self.n_peaks_used}",
        ]
        if self.notes:
            bits.append(f"    {self.notes}")
        return "\n".join(bits)


def williamson_hall_regression(
    peak_2theta_deg: Sequence[float],
    fwhm_deg: Sequence[float],
    *,
    lambda_A: float = LAMBDA_CU_KA1_A,
    K: float = SCHERRER_K,
) -> tuple[float, float | None]:
    """Classical Williamson-Hall: linear regression of β·cosθ vs sinθ.

    Inputs:
      peak_2theta_deg: per-peak peak positions in degrees 2θ (already
        instrumental-broadening-corrected? caller's choice; this fn does no
        β_inst handling).
      fwhm_deg: per-peak FWHMs in degrees 2θ (same indexing as above).

    Returns (epsilon_microstrain, D_size_nm). D_size_nm is None when the
    intercept is zero or negative (no resolvable size term — the broadening
    is essentially all strain).
    """
    if len(peak_2theta_deg) != len(fwhm_deg):
        raise ValueError("peak_2theta_deg and fwhm_deg must be same length")
    if len(peak_2theta_deg) < 2:
        raise ValueError("need >= 2 peaks for WH regression")

    xs: list[float] = []
    ys: list[float] = []
    for t2_deg, fwhm_d in zip(peak_2theta_deg, fwhm_deg, strict=True):
        theta_rad = math.radians(t2_deg / 2.0)
        beta_rad = math.radians(fwhm_d) * GAUSSIAN_FWHM_TO_BETA
        xs.append(math.sin(theta_rad))
        ys.append(beta_rad * math.cos(theta_rad))

    n = len(xs)
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xy = sum(x * y for x, y in zip(xs, ys, strict=True))
    sum_x2 = sum(x * x for x in xs)
    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        # All sin θ identical — undefined. Return zero strain, no size.
        return 0.0, None
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    epsilon = max(0.0, slope / 4.0)
    if intercept <= 0.0:
        D_nm = None
    else:
        # K · λ / D = intercept (in radians); λ given in Å → D in Å, /10 → nm.
        D_A = K * lambda_A / intercept
        D_nm = D_A / 10.0
    return epsilon, D_nm


def dislocation_density_from_microstrain(
    epsilon: float,
    *,
    K_alpha: float = K_ALPHA_BCC_SCREW,
    b_m: float = BURGERS_VECTOR_ALPHA_FE_M,
) -> float:
    """ρ ≈ K_α · ε² / b². Returns m⁻². For α-Fe defaults this is
    ≈ 2.34 × 10²⁰ · ε² m⁻²."""
    if epsilon < 0:
        raise ValueError("epsilon must be >= 0")
    return K_alpha * (epsilon * epsilon) / (b_m * b_m)


# ---- High-level helpers -----------------------------------------------------------------


def analyze_williamson_hall_for_cr(
    cw_pct: float,
    *,
    beta_inst_deg: float = DEFAULT_BETA_INST_DEG,
    min_peak_height: float = DEFAULT_MIN_PEAK_HEIGHT,
    K_alpha: float = K_ALPHA_BCC_SCREW,
    b_m: float = BURGERS_VECTOR_ALPHA_FE_M,
    lambda_A: float = LAMBDA_CU_KA1_A,
    K: float = SCHERRER_K,
) -> WHResult:
    """Run a classical-WH analysis on the user's α′ peaks at one CR condition.

    Loads the spectrum via `m54model.calibration.data_loaders.load_xrd_spectrum`,
    estimates per-peak FWHM by half-max-width above a linear baseline, subtracts
    instrumental broadening in quadrature (Gaussian assumption), then regresses
    β·cosθ vs sinθ across the peaks that survive the noise filter.
    """
    from m54model.calibration.data_loaders import load_xrd_spectrum

    pts = load_xrd_spectrum(cw_pct)
    twos = [p.two_theta_deg for p in pts]
    ints = [p.intensity_counts for p in pts]

    peak_records: list[PeakBroadening] = []
    used_2theta: list[float] = []
    used_fwhm: list[float] = []

    for window, _hkl in ALPHA_PEAKS:
        fwhm_obs, peak_t, max_h = estimate_fwhm_deg(twos, ints, window)
        # Quadrature subtraction of instrumental broadening (Gaussian assumption).
        fwhm_sq = fwhm_obs * fwhm_obs - beta_inst_deg * beta_inst_deg
        fwhm_sample = math.sqrt(fwhm_sq) if fwhm_sq > 0 else 0.0
        # Convert to integral breadth in radians.
        beta_int_rad = math.radians(fwhm_sample) * GAUSSIAN_FWHM_TO_BETA
        theta_rad = math.radians(peak_t / 2.0)
        sin_t = math.sin(theta_rad)
        cos_t = math.cos(theta_rad)
        used = max_h >= min_peak_height and fwhm_sample > 0.0
        peak_records.append(
            PeakBroadening(
                label=window.label,
                two_theta_deg=peak_t,
                fwhm_obs_deg=fwhm_obs,
                max_above_baseline=max_h,
                fwhm_sample_deg=fwhm_sample,
                beta_int_rad=beta_int_rad,
                sin_theta=sin_t,
                cos_theta=cos_t,
                used_in_regression=used,
            )
        )
        if used:
            used_2theta.append(peak_t)
            used_fwhm.append(fwhm_sample)

    notes = ""
    if len(used_2theta) < 2:
        notes = "fewer than 2 peaks above noise floor; ε set to 0"
        return WHResult(
            cw_pct=cw_pct,
            peaks=peak_records,
            epsilon_microstrain=0.0,
            D_size_nm=None,
            rho_WH_per_m2=0.0,
            n_peaks_used=len(used_2theta),
            beta_inst_deg=beta_inst_deg,
            K_alpha=K_alpha,
            burgers_m=b_m,
            notes=notes,
        )

    epsilon, D_nm = williamson_hall_regression(
        used_2theta, used_fwhm, lambda_A=lambda_A, K=K
    )
    rho = dislocation_density_from_microstrain(epsilon, K_alpha=K_alpha, b_m=b_m)

    return WHResult(
        cw_pct=cw_pct,
        peaks=peak_records,
        epsilon_microstrain=epsilon,
        D_size_nm=D_nm,
        rho_WH_per_m2=rho,
        n_peaks_used=len(used_2theta),
        beta_inst_deg=beta_inst_deg,
        K_alpha=K_alpha,
        burgers_m=b_m,
        notes=notes,
    )


def analyze_williamson_hall_all_cr(
    cw_pcts: tuple[float, ...] = (0, 20, 40, 60),
    **kwargs,
) -> list[WHResult]:
    """Run WH at each CR condition. Forwards kwargs to
    `analyze_williamson_hall_for_cr`."""
    return [analyze_williamson_hall_for_cr(cw, **kwargs) for cw in cw_pcts]


def wh_vs_gnd_for_all_cr(
    cw_pcts: tuple[float, ...] = (0, 20, 40, 60),
    *,
    gnd_metric: str = "BCC_median",
    **kwargs,
) -> list[dict]:
    """Compare WH-derived ρ_total vs ASTAR-PED ρ_GND at each CR condition.

    Returns a list of dicts (one per CR), each with:
      cw_pct, rho_GND_per_m2, rho_WH_per_m2,
      multiplier_k (= ρ_WH / ρ_GND), epsilon_microstrain, n_peaks_used.

    `gnd_metric`: forwarded to `gnd_for_cr` (one of 'BCC_median', 'BCC_p90',
    'FCC_median'). Default 'BCC_median' matches the σ_y model's input.
    """
    from m54model.calibration.user_microstructure_data import gnd_for_cr

    out: list[dict] = []
    for cw in cw_pcts:
        wh = analyze_williamson_hall_for_cr(cw, **kwargs)
        rho_gnd = gnd_for_cr(cw, location_phase=gnd_metric)
        k = wh.rho_WH_per_m2 / rho_gnd if rho_gnd > 0 else float("inf")
        out.append(
            {
                "cw_pct": cw,
                "rho_GND_per_m2": rho_gnd,
                "rho_WH_per_m2": wh.rho_WH_per_m2,
                "multiplier_k": k,
                "epsilon_microstrain": wh.epsilon_microstrain,
                "n_peaks_used": wh.n_peaks_used,
            }
        )
    return out
