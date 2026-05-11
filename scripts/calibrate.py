"""Run calibration sweeps over Sun 2022 anchors and print a comparison table.

Usage:
    uv run python scripts/calibrate.py
"""

from __future__ import annotations

from m54model.alloys.ferrium_m54 import (
    SUN_2022_AF550_45,
    SUN_2022_DQ,
    SUN_2022_DQ_T516_10,
)
from m54model.calibration import (
    evaluate_against_anchor,
    sun_2022_af550_45,
    sun_2022_dq,
    sun_2022_dq_t516_10,
)
from m54model.calibration.sweep import find_beta_c_for_target, sweep_beta_c
from m54model.constants import Convention


def header(text: str) -> None:
    print()
    print("=" * 78)
    print(f" {text}")
    print("=" * 78)


def main() -> None:
    header("Baseline (Sun convention, linear sum, default Fleischer placeholders)")
    for state_factory, anchor in [
        (sun_2022_dq, SUN_2022_DQ),
        (sun_2022_dq_t516_10, SUN_2022_DQ_T516_10),
        (sun_2022_af550_45, SUN_2022_AF550_45),
    ]:
        report = evaluate_against_anchor(state_factory(), anchor)
        print(report)

    header("Strategy comparison: linear vs pythagorean_dp on DQ + T516/10")
    for strat in ("linear", "pythagorean_p", "pythagorean_dp"):
        report = evaluate_against_anchor(sun_2022_dq_t516_10(), SUN_2022_DQ_T516_10, strategy=strat)
        print(report)

    header("Convention comparison: Sun vs Wang on DQ + T516/10 (linear)")
    for conv in (Convention.SUN, Convention.WANG):
        report = evaluate_against_anchor(
            sun_2022_dq_t516_10(), SUN_2022_DQ_T516_10, convention=conv
        )
        print(report)

    header("β_C sweep on DQ anchor (linear, Sun convention)")
    for r in sweep_beta_c(sun_2022_dq(), SUN_2022_DQ):
        bc = r.contributions_MPa  # placeholder access — beta value not stored
        print(r)

    header("β_C bisection: find value that nails DQ anchor exactly")
    bc, report = find_beta_c_for_target(sun_2022_dq(), SUN_2022_DQ)
    print(f"  β_C = {bc:.0f} MPa → {report}")

    header("With calibrated β_C, re-test DQ + T516/10 under each strategy")
    for strat in ("linear", "pythagorean_p", "pythagorean_dp"):
        report = evaluate_against_anchor(
            sun_2022_dq_t516_10(),
            SUN_2022_DQ_T516_10,
            strategy=strat,
            beta_overrides={"C": bc},
        )
        print(report)


if __name__ == "__main__":
    main()
