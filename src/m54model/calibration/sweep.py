"""Calibration utilities — compare predictions to anchors and sweep parameters."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from m54model.alloys.ferrium_m54 import CommercialReference
from m54model.constants import (
    Convention,
    StrengtheningConstants,
    SummationStrategy,
)
from m54model.states import MicrostructuralState
from m54model.strengthening import assemble_yield_strength


@dataclass(frozen=True)
class AnchorReport:
    """Result of comparing one prediction to one anchor."""

    anchor_label: str
    measured_YS_MPa: float
    predicted_YS_MPa: float
    miss_MPa: float
    miss_pct: float
    strategy: SummationStrategy
    convention: Convention
    contributions_MPa: dict[str, float]

    @property
    def passes_calibration(self) -> bool:
        """Within ±5 % per MODEL_PLAN.md §6."""
        return abs(self.miss_pct) <= 5.0

    def __repr__(self) -> str:
        ok = "PASS" if self.passes_calibration else "FAIL"
        return (
            f"[{ok}] {self.anchor_label}: predicted {self.predicted_YS_MPa:.0f} MPa "
            f"vs measured {self.measured_YS_MPa:.0f} (miss {self.miss_MPa:+.0f}, "
            f"{self.miss_pct:+.1f} %) — {self.strategy} / {self.convention}"
        )


def evaluate_against_anchor(
    state: MicrostructuralState,
    anchor: CommercialReference,
    *,
    convention: Convention = Convention.SUN,
    strategy: SummationStrategy = "linear",
    beta_overrides: dict[str, float] | None = None,
) -> AnchorReport:
    """Predict YS for `state` and compare to `anchor.YS_MPa`."""
    constants = StrengtheningConstants.from_convention(convention)
    result = assemble_yield_strength(
        state,
        constants=constants,
        strategy=strategy,
        beta_overrides=beta_overrides,
    )
    miss_MPa = result.sigma_y_MPa - anchor.YS_MPa
    miss_pct = 100.0 * miss_MPa / anchor.YS_MPa
    return AnchorReport(
        anchor_label=anchor.label,
        measured_YS_MPa=anchor.YS_MPa,
        predicted_YS_MPa=result.sigma_y_MPa,
        miss_MPa=miss_MPa,
        miss_pct=miss_pct,
        strategy=strategy,
        convention=convention,
        contributions_MPa=result.contributions_MPa,
    )


def sweep_beta_c(
    state: MicrostructuralState,
    anchor: CommercialReference,
    *,
    beta_c_values: Iterable[float] = (1500, 1600, 1700, 1722, 1800, 1900, 2000),
    convention: Convention = Convention.SUN,
    strategy: SummationStrategy = "linear",
) -> list[AnchorReport]:
    """Sweep beta_C and report YS prediction at each."""
    return [
        evaluate_against_anchor(
            state,
            anchor,
            convention=convention,
            strategy=strategy,
            beta_overrides={"C": float(beta_c)},
        )
        for beta_c in beta_c_values
    ]


def best_beta_c(reports: Iterable[AnchorReport]) -> float | None:
    """Return the beta_C that minimises |miss_pct|."""
    best = min(reports, key=lambda r: abs(r.miss_pct))
    return best.contributions_MPa.get("_beta_c") or None  # not stored — find by label


def find_beta_c_for_target(
    state: MicrostructuralState,
    anchor: CommercialReference,
    *,
    convention: Convention = Convention.SUN,
    strategy: SummationStrategy = "linear",
    bracket: tuple[float, float] = (1000.0, 3000.0),
    tol_MPa: float = 1.0,
    max_iter: int = 50,
) -> tuple[float, AnchorReport]:
    """Bisection search for the beta_C that nails `anchor.YS_MPa` within tol_MPa."""
    lo, hi = bracket
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        report = evaluate_against_anchor(
            state,
            anchor,
            convention=convention,
            strategy=strategy,
            beta_overrides={"C": mid},
        )
        if abs(report.miss_MPa) <= tol_MPa:
            return mid, report
        if report.miss_MPa > 0:
            hi = mid  # over-predict: lower beta_C
        else:
            lo = mid  # under-predict: raise beta_C
    return mid, report
