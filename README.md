# alloy-strengthening-contributions-modeling

Quantitative strengthening + toughening model for **Ferrium® M54®** secondary-hardening UHSS, calibrated against four microstructural states: mill-anneal, direct-quench, direct-quench + temper, and ausformed + temper.

## Status

Phase 2 complete — all four Sun 2022 calibration anchors PASS within ±5 %:

| Anchor | Predicted | Measured | Miss |
|--------|----------:|---------:|-----:|
| DQ                  | 1419 | 1420 | -0.1 % |
| DQ + T516/10        | 1675 | 1762 | -4.9 % |
| AF550/45            | 1864 | 1830 | +1.9 % |
| AF550/45 + T425/10  | 1748 | 1726 | +1.3 % |

See [`docs/MODEL_PLAN.md`](docs/MODEL_PLAN.md) for the full architecture and
[`docs/FINDINGS.md`](docs/FINDINGS.md) for the running insights log.

## Quickstart

```bash
uv sync --extra dev               # one-time: install Python 3.12, deps, jupyter
uv run pytest                     # run all tests
uv run python scripts/calibrate.py   # CLI calibration sweep
uv run jupyter lab notebooks/     # launch the walkthrough notebook
```

The interactive walkthrough is at [`notebooks/01_introduction.ipynb`](notebooks/01_introduction.ipynb)
— covers the API, contribution decompositions, tempering parameter sweeps,
and the AF-vs-DQ direction-of-effect bias. The notebook is built from
[`scripts/build_walkthrough_notebook.py`](scripts/build_walkthrough_notebook.py); re-generate
with `uv run python scripts/build_walkthrough_notebook.py`.

## Layout

```
docs/                          Architecture & planning docs
├── MODEL_PLAN.md              The canonical plan v1
index/                         Per-paper indexes (figures, equations, takeaways)
├── main-article-index.md      Zhu 2025 (the dual-precipitation paper)
├── sun-2022-index.md          Sun 2022 (M54 ausforming + tempering)
├── trip-foundations-index.md  Patel-Cohen 1953 + Olson-Cohen 1975
└── cited-by-summaries.md      The five papers citing Zhu 2025
references/                    Bibliography
├── references.bib             73-entry BibTeX with file= paths to local PDFs
├── citation-chart.md          Annotated chart with errata + retrieval routes
└── README.md                  How to import into Zotero
reference docs/                User-supplied source PDFs
└── Articles that CITE main article/   The 5 cited-by papers
pdf-archive/                   PDFs gathered for the bibliography (~390 MB)
└── MANIFEST.md                Per-PDF provenance
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

`.gitattributes` marks PDFs and other binary file types as opaque — no text-diff, no merge attempt. The `pdf-archive/` and `reference docs/` folders are tracked normally; if the repo grows past ~1 GB we can migrate to Git LFS without losing history.

## License

[MIT](LICENSE) — permissive, compatible with the open-source dependencies we plan to use (NumPy, SciPy, pandas, matplotlib, pydantic, pint, optionally PyCalphad / Streamlit).
