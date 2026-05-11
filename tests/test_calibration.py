"""Calibration tests — assert predictions vs Sun 2022 anchors at the ±5 % gate.

Three anchors per MODEL_PLAN.md §6:

1. **DQ (untempered)**       — Sun 2022, YS 1420 MPa  → PASS at -0.1 %
2. **DQ + T516/10**          — Sun 2022, YS 1762 MPa  → PASS at -4.9 %
3. **AF550/45 (untempered)** — Sun 2022, YS 1830 MPa  → PASS at +1.9 %
4. **AF550/45 + T425/10**    — Sun 2022, YS 1726 MPa  → deferred to Phase 2 (needs kinetics)

The DQ and AF (untempered) anchors close cleanly after introducing the
sigma_intrinsic_martensite term (Speich-Leslie / Krauss empirical fit on
wt% C in solid solution). The same K calibrates both DQ and AF without
retuning, which is encouraging.
"""

import pytest

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


def test_dq_passes_within_5pct() -> None:
    report = evaluate_against_anchor(sun_2022_dq(), SUN_2022_DQ)
    assert report.passes_calibration, repr(report)


def test_dq_t516_10_passes_within_5pct() -> None:
    report = evaluate_against_anchor(sun_2022_dq_t516_10(), SUN_2022_DQ_T516_10)
    assert report.passes_calibration, repr(report)


def test_af550_45_passes_within_5pct() -> None:
    report = evaluate_against_anchor(sun_2022_af550_45(), SUN_2022_AF550_45)
    assert report.passes_calibration, repr(report)


def test_intrinsic_term_only_in_untempered_states() -> None:
    """sigma_intr should be > 0 for DQ/AF, == 0 for DQ+T."""
    r_dq = evaluate_against_anchor(sun_2022_dq(), SUN_2022_DQ)
    r_dqt = evaluate_against_anchor(sun_2022_dq_t516_10(), SUN_2022_DQ_T516_10)
    assert r_dq.contributions_MPa["sigma_intr"] > 100  # ~540 MPa for 0.30 wt% C
    assert r_dqt.contributions_MPa["sigma_intr"] == 0.0


def test_strategy_choice_matters_on_tempered() -> None:
    """Linear and pythagorean_dp give different answers when both rho and p>0."""
    r_lin = evaluate_against_anchor(sun_2022_dq_t516_10(), SUN_2022_DQ_T516_10, strategy="linear")
    r_dp = evaluate_against_anchor(
        sun_2022_dq_t516_10(), SUN_2022_DQ_T516_10, strategy="pythagorean_dp"
    )
    assert r_lin.predicted_YS_MPa > r_dp.predicted_YS_MPa


@pytest.mark.skip(reason="AF + T425/10 anchor needs Phase 2 ausforming-tempering kinetics.")
def test_af550_45_t425_10_passes_within_5pct() -> None:
    pass  # Phase 2
