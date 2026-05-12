# Experimental Data

Raw experimental measurements that the model consumes for calibration and
validation. Organized by data-collection technique.

## Layout

```
data/
├── xrd/
│   └── experimental/         Raw XRD spectra workbooks (private)
├── nanoindentation/
│   └── experimental/         H + Er depth profiles (private)
└── tensile/
    └── experimental/         Stress-strain curves + Charpy/K_IC outputs (private)
```

Other planned subfolders (when relevant data lands):
- `data/xrd/derived/`         Processed / fitted spectra, peak tables (synced)
- `data/astar/`               ASTAR phase-fraction + GND maps (raw vs derived split TBD)
- `data/hardness/`            HV / HRC measurements

## Public-mirror policy

Like `pdf-archive/` and `reference docs/`, certain subfolders here are
**excluded from the public mirror** because they are large raw source files
of the user's experimental work. Specifically:

- `data/xrd/experimental/`             — excluded
- `data/nanoindentation/experimental/` — excluded
- `data/tensile/experimental/`         — excluded

Derived analyses, plots, summary tables, and code that **uses** the data
ARE synced to the public mirror. Just not the raw source files.

If you add new raw-data subfolders, update the exclusion list in
[`scripts/build_public_mirror.sh`](../scripts/build_public_mirror.sh) and
note the addition here.

## XRD source files

The current `data/xrd/experimental/` (when populated) holds:

- `M54_MoXRD_ConvertedToCuSpectrum_Workbook_0p20p40p60p.xlsx` — Cu-equivalent
  XRD spectra at 0/20/40/60 % CR, all conditions in one workbook
- `M54_MoXRD-TotalScattering (High Res)_ConvertedToCuSpectrum_Workbook_0p.xlsx`
  — high-resolution total-scattering data at 0 % CR (PDF-analysis source)
- `M54_MoXRD-TotalScattering (High Res)_ConvertedToCuSpectrum_Workbook_6p.xlsx`
  — same at 60 % CR
- `Stacked HR-XRD (Mo-Source) Ferrium M54 from Pair Distribution Fxn.pdf` —
  stacked HR-XRD plot from PDF analysis
- `Stacked XRD (Mo-Source) Ferrium M54.pdf` — stacked Mo-source XRD plot

These are used (or planned for use) in:

- **Phase 3.6** (competing-mechanism austenite model): bulk phase-fraction
  validation vs ASTAR's small-n statistics; M54-specific γ and α′ lattice
  parameters → real Bain transformation strains for Patel-Cohen reverse-
  transformation under cold-rolling compression.
- **Phase 3.7+**: PDF-derived local short-range order to test the cellular
  shear-band-network hypothesis at the atomic scale.
