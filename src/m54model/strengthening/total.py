"""Assemble all strengthening contributions into yield strength.

For derived properties (Tabor hardness, composite hardness, UTS via
work-hardening ratio), see `m54model.strengthening.derived_properties`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Literal

from m54model.constants import (
    MONDIERE_2025_F_A_SOFTENING_RATE_MPA_PER_PCT,
    SIGMA_AUSTENITE_MPA,
    Convention,
    StrengtheningConstants,
    SummationStrategy,
)

FACorrectionMode = Literal["rule_of_mix", "mondière_2025"]
from m54model.states import MicrostructuralState
from m54model.strengthening.dislocation import sigma_dislocation
from m54model.strengthening.friction import sigma_friction
from m54model.strengthening.hall_petch import sigma_hall_petch
from m54model.strengthening.intrinsic_martensite import sigma_intrinsic_martensite
from m54model.strengthening.orowan import sigma_orowan_carbide
from m54model.strengthening.solid_solution import sigma_fleischer


@dataclass(frozen=True)
class StrengtheningResult:
    """Decomposed yield-strength prediction."""

    sigma_y_MPa: float
    sigma_y_austenite_corrected_MPa: float
    contributions_MPa: dict[str, float] = field(default_factory=dict)
    strategy: str = "linear"

    def __repr__(self) -> str:
        parts = [f"  {k:14s} = {v:>7.1f} MPa" for k, v in self.contributions_MPa.items()]
        return (
            f"StrengtheningResult(strategy={self.strategy!r})\n"
            + "\n".join(parts)
            + f"\n  {'TOTAL':14s} = {self.sigma_y_MPa:>7.1f} MPa"
            + (
                f"\n  {'(after f_A)':14s} = {self.sigma_y_austenite_corrected_MPa:>7.1f} MPa"
                if self.sigma_y_austenite_corrected_MPa != self.sigma_y_MPa
                else ""
            )
        )


def assemble_yield_strength(
    state: MicrostructuralState,
    constants: StrengtheningConstants | None = None,
    strategy: SummationStrategy = "linear",
    beta_overrides: dict[str, float] | None = None,
    *,
    orowan_sub_critical: str = "clamp",
    f_A_correction_mode: FACorrectionMode = "rule_of_mix",
) -> StrengtheningResult:
    """Compute YS from a microstructural state.

    Reads everything from `state`: block size, dislocation density, matrix at%,
    precipitate populations, retained/reverted austenite fraction.

    Returns the decomposition (each contribution kept individually) and the
    summed sigma_y under the chosen strategy. f_austenite drives a separate
    correction reported as `sigma_y_austenite_corrected_MPa`.

    `f_A_correction_mode` (Phase 3.7d):
      - 'rule_of_mix' (default — backwards-compatible): σ_y_corr = (1 - f_A) ·
        σ_y + f_A · σ_A, with σ_A = SIGMA_AUSTENITE_MPA = 360 (Li 2026 C64).
        Gives ∂σ_y/∂f_A ≈ −13 MPa per 1 % γ for σ_matrix ≈ 1700 — much
        shallower than M54's measured rate.
      - 'mondière_2025': σ_y_corr = σ_y_matrix −
        MONDIERE_2025_F_A_SOFTENING_RATE_MPA_PER_PCT · (f_A · 100) =
        σ_y - 6800 · f_A. From Mondière 2025 Eq. 2 (YS = 1978 − 68·γ%
        on commercial M54). 5× steeper than rule-of-mix because it
        captures total γ-related softening (volumetric + interface +
        modulus + lath-boundary effects) as one lumped slope.

        **Caveat — extrapolation regime**: Mondière fit her relation on
        commercial M54 with γ% in the ~1-10 % range from various
        tempering schedules. At our user's high-CR core f_A = 12.6 %,
        applying the −68 MPa/% slope to our predicted σ_matrix (1672
        MPa) drops σ_y_corr to 815 MPa — **unphysical** vs measured
        1900 MPa. The relation is a *confounded* empirical observation
        (γ% co-varies with tempering-history-dependent matrix
        properties), not a clean f_A-only law. Recommended for cross-
        check use at f_A ≲ 5 %, NOT as a high-f_A correction.
    """
    c = constants or StrengtheningConstants.from_convention(Convention.SUN)

    contribs: dict[str, float] = {
        "sigma_0": sigma_friction(),
        "sigma_ss": sigma_fleischer(state.matrix_at_frac, beta_overrides=beta_overrides),
        "sigma_HP": sigma_hall_petch(state.block_width_um, constants=c),
        "sigma_rho": sigma_dislocation(state.dislocation_density_per_m2, constants=c),
        "sigma_intr": sigma_intrinsic_martensite(state),
    }
    p_terms: dict[str, float] = {
        f"sigma_{p.phase}": sigma_orowan_carbide(p, constants=c, sub_critical=orowan_sub_critical)
        for p in state.precipitates
    }
    contribs.update(p_terms)

    # Non-precipitation, non-rho contributions (these are linearly summed in all strategies).
    base_terms = ("sigma_0", "sigma_ss", "sigma_HP", "sigma_intr")
    base_sum = sum(contribs[k] for k in base_terms if k in contribs)

    if strategy == "linear":
        sigma_y = sum(contribs.values())
    elif strategy == "pythagorean_p":
        sigma_p = math.sqrt(sum(v**2 for v in p_terms.values())) if p_terms else 0.0
        contribs["sigma_p_combined"] = sigma_p
        sigma_y = base_sum + contribs["sigma_rho"] + sigma_p
    elif strategy == "pythagorean_dp":
        sigma_dp_sq = contribs["sigma_rho"] ** 2 + sum(v**2 for v in p_terms.values())
        sigma_dp = math.sqrt(sigma_dp_sq)
        contribs["sigma_rho_p_combined"] = sigma_dp
        sigma_y = base_sum + sigma_dp
    else:
        raise ValueError(f"unknown strategy {strategy!r}")

    f_A = state.f_austenite
    if f_A <= 0:
        sigma_y_corrected = sigma_y
    elif f_A_correction_mode == "rule_of_mix":
        sigma_y_corrected = (1.0 - f_A) * sigma_y + f_A * SIGMA_AUSTENITE_MPA
    elif f_A_correction_mode == "mondière_2025":
        # YS = σ_y_matrix − 68 · γ%, with γ% = f_A · 100
        sigma_y_corrected = max(
            0.0,
            sigma_y - MONDIERE_2025_F_A_SOFTENING_RATE_MPA_PER_PCT * (f_A * 100.0),
        )
    else:
        raise ValueError(f"unknown f_A_correction_mode {f_A_correction_mode!r}")
    return StrengtheningResult(
        sigma_y_MPa=sigma_y,
        sigma_y_austenite_corrected_MPa=sigma_y_corrected,
        contributions_MPa=contribs,
        strategy=strategy,
    )
