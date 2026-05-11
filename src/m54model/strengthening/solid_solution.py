"""Fleischer solid-solution strengthening."""

import math

from m54model.constants import FLEISCHER_BETA_MPA, FLEISCHER_BETA_PLACEHOLDERS_MPA


def sigma_fleischer(
    matrix_at_frac: dict[str, float],
    beta_overrides: dict[str, float] | None = None,
) -> float:
    """sigma_ss = sqrt( sum_i beta_i^2 * x_i ), x in atomic fraction.

    Skips Fe (matrix). Missing beta for an element is fatal unless an override is
    provided — this is intentional, to avoid silently dropping contributions.

    Returns MPa.
    """
    table = dict(FLEISCHER_BETA_MPA)
    table.update(FLEISCHER_BETA_PLACEHOLDERS_MPA)
    if beta_overrides:
        table.update(beta_overrides)

    contributions: list[float] = []
    missing: list[str] = []
    for elem, x in matrix_at_frac.items():
        if elem == "Fe":
            continue
        if x <= 0:
            continue
        beta = table.get(elem)
        if beta is None:
            missing.append(elem)
            continue
        contributions.append(beta * beta * x)

    if missing:
        raise ValueError(f"missing Fleischer beta for {missing}. Provide via beta_overrides.")
    if not contributions:
        return 0.0
    return math.sqrt(sum(contributions))
