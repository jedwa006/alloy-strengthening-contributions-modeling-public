"""Universal constants for the M54 strengthening model.

Sourced from MODEL_PLAN.md §3.5. Where conventions diverge between Sun 2022,
Wang 2024 / Zhu 2025, and Galindo-Nava 2015, we keep both and make the choice
explicit at the call site.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

# ---------- core physical constants -------------------------------------------------

SIGMA_0_MPA = 50.0
"""Lattice friction stress for secondary-hardening BCC steel (MPa).
Universal across Sun 2022, Wang 2024, Zhu 2025, Galindo-Nava 2015."""

G_MATRIX_GPA = 80.0
"""Matrix shear modulus, BCC alpha-Fe (GPa)."""

G_NIAL_GPA = 88.0
"""NiAl precipitate shear modulus (GPa) — unused for M54 (no Al)."""

B_NM = 0.25
"""Burgers vector in BCC alpha-Fe (nm). Sun/Wang/Zhu convention.
Galindo-Nava 2015 uses 0.286 nm which appears to be the lattice parameter
a0, not |b|; |b| = a0*sqrt(3)/2 = 0.248 nm."""

R_C_NIAL_NM = 3.8
"""NiAl shearing -> Orowan-looping critical radius (nm). Yang 2023.
Unused for M54 (no NiAl)."""

SIGMA_AUSTENITE_MPA = 360.0
"""Reverted/retained austenite yield strength used in rule-of-mixtures
correction. From Li 2026 C64 paper. Only applied when f_A > 0."""

K_INTRINSIC_MARTENSITE_MPA_PER_SQRT_WTPCT = 985.0
"""As-quenched intrinsic-martensite strengthening coefficient.
sigma_intrinsic = K * sqrt(wt%C in solid solution).

Calibrated against Sun 2022 DQ anchor (YS 1420 MPa) — with K=985, the
predicted sigma_y closes to within ±1 % at 0.30 wt%C in solution. AF
state validates at +1.1 % miss with the same K (no retuning needed for
ausformed condition).

Physical interpretation: residual carbon-related strengthening NOT
captured by Fleischer-C — i.e. the Bain-distortion / supersaturation
contribution + lath-boundary HP that block-based HP under-counts.
Disappears in tempered states because (a) C drops to ~0.003 wt% and
(b) laths coarsen during recovery.

For comparison: Speich-Leslie 1972 empirical fit on plain-C steels
gives sigma_C_total = 1722 * sqrt(wt%C). The 1722 lumps Fleischer-C +
Bain + lath; our 985 is the residual after Fleischer-C is counted
separately."""

# ---------- divergent constants — pick a strategy ------------------------------------


class Convention(StrEnum):
    """Which paper's constants to use where conventions diverge."""

    SUN = "sun"  # Sun et al. 2022 (the user's own M54 paper) — DEFAULT
    WANG = "wang"  # Wang B. 2024 / Zhu et al. 2025 / most other lit


@dataclass(frozen=True)
class StrengtheningConstants:
    """Convention-dependent constants. Default to Sun 2022 (user's paper).

    Switch to WANG convention via `StrengtheningConstants.from_convention(Convention.WANG)`
    if reproducing Wang/Zhu numbers exactly.
    """

    M_taylor: float
    """Taylor factor (dimensionless). Used in Orowan-style formulas. NOT used
    in dislocation strengthening — that's already absorbed into alpha_BH."""

    alpha_BH: float
    """Effective Schmid-averaged prefactor in sigma_rho = alpha_eff * G * b * sqrt(rho).
    Taylor factor is implicit. Conventions:
    - Sun 2022 (per Bhadeshia & Honeycombe Steels Ch. 14): alpha = 0.38.
    - Wang 2024 / Zhu 2025: original form alpha * M * G * b * sqrt(rho) with
      alpha = 0.25, M = 2.5 → effective alpha_eff = 0.625. We pre-collapse it."""

    K_HP_MPa_um_half: float
    """Hall-Petch coefficient with d in micrometers (MPa·µm^(1/2)).
    Sun fit 230 from his Hall-Petch plot. Wang/Zhu use 300."""

    @classmethod
    def from_convention(cls, c: Convention = Convention.SUN) -> StrengtheningConstants:
        if c == Convention.SUN:
            return cls(M_taylor=2.5, alpha_BH=0.38, K_HP_MPa_um_half=230.0)
        if c == Convention.WANG:
            # Wang/Zhu original: alpha=0.25, M=2.5 → effective 0.625
            return cls(M_taylor=2.5, alpha_BH=0.625, K_HP_MPa_um_half=300.0)
        raise ValueError(f"unknown convention {c}")


# ---------- Fleischer solid-solution-strengthening coefficients ----------------------

# β_i in MPa per sqrt(at-fraction). From Zhu 2025 Table 3 (originally Niu 2019).
# Missing: W, V, C — flagged below for compute-from-mismatch (Galindo-Nava Appx A).
FLEISCHER_BETA_MPA: dict[str, float] = {
    "Co": 200.0,
    "Ni": 405.8,
    "Cr": 174.0,
    "Mo": 953.5,
    "Al": 196.0,
}

# TODO: compute β_W, β_V from atomic-radius + shear-modulus mismatch (Galindo-Nava
# Appendix A) and add here. β_C dominates the DQ-state YS prediction (~200 MPa
# contribution at 1.4 at%); needs careful sourcing from Krauss 1999 or similar.
FLEISCHER_BETA_PLACEHOLDERS_MPA: dict[str, float] = {
    "W": 700.0,  # placeholder — atomic radius and modulus close to Mo
    "V": 200.0,  # placeholder — modulus mismatch much smaller than Mo
    "C": 1722.0,  # placeholder — order of magnitude per Speich 1972
    "Ti": 250.0,  # placeholder — minor contribution (~0.01 wt% in M54)
}


# ---------- summation strategy --------------------------------------------------------

SummationStrategy = Literal["linear", "pythagorean_p", "pythagorean_dp"]
"""How sigma_y is assembled from contributions.

- 'linear':            sigma_y = sigma_0 + sigma_ss + sigma_HP + sigma_rho + sigma_p
                       Sun 2022 + Zhu 2025 (DEFAULT).
- 'pythagorean_p':     sigma_y = sigma_0 + sigma_ss + sigma_HP + sigma_rho + sqrt(sum sigma_pi^2)
                       Pythagorean within precipitation only (between M2C, MC, NiAl).
- 'pythagorean_dp':    sigma_y = sigma_0 + sigma_ss + sigma_HP + sqrt(sigma_rho^2 + sigma_p^2)
                       Wang 2024 / Li 2026 C64 — Pythagorean across dislocation+precipitation.
"""


# ---------- precipitate-population summary --------------------------------------------


@dataclass(frozen=True)
class CarbideAnchor:
    """Measured precipitate population from a literature anchor."""

    source: str
    state_label: str
    radius_nm: float | None
    length_nm: float | None
    width_nm: float | None
    aspect_ratio: float | None
    number_density_per_m3: float | None
    volume_fraction: float | None
    spacing_nm: float | None
    composition_at_frac: dict[str, float] = field(default_factory=dict)


# Mondière 2018 commercial DQ+T516/10 anchor (M54). N and f_v not reported.
MONDIERE_M54_T516_10 = CarbideAnchor(
    source="zhu07_Mondiere_2018",
    state_label="DQ + T 516C / 10h (commercial M54)",
    radius_nm=None,
    length_nm=9.6,
    width_nm=1.2,
    aspect_ratio=8.0,
    number_density_per_m3=None,
    volume_fraction=None,
    spacing_nm=None,
    composition_at_frac={"Mo": 0.50, "Cr": 0.125, "W": 0.10, "Fe": 0.10, "Ni": 0.10, "V": 0.025},
)

# Wang 2024 DQ+T520/8 (peak hardening — closest to commercial 516/10).
WANG_M54_T520_8 = CarbideAnchor(
    source="zhu41_Wang_2024",
    state_label="DQ + T 520C / 8h (Wang peak)",
    radius_nm=0.85,  # mean of 0.8-0.9 nm range
    length_nm=4.0,
    width_nm=0.8,
    aspect_ratio=5.0,
    number_density_per_m3=6.5e20,  # 650 µm⁻² × estimated foil thickness 100 nm
    volume_fraction=None,  # not numerically reported at 8h; bracketed 0.09%–0.29%
    spacing_nm=12.3,
    composition_at_frac={"Mo": 0.50, "Cr": 0.125, "W": 0.10, "Fe": 0.10, "Ni": 0.10, "V": 0.025},
)
