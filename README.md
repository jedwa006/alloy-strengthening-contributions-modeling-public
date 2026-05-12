# alloy-strengthening-contributions-modeling

Quantitative strengthening + toughening model for **Ferrium® M54®** secondary-hardening UHSS, calibrated against four microstructural states: mill-anneal, direct-quench, direct-quench + temper, and ausformed + temper.

> **Last updated:** 2026-05-12 — Phase 3.6f: sub-block Hall-Petch term as a baseline-relative increment closes the 60 % CR gap to **+1 %** (1923 vs 1900 ± 50 MPa) at K<sub>sub</sub> ≈ 150 MPa·µm<sup>½</sup>, **without disturbing the 0 % CR baseline** (+9 % bias unchanged). Sub-block HP is the right knob for cw-induced strengthening; SSD multiplier (Phase 3.6e) was the wrong knob. The +9 % baseline residual is a separate issue — likely cross-rolled prior history or σ<sub>p</sub>(M2C) calibration; deferred to Phase 3.6h+. Up next: Phase 3.6c HRR-J refinement of K<sub>IC</sub> spatial integration.

## Status

Phase 2 complete — all four Sun 2022 calibration anchors PASS within ±5 %. Phase 3 v1 (TRIP submodel equations + M54 cw/cr data) complete; Phase 3.5 (crack-tip K<sub>IC</sub> integration) is next.

| Anchor | Predicted | Measured | Miss | Status |
|--------|----------:|---------:|-----:|--------|
| DQ                  | 1419 | 1420 | -0.1 % | ✓ PASS |
| DQ + T516/10        | 1675 | 1762 | -4.9 % | ✓ PASS |
| AF550/45            | 1864 | 1830 | +1.9 % | ✓ PASS |
| AF550/45 + T425/10  | 1748 | 1726 | +1.3 % | ✓ PASS |

See [`docs/MODEL_PLAN.md`](docs/MODEL_PLAN.md) for the full architecture and
[`docs/FINDINGS.md`](docs/FINDINGS.md) for the running insights log.

## Interactive notebooks (browse-without-cloning)

GitHub renders these directly in the browser — no clone, no install, no account needed. Plots and tables are pre-executed.

- 📊 **[`notebooks/01_introduction.ipynb`](notebooks/01_introduction.ipynb)** — Model walkthrough: composition → state → prediction. Stacked-bar contribution decomposition (Wang Fig. 15 style), predicted-vs-measured anchor dashboard, DQ vs AF tempering sweeps, M2C population evolution, K<sub>HP</sub> sensitivity.
- 🔄 **[`notebooks/02_trip_toughening.ipynb`](notebooks/02_trip_toughening.ipynb)** — TRIP submodel: Patel-Cohen 1953 (Fig. 1 reproduction) + Olson-Cohen 1975 (Angel 304 SS sigmoidal family) + the M54 ASTAR cw/cr austenite data with the non-monotonic finding visualized.
- 💥 **[`notebooks/03_crack_tip_kic.ipynb`](notebooks/03_crack_tip_kic.ipynb)** — Crack-tip K<sub>IC</sub> integration via McMeeking-Evans 1982 transformation toughening. Predicts ΔK<sub>TRIP</sub> for each calibrated state, solves for the matrix-toughness needed to land at Mondière's K<sub>IC</sub> = 110 MPa·m<sup>½</sup>, and shows the f<sub>A</sub> sweep that bounds where TRIP becomes a primary toughening mechanism (~25 % austenite — much higher than M54's 1-3 %).

For deeper reading, [`docs/FINDINGS.md`](docs/FINDINGS.md) is the running log of model insights, calibration choices, and known biases.

## Architecture compatibility

Built and tested on **Apple Silicon (M-series) macOS** with Python 3.12 via `uv`. The dependency stack (NumPy, SciPy, pandas, pydantic, pint, matplotlib, jupyterlab) is all pure-Python or has wheels for the major platforms (Linux x86_64/arm64, macOS Intel/ARM, Windows x86_64), so the Quickstart below should work elsewhere too. If `uv sync` fails on a different architecture, it's most likely a SciPy or matplotlib wheel mismatch — usually fixable by upgrading uv or pinning a slightly older version of the offending package.

## Quickstart (for local development)

```bash
git clone https://github.com/jedwa006/alloy-strengthening-contributions-modeling-public.git
cd alloy-strengthening-contributions-modeling-public
uv sync --extra dev               # one-time: install Python 3.12, deps, jupyter
uv run pytest                     # run all tests
uv run python scripts/calibrate.py   # CLI calibration sweep
uv run jupyter lab notebooks/     # launch the walkthrough notebook
```

Notebooks are built from `scripts/build_walkthrough_notebook.py` and `scripts/build_trip_notebook.py`; re-generate with:

```bash
uv run python scripts/build_walkthrough_notebook.py
uv run python scripts/build_trip_notebook.py
```

## Layout

```
docs/                          Architecture & planning docs
├── MODEL_PLAN.md              The canonical plan v1
├── FINDINGS.md                Living log of insights vs source literature
└── PUBLIC_MIRROR_SETUP.md     One-time setup for the public mirror
index/                         Per-paper indexes (figures, equations, takeaways)
├── main-article-index.md      Zhu 2025 (the dual-precipitation paper)
├── sun-2022-index.md          Sun 2022 (M54 ausforming + tempering)
├── trip-foundations-index.md  Patel-Cohen 1953 + Olson-Cohen 1975
└── cited-by-summaries.md      The five papers citing Zhu 2025
references/                    Bibliography
├── references.bib             73-entry BibTeX with file= paths to local PDFs
├── citation-chart.md          Annotated chart with errata + retrieval routes
└── README.md                  How to import into Zotero
reference docs/                User-supplied source PDFs (private repo only)
└── Articles that CITE main article/   The 5 cited-by papers
pdf-archive/                   PDFs gathered for the bibliography (private only)
└── MANIFEST.md                Per-PDF provenance (synced to public)
data/                          Experimental data
├── README.md                   Folder structure + which subfolders are private
├── xrd/experimental/           Raw XRD spectra workbooks (private)
├── nanoindentation/experimental/  H + Er depth profiles (private)
└── tensile/experimental/       Stress-strain curves + K_IC outputs (private)
src/m54model/                  Python package — alloy/state/precipitate
                                dataclasses, kinetics, strengthening,
                                calibration anchors, plotting helpers
notebooks/                     Jupyter walkthroughs (interactive)
scripts/                       Reproducibility runners + notebook builders
tests/                         Unit + integration tests (pytest)
```

## Working with this repo

### Branching

`main` is stable. All work is on topic branches merged via `--no-ff`:
- `research/<topic>` — literature, indexing, calibration anchors
- `feat/<scope>-<name>` — features (e.g. `feat/model-strengthening-core`)
- `fix/<name>` — bug fixes
- `chore/<name>` — tooling, deps, cleanup
- `docs/<name>` — documentation-only

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `research:`, `chore:`, `docs:`).

### Binary handling

`.gitattributes` marks PDFs and other binary file types as opaque — no text-diff, no merge attempt. The `pdf-archive/` and `reference docs/` folders are tracked normally on the private repo; if the repo grows past ~1 GB we can migrate to Git LFS without losing history.

### Public mirror

The private repo auto-syncs a filtered copy to a public mirror on every push to `main`. Literature PDFs and raw experimental data are excluded from the mirror but their MANIFEST/index files are kept. See [`docs/PUBLIC_MIRROR_SETUP.md`](docs/PUBLIC_MIRROR_SETUP.md) for the setup.

## License

[MIT](LICENSE) — permissive, compatible with the open-source dependencies we plan to use (NumPy, SciPy, pandas, matplotlib, pydantic, pint, optionally PyCalphad / Streamlit).
