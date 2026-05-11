# alloy-strengthening-contributions-modeling

Quantitative strengthening + toughening model for **Ferrium® M54®** secondary-hardening UHSS, calibrated against four microstructural states: mill-anneal, direct-quench, direct-quench + temper, and ausformed + temper.

## Status

Phase 0 — literature foundation complete (73/73 papers locally indexed). Phase 1 — strengthening core — in planning. See [`docs/MODEL_PLAN.md`](docs/MODEL_PLAN.md) for the full architecture and phasing plan.

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
m54model/                      [Phase 1+] Python package — TBD
notebooks/                     [Phase 1+] Jupyter walkthroughs — TBD
scripts/                       [Phase 1+] Reproducibility runners — TBD
tests/                         [Phase 1+] Unit + integration tests — TBD
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
