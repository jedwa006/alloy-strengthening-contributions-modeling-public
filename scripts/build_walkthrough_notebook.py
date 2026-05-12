"""Generate notebooks/01_introduction.ipynb from this script.

The notebook is a build artifact. To re-generate:
    uv run python scripts/build_walkthrough_notebook.py

Edit cell content here, not the .ipynb directly — the .ipynb gets
overwritten on next run.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


def md(*lines: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell("\n".join(lines))


def code(*lines: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell("\n".join(lines))


CELLS: list[nbf.NotebookNode] = [
    md(
        "# M54 Strengthening Model — Interactive Walkthrough",
        "",
        "Quick tour of the model, calibrated against four Sun 2022 anchors. After running",
        "this notebook end-to-end you'll have:",
        "",
        "- a feel for the API (alloy → state → prediction),",
        "- per-contribution decomposition for each calibration anchor,",
        "- tempering parameter sweeps,",
        "- a comparison of the DQ vs AF processing routes at the same temper.",
        "",
        "See [`docs/MODEL_PLAN.md`](../docs/MODEL_PLAN.md) for the full architecture and",
        "[`docs/FINDINGS.md`](../docs/FINDINGS.md) for the running list of insights.",
    ),
    md("## 0. Setup"),
    code(
        "import numpy as np",
        "import matplotlib.pyplot as plt",
        "",
        "from m54model import FERRIUM_M54, MicrostructuralState, assemble_yield_strength",
        "from m54model.alloys.ferrium_m54 import (",
        "    SUN_2022_DQ, SUN_2022_DQ_T516_10, SUN_2022_AF550_45, SUN_2022_AF550_45_T425_10,",
        ")",
        "from m54model.calibration import (",
        "    sun_2022_dq, sun_2022_dq_t516_10, sun_2022_af550_45, sun_2022_af550_45_t425_10,",
        "    evaluate_against_anchor,",
        ")",
        "from m54model.kinetics import m2c_population_dq_tempered, m2c_population_af_tempered",
        "from m54model.plotting import plot_contributions, plot_anchor_dashboard, plot_tempering_sweep",
        "",
        "%matplotlib inline",
        "plt.rcParams['figure.dpi'] = 110",
    ),
    md(
        "## 1. The alloy",
        "",
        "Ferrium M54 composition is a frozen `Composition` dataclass. Everything is",
        "derived from this — at% conversion, Fleischer-eligible elements, etc.",
    ),
    code(
        "print(f'Name: {FERRIUM_M54.name}')",
        "print(f'wt%:  {FERRIUM_M54.wt_pct_full}')",
        "print()",
        "print('at%:')",
        "for elem, x in sorted(FERRIUM_M54.at_pct().items(), key=lambda kv: -kv[1]):",
        "    print(f'  {elem:3s}  {x:6.3f}')",
    ),
    md(
        "## 2. The four Sun 2022 calibration anchors",
        "",
        "Each anchor pairs a `MicrostructuralState` (built from Sun 2022's measured",
        "block / dislocation density / etc.) with the measured YS to compare against.",
    ),
    code(
        "anchors = [",
        "    (sun_2022_dq(),                SUN_2022_DQ),",
        "    (sun_2022_dq_t516_10(),        SUN_2022_DQ_T516_10),",
        "    (sun_2022_af550_45(),          SUN_2022_AF550_45),",
        "    (sun_2022_af550_45_t425_10(),  SUN_2022_AF550_45_T425_10),",
        "]",
        "reports = [evaluate_against_anchor(state, anchor) for state, anchor in anchors]",
        "for r in reports:",
        "    print(r)",
    ),
    md(
        "## 3. Contribution decomposition (Wang Fig. 15 style)",
        "",
        "Stacked-bar showing which strengthening source contributes how much per anchor.",
        "Black tick marks the measured YS; bar height is the predicted total; annotation",
        "shows miss%.",
    ),
    code("fig = plot_contributions(reports)\nplt.show()"),
    md(
        "## 4. Predicted vs measured at a glance",
        "",
        "Side-by-side bars show the model passes all four anchors within ±5%.",
        "Failed anchors would render in red.",
    ),
    code("fig = plot_anchor_dashboard(reports)\nplt.show()"),
    md(
        "## 5. Decomposition table (numerical)",
        "",
        "Same data as the stacked bar, but tabular.",
    ),
    code(
        "import pandas as pd",
        "rows = []",
        "for r in reports:",
        "    row = {'Anchor': r.anchor_label, 'Measured': r.measured_YS_MPa, 'Predicted': r.predicted_YS_MPa, 'Miss%': r.miss_pct}",
        "    row.update({k: round(v, 1) for k, v in r.contributions_MPa.items()})",
        "    rows.append(row)",
        "pd.DataFrame(rows).set_index('Anchor').T",
    ),
    md(
        "## 6. Tempering sweep — DQ + tempering at varying T, t",
        "",
        "What does the model predict if we vary tempering temperature and time, holding",
        "the rest of the DQ microstructure fixed? This shows the precipitation-strengthening",
        "engagement curve. The red star marks the Sun 2022 anchor (516 °C / 10 h) for",
        "reference.",
    ),
    code(
        "from m54model.calibration.anchors import _matrix_tempered",
        "",
        "def predict_dq_tempered(T_celsius: float, t_hours: float) -> float:",
        "    base = sun_2022_dq_t516_10()  # block, rho, etc.",
        "    m2c = m2c_population_dq_tempered(T_celsius, t_hours)",
        "    state = MicrostructuralState(",
        "        state='dq_tempered',",
        "        block_width_um=base.block_width_um,",
        "        dislocation_density_per_m2=base.dislocation_density_per_m2,",
        "        f_austenite=0.0,",
        "        matrix_at_frac=base.matrix_at_frac,",
        "        wt_pct_C_in_solution=0.003,",
        "        precipitates=[m2c],",
        "        label=f'DQ + T{T_celsius:.0f}/{t_hours:.1f}',",
        "    )",
        "    return assemble_yield_strength(state).sigma_y_MPa",
        "",
        "t_hours = np.array([0.5, 1, 2, 5, 10, 20, 50, 100])",
        "T_grid = [425.0, 475.0, 516.0]",
        "curves = {T: (t_hours, [predict_dq_tempered(T, t) for t in t_hours]) for T in T_grid}",
        "fig = plot_tempering_sweep(curves, title='DQ tempering — YS vs t', anchor_t_h=10, anchor_y_MPa=1762)",
        "plt.show()",
    ),
    md(
        "## 7. AF vs DQ at the same temper",
        "",
        "Compare the two processing routes at identical temper conditions. The model says",
        "AF beats DQ across the board (because of refined block + ausforming-accelerated M2C).",
        "Sun 2022 measures AF+T (T425/10) at 1726 vs DQ+T (T516/10) at 1762 — the **opposite**",
        "ordering. This is the direction-of-effect bias documented in",
        "[`docs/FINDINGS.md`](../docs/FINDINGS.md) §5 and worth investigating in Phase 2.5.",
    ),
    code(
        "def predict_af_tempered(T_celsius: float, t_hours: float) -> float:",
        "    base = sun_2022_af550_45_t425_10()",
        "    m2c = m2c_population_af_tempered(T_celsius, t_hours)",
        "    state = MicrostructuralState(",
        "        state='af_tempered',",
        "        block_width_um=base.block_width_um,",
        "        dislocation_density_per_m2=base.dislocation_density_per_m2,",
        "        f_austenite=0.0,",
        "        matrix_at_frac=base.matrix_at_frac,",
        "        wt_pct_C_in_solution=0.003,",
        "        precipitates=[m2c],",
        "        label=f'AF + T{T_celsius:.0f}/{t_hours:.1f}',",
        "    )",
        "    return assemble_yield_strength(state).sigma_y_MPa",
        "",
        "T_grid = [425.0, 475.0, 516.0]",
        "fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)",
        "for ax, T in zip(axes[:2], (425.0, 475.0)):",
        "    dq_ys = [predict_dq_tempered(T, t) for t in t_hours]",
        "    af_ys = [predict_af_tempered(T, t) for t in t_hours]",
        "    ax.plot(t_hours, dq_ys, '-o', label='DQ + T', color='#1f78b4')",
        "    ax.plot(t_hours, af_ys, '-s', label='AF + T', color='#e31a1c')",
        "    ax.set_xscale('log')",
        "    ax.set_xlabel('Temper time (h)')",
        "    ax.set_title(f'Temper at {T:.0f} °C')",
        "    ax.grid(True, which='both', linestyle=':', alpha=0.5)",
        "    ax.legend()",
        "axes[0].set_ylabel('Predicted YS (MPa)')",
        "fig.suptitle('Direction-of-effect: model says AF > DQ; experiment says AF < DQ at peak')",
        "fig.tight_layout()",
        "plt.show()",
    ),
    md(
        "## 8. M2C population evolution",
        "",
        "How the M2C precipitate population changes with temper time at 425 °C, comparing",
        "DQ vs AF kinetics. AF state has lower nucleation activation energy (137 vs",
        "407 kJ/mol per Cho 2015) so it reaches saturation V_f much faster.",
    ),
    code(
        "t_log = np.logspace(np.log10(0.1), np.log10(100), 40)",
        "T = 425.0",
        "dq_pops = [m2c_population_dq_tempered(T, t) for t in t_log]",
        "af_pops = [m2c_population_af_tempered(T, t) for t in t_log]",
        "",
        "fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))",
        "axes[0].plot(t_log, [p.volume_fraction for p in dq_pops], '-', label='DQ', color='#1f78b4')",
        "axes[0].plot(t_log, [p.volume_fraction for p in af_pops], '-', label='AF', color='#e31a1c')",
        "axes[0].set_xscale('log'); axes[0].set_yscale('log')",
        "axes[0].set_xlabel('t (h)'); axes[0].set_ylabel('M2C volume fraction')",
        "axes[0].set_title('V_f(t) at 425 °C'); axes[0].legend(); axes[0].grid(True, which='both', alpha=0.4)",
        "",
        "axes[1].plot(t_log, [p.equivalent_radius_nm or 0 for p in dq_pops], '-', label='DQ', color='#1f78b4')",
        "axes[1].plot(t_log, [p.equivalent_radius_nm or 0 for p in af_pops], '-', label='AF', color='#e31a1c')",
        "axes[1].set_xscale('log'); axes[1].set_xlabel('t (h)'); axes[1].set_ylabel('M2C r_eq (nm)')",
        "axes[1].set_title('r(t) at 425 °C'); axes[1].legend(); axes[1].grid(True, which='both', alpha=0.4)",
        "",
        "axes[2].plot(t_log, [p.spacing_nm or 0 for p in dq_pops], '-', label='DQ', color='#1f78b4')",
        "axes[2].plot(t_log, [p.spacing_nm or 0 for p in af_pops], '-', label='AF', color='#e31a1c')",
        "axes[2].set_xscale('log'); axes[2].set_xlabel('t (h)'); axes[2].set_ylabel('M2C spacing L (nm)')",
        "axes[2].set_title('L(t) at 425 °C'); axes[2].legend(); axes[2].grid(True, which='both', alpha=0.4)",
        "",
        "fig.tight_layout()",
        "plt.show()",
    ),
    md(
        "## 9. Sensitivity analysis — what if K_HP is wrong?",
        "",
        "Sun fits K_HP = 230 MPa·µm^½ on M54; Wang and Zhu use 300 for generic SH steel.",
        "Sweeping over a range to see how DQ+T anchor moves.",
    ),
    code(
        "from m54model.constants import StrengtheningConstants",
        "",
        "K_range = np.linspace(180, 320, 15)",
        "state = sun_2022_dq_t516_10()",
        "predicted = [",
        "    assemble_yield_strength(",
        "        state,",
        "        constants=StrengtheningConstants(M_taylor=2.5, alpha_BH=0.38, K_HP_MPa_um_half=K),",
        "    ).sigma_y_MPa",
        "    for K in K_range",
        "]",
        "",
        "fig, ax = plt.subplots(figsize=(7, 4))",
        "ax.plot(K_range, predicted, '-o', color='#1f78b4')",
        "ax.axhline(SUN_2022_DQ_T516_10.YS_MPa, color='red', linestyle='--',",
        "           label=f'Sun 2022 anchor ({SUN_2022_DQ_T516_10.YS_MPa} MPa)')",
        "ax.axvline(230, color='green', linestyle=':', label='Sun K_HP=230 (default)')",
        "ax.axvline(300, color='orange', linestyle=':', label='Wang/Zhu K_HP=300')",
        "ax.set_xlabel('K_HP (MPa·µm^½)'); ax.set_ylabel('Predicted DQ+T516/10 YS (MPa)')",
        "ax.set_title('Sensitivity of DQ+T anchor to K_HP'); ax.legend(); ax.grid(alpha=0.4)",
        "fig.tight_layout()",
        "plt.show()",
    ),
    md(
        "## 10. Where to go from here",
        "",
        "**Try modifying:**",
        "- The composition in [`src/m54model/alloys/ferrium_m54.py`](../src/m54model/alloys/ferrium_m54.py)",
        "  to model a hypothetical alloy variant.",
        "- Block size or dislocation density in the anchor factories",
        "  ([`src/m54model/calibration/anchors.py`](../src/m54model/calibration/anchors.py))",
        "  to see what microstructural levers move YS most.",
        "- The Fleischer β placeholders in [`src/m54model/constants.py`](../src/m54model/constants.py)",
        "  for W, V, C, Ti — sensitivity is small but not zero.",
        "",
        "**Coming next:**",
        "- Phase 3 — TRIP toughening submodel (Patel-Cohen + Olson-Cohen) calibrated",
        "  against your 0/20/40/60 % cw/cr austenite-content data.",
        "- Phase 2.5 — investigate the AF+T vs DQ+T direction-of-effect bias surfaced",
        "  in cell 7.",
    ),
]


def main() -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = CELLS
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python"},
    }
    out = Path("notebooks/01_introduction.ipynb")
    out.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, out)
    print(f"wrote {out} with {len(CELLS)} cells")


if __name__ == "__main__":
    main()
