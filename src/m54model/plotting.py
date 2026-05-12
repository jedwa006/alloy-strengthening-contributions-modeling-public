"""Plotting helpers for the M54 model.

Designed for use in Jupyter notebooks. Each function takes prediction objects
produced by `m54model.calibration` (AnchorReport, etc.) plus standard library
data and returns a matplotlib Figure for further customization.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
    from matplotlib.figure import Figure

    from m54model.calibration import AnchorReport


# Consistent color per contribution type — matches Wang 2024 Fig. 15 palette
_COLORS = {
    "sigma_0": "#888888",  # grey
    "sigma_ss": "#a6cee3",  # light blue
    "sigma_HP": "#1f78b4",  # blue
    "sigma_rho": "#b2df8a",  # light green
    "sigma_intr": "#fdbf6f",  # orange
    "sigma_M2C": "#e31a1c",  # red
    "sigma_MC": "#fb9a99",  # light red
    "sigma_NiAl": "#cab2d6",  # purple
}
_LABELS = {
    "sigma_0": r"$\sigma_0$ (friction)",
    "sigma_ss": r"$\sigma_{ss}$ (Fleischer)",
    "sigma_HP": r"$\sigma_{HP}$ (block)",
    "sigma_rho": r"$\sigma_\rho$ (dislocation)",
    "sigma_intr": r"$\sigma_{intr}$ (Bain + lath)",
    "sigma_M2C": r"$\sigma_{M_2C}$ (Orowan)",
    "sigma_MC": r"$\sigma_{MC}$ (Orowan)",
    "sigma_NiAl": r"$\sigma_{NiAl}$",
}


def plot_contributions(
    reports: Sequence[AnchorReport],
    *,
    show_anchor: bool = True,
    figsize: tuple[float, float] = (10, 5),
) -> Figure:
    """Stacked-bar plot of YS contributions for each anchor (Wang Fig. 15 style).

    Each anchor is one bar; stacked segments are the named contributions in
    `reports[i].contributions_MPa`. If `show_anchor`, draws a black tick mark
    at the measured YS for direct comparison.
    """
    fig, ax = plt.subplots(figsize=figsize)
    n = len(reports)
    x = np.arange(n)
    width = 0.6

    # Discover all keys, then sort by display order from _COLORS
    all_keys: list[str] = []
    for r in reports:
        for k in r.contributions_MPa:
            if k not in all_keys and k in _COLORS:
                all_keys.append(k)
    ordered = [k for k in _COLORS if k in all_keys]

    bottoms = np.zeros(n)
    for key in ordered:
        heights = np.array([r.contributions_MPa.get(key, 0.0) for r in reports])
        ax.bar(x, heights, width, bottom=bottoms, label=_LABELS[key], color=_COLORS[key])
        bottoms += heights

    if show_anchor:
        ax.scatter(
            x,
            [r.measured_YS_MPa for r in reports],
            marker="_",
            color="black",
            s=600,
            linewidths=2.5,
            zorder=5,
            label="measured YS",
        )

    # Annotate predicted total above each bar
    for i, r in enumerate(reports):
        ax.text(
            i,
            bottoms[i] + 30,
            f"{r.predicted_YS_MPa:.0f}\n({r.miss_pct:+.1f} %)",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(
        [r.anchor_label.replace(" (", "\n(") for r in reports],
        fontsize=9,
    )
    ax.set_ylabel("Yield strength contribution (MPa)")
    ax.set_title("Strengthening contributions vs Sun 2022 anchors")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=9)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    return fig


def plot_anchor_dashboard(
    reports: Sequence[AnchorReport],
    *,
    figsize: tuple[float, float] = (8, 4),
) -> Figure:
    """Side-by-side bars: predicted vs measured for each anchor."""
    fig, ax = plt.subplots(figsize=figsize)
    n = len(reports)
    x = np.arange(n)
    width = 0.35

    pred = np.array([r.predicted_YS_MPa for r in reports])
    meas = np.array([r.measured_YS_MPa for r in reports])
    colors_pred = ["#1f78b4" if r.passes_calibration else "#e31a1c" for r in reports]

    ax.bar(x - width / 2, meas, width, label="measured (Sun 2022)", color="#888888")
    ax.bar(x + width / 2, pred, width, label="model prediction", color=colors_pred)

    for i, r in enumerate(reports):
        ax.text(
            i + width / 2,
            r.predicted_YS_MPa + 25,
            f"{r.miss_pct:+.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#1f78b4" if r.passes_calibration else "#e31a1c",
            fontweight="bold",
        )

    ax.axhline(0, color="black", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(
        [r.anchor_label.replace(" (", "\n(") for r in reports],
        fontsize=9,
    )
    ax.set_ylabel("Yield strength (MPa)")
    ax.set_title("Calibration anchors — predicted vs measured")
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    ax.set_ylim(0, max(pred.max(), meas.max()) * 1.15)
    fig.tight_layout()
    return fig


def plot_tempering_sweep(
    sigma_y_curves: dict[float, tuple[Sequence[float], Sequence[float]]],
    *,
    title: str = "Tempering sweep",
    anchor_t_h: float | None = None,
    anchor_y_MPa: float | None = None,
    figsize: tuple[float, float] = (8, 5),
) -> Figure:
    """Plot YS vs tempering time for one or more temperatures.

    `sigma_y_curves` is a dict {T_celsius: (t_hours_array, ys_MPa_array)}.
    If anchor_t_h and anchor_y_MPa are supplied, marks the experimental anchor.
    """
    fig, ax = plt.subplots(figsize=figsize)
    cmap = plt.get_cmap("viridis")
    Ts = sorted(sigma_y_curves)
    for i, T in enumerate(Ts):
        t_h, ys = sigma_y_curves[T]
        ax.plot(
            t_h, ys, "-o", color=cmap(i / max(1, len(Ts) - 1)), label=f"{T:.0f} °C", markersize=4
        )
    if anchor_t_h is not None and anchor_y_MPa is not None:
        ax.scatter(
            [anchor_t_h],
            [anchor_y_MPa],
            marker="*",
            color="red",
            s=200,
            zorder=5,
            label=f"anchor ({anchor_y_MPa:.0f} MPa)",
        )
    ax.set_xscale("log")
    ax.set_xlabel("Temper time (h)")
    ax.set_ylabel("Predicted YS (MPa)")
    ax.set_title(title)
    ax.legend(fontsize=9)
    ax.grid(True, which="both", linestyle=":", alpha=0.5)
    fig.tight_layout()
    return fig
