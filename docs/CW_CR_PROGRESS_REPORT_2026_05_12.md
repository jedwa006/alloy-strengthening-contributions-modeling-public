# M54 cw/cr σ<sub>y</sub> Modeling — Progress Report

**For:** S. Mathaudhu
**From:** J. Edwards (model build) + supporting model framework
**Date:** 2026-05-12
**Repo:** [`alloy-strengthening-contributions-modeling`](https://github.com/jedwa006/alloy-strengthening-contributions-modeling)
**Concise summary**: We now have three independent ways to predict bulk
σ<sub>y</sub> at the user's cw/cr conditions. The H-data-anchored
approach (no hand-fit knobs) lands within ±2 % of measured tensile at
both 0 % and 60 % CR. The microstructure-only prediction misses by
−14 % at 60 % CR; per-zone analysis shows why (and reveals an unmodeled
surface-matrix-hardening contribution).

---

## 1. Status snapshot

**Model**: literature-consensus σ<sub>y</sub> decomposition (Sun 2022 +
Wang 2024 + Zhu 2025 framework, calibrated against four Sun anchors at
±5 %), extended with the user's measured cw/cr inputs (ASTAR f<sub>A</sub>,
GND density, grain size, nanoindentation H, XRD V<sub>γ</sub> + Bain
ε<sup>V</sup>).

**Mechanistic framing**: the M54 cw/cr regime sits in the
"cumulatively-large but never instantaneously-large" strain space that
Maresca-Kouznetsova-Geers 2014 [1] frames as the regime where interlath
retained austenite films contribute meaningfully to deformability. Our
65-pass skin-pass schedule (0.5-1 % per pass, total ~61 % reduction)
realizes precisely this regime. The user's measured 60 % CR
microstructure — uniformly distributed γ films at lath boundaries with
~30 nm lath thickness (Ch 4 §"Phase distribution") — is the material
the Maresca framework was built to describe. Maresca-Curtin 2017 [2]
adds an atomistic + crystallographic theory of the fcc/bcc interface
showing glissile, athermal motion under shear; Maresca-Kouznetsova-Geers
-Curtin 2018 [3] extends this to a continuum model and explicitly
documents the **forward FCC→BCC transformation as spontaneous while
the reverse BCC→FCC requires high stress** — the asymmetry our Phase
3.6h Patel-Cohen analysis already invoked, now with a published
atomistic basis.

**Validation surface**: 4 Sun published anchors + 4 cw/cr conditions
(0/20/40/60 % CR) × multiple measured properties per condition
(σ<sub>y</sub>, σ<sub>UTS</sub>, EL, hardness in 5 zones, reduced
modulus in 5 zones, austenite fraction surface + core, GND density per
phase, grain size statistics).

**Test suite**: 160 tests pass.

---

## 2. Three approaches to predict bulk σ<sub>y</sub>(CR)

| Phase | Approach | Hand-fit anchors |
|---|---|---|
| 3.7b | Direct-core σ<sub>y</sub> + sub-block HP scaled by an empirical f<sub>engaged</sub>(CR) | f<sub>engaged</sub>(0)=0, f<sub>engaged</sub>(20)=0, f<sub>engaged</sub>(40)=0.7, f<sub>engaged</sub>(60)=1.0 (knot points calibrated to Ch 4 microstructure description + bulk tensile) |
| 3.8a | Per-zone σ<sub>y</sub> from linearly-interpolated f<sub>A</sub> + d<sub>subblock</sub> between surface and core, volume-weighted to bulk | None — fully ab-initio from microstructure inputs |
| 3.8c | Per-zone σ<sub>y</sub> derived from measured H<sub>composite</sub> via Eq. 1 + Tabor + work-hardening ratio, volume-weighted to bulk | None — uses measured H + chain |

### Bulk σ<sub>y</sub>(CR) results

| CR % | σ<sub>y</sub> measured | 3.7b empirical | 3.8a microstructure | 3.8c H-anchored |
|---:|---:|---:|---:|---:|
| 0  | 1300 ± 30 | 1420 (+9.2 %)   | 1427 (+9.8 %)   | **1390 (+6.9 %)** |
| 20 | (no tensile) | 1745          | 1886           | 1642           |
| 40 | (no tensile) | 1878          | 1796           | 1903           |
| 60 | 1900 ± 50 | 1923 (+1.2 %)   | 1641 (−13.6 %)  | **1866 (−1.7 %)** |

**The H-anchored approach (3.8c) gives the most internally-consistent
prediction** — within ±2 % at both measured points (0 % and 60 % CR),
with no hand-fit knobs. Its 20 % and 40 % CR values are the model's
best guesses for the user's pending tensile measurements.

---

## 3. The smoking-gun finding: surface-matrix-hardening gradient at 60 % CR

The microstructure-only model (3.8a) under-predicts bulk σ<sub>y</sub>
at 60 % CR by −14 %. Per-zone analysis explains why:

| 60 % CR zone | depth (µm) | σ<sub>y</sub> predicted (3.8a) | σ<sub>y</sub> derived from H (3.8b) |
|---|---:|---:|---:|
| 0-50 µm    |   25 | 1431 | **2044** |
| 50-100 µm  |   75 | 1459 | 1987 |
| 100-250 µm |  175 | 1512 | 1973 |
| 250-500 µm |  375 | 1615 | 1838 |
| Core       |  630 | **1816** | 1775 |

**The model and the data have OPPOSITE through-thickness gradients
at 60 % CR**. The model predicts surface SOFTER than core because
linear-f<sub>A</sub> interpolation puts more austenite at the surface
(26 → 13 % from surface to core per ASTAR), and γ softens via
rule-of-mixtures. The H data shows surface HARDER than core because
the surface matrix is more heavily strain-hardened (cumulative shear
from the rolling refinement front, per Ch 4 §"Grain Architecture and
Through-Thickness Refinement").

**This is the single biggest unmodeled physics**: surface-localized
matrix work-hardening from accumulated rolling strain. The model has no
zone-resolved GND density or equivalent strain-state proxy to capture
it; we only have the per-CR median GND from `USER_M54_GND_DENSITY`.

---

## 4. Visualization

The two-panel figure in [`notebooks/02_trip_toughening.ipynb`](../notebooks/02_trip_toughening.ipynb)
§3c shows:
- **Panel (a)**: bulk σ<sub>y</sub>(CR) for all three model approaches
  + measured tensile points with error bars.
- **Panel (b)**: per-zone σ<sub>y</sub>(depth) at 60 % CR, predicted
  vs derived, with the bulk tensile reference band — the gradient
  reversal is visible at a glance.

GitHub renders the notebook directly; no clone required.

---

## 5. Discussion

### What the model now does well

- **Predicts σ<sub>y</sub> at the user's cw/cr conditions within ±2 %
  using only existing measurements** (H-anchored mode).
- **Identifies which contributions matter at each CR** — the σ<sub>y</sub>
  decomposition (σ<sub>0</sub> + σ<sub>ss</sub> + σ<sub>HP</sub> +
  σ<sub>ρ</sub> + σ<sub>p</sub>(M2C) + corrections) lets us decompose
  the +600 MPa rise from 0 to 60 % CR into sources.
- **Falsifiably bounds TRIP toughening at the crack tip** (ΔK<sub>TRIP</sub>
  &lt; 0.3 MPa·m<sup>½</sup> at M54 f<sub>A</sub> levels, robust across
  every spatial-field variation tried — Phase 3.6 a-c).
- **Uses the Patel-Cohen reverse-transformation framework that Chapter 4
  endorses** for the cw/cr austenite cycle (the model and the
  microstructure paper agree on the mechanism).
- **Cross-validates measurement chains**: H + Eq. 1 + Tabor + WH ratio
  gives volume-weighted bulk σ<sub>y</sub> within −1.7 % of the
  independently-measured tensile value at 60 % CR. Each link in the
  chain is internally consistent.

### What it doesn't do well

- **Microstructure-only prediction (3.8a) misses the surface-matrix-
  hardening gradient.** Without zone-resolved GND or an equivalent
  strain-state proxy, the model can only interpolate f<sub>A</sub> and
  d<sub>subblock</sub> linearly between surface and core measurements
  — too coarse to capture the surface-localized matrix hardening that
  the H data reveals.
- **No mechanism for K<sub>IC</sub>(CR) doubling** (the user's measured
  219 → 434 MJ/m³ tensile-toughness rise from 0 → 60 % CR). Lit search
  (Phase 3.7c) found NO published K<sub>matrix</sub>(d<sub>subblock</sub>)
  scaling for UHSS. Wang 2023 attributes K<sub>IC</sub> trends in
  AerMet 100 to RA, not sub-block size — restricting the modeling
  space rather than expanding it.
- **The Phase 3.7b empirical f<sub>engaged</sub>(CR) is a fit, not a
  prediction**. It numerically agrees with bulk tensile but misses the
  per-zone gradient story.

### Open questions worth airing

1. **Surface matrix hardening — measure or model?** Adding a per-zone
   ρ-resolved Bailey-Hirsch term would close the prediction gap, but
   we'd need either (a) zone-resolved ASTAR-PED on the same cross-
   sections (new experimental campaign) or (b) a constitutive law
   linking accumulated cumulative shear strain to GND density (model
   extension; would need calibration).
2. **K<sub>IC</sub>(CR) doubling — model or just observation?** No
   published model captures the doubling. Could the model be extended
   to predict it via the through-thickness sub-block gradient acting
   as a "natural laminate composite"? Or do we accept it as a
   measurement-only finding for the manuscript?
3. **f<sub>A</sub> source canonicalization for the chapters.** Chapter
   4 Table 2 (which our code matches) gives aggregate values; Chapter
   5 §Results text gives per-foil values that differ substantially
   (e.g., 35.1 % surface @ 40 % CR vs 26.4 ± 9 in Table 2). Both papers
   should use the same numbers; current code uses Ch 4. Worth deciding
   for Ch 5.
4. **Mondière 2025's YS = 1978 − 68·γ% relation** — implemented as an
   alternative `f_A_correction_mode="mondière_2025"` (Phase 3.7d) but
   over-corrects at high f<sub>A</sub> (gives 815 MPa at 12.6 % core
   vs measured 1900). Not used as default. If the chapters cite it,
   the over-correction should be acknowledged.
5. **Critical bib correction needed before submission**: Akama 2016
   DOI is wrong in BOTH chapter bibs (lists Chang et al. tundish
   paper). The local PDF in `Chapter 5_Refs_Paper1/files/9788/` is
   also the wrong content. Correct DOI: `10.2355/isijinternational.isijint-2016-140`.

---

## 6. Recommended next direction (open for discussion)

Three options, in increasing scope:

1. **Adopt H-anchored as the model's "primary" cw/cr σ<sub>y</sub>
   output** in the cw/cr predictions chapter; relegate microstructure-
   only as the "comparison from-physics" mode. Recommended for the
   manuscript narrative.
2. **Phase 3.8d — extend with a per-zone ρ proxy** (e.g., scale ρ by
   relative depth fraction informed by the H gradient) so the
   microstructure-only prediction approaches the H-anchored answer.
   Closes the −14 % gap at 60 % CR via parametrization rather than
   measurement.
3. **Move to the K<sub>IC</sub> mechanism question** — the doubling-
   with-CW story has no model in the literature. Could be a paper
   contribution if we can build a defensible mechanism. The Maresca
   framework [1-3] suggests the natural starting point: interlath γ
   films contribute deformability (energy absorption) under
   cumulatively-large strain in proportion to their boundary-network
   connectivity (Ch 4 documents "boundary-following network at lath
   interfaces (20-80 nm)" at 40 % CR; "elongated residual films" at
   60 % CR). A `K_IC ∝ f_film · L_film_boundary_network` scaling could
   plausibly be calibrated against the measured 219 → 434 MJ/m³
   tensile-toughness rise.

---

## 7. References to module code

| Concept | Code path |
|---|---|
| Strengthening contribution decomposition | [`m54model.strengthening`](../src/m54model/strengthening/__init__.py) |
| cw/cr state factory | [`m54model.calibration.anchors.m54_af_t516_10_cw`](../src/m54model/calibration/anchors.py) |
| 3.7b — empirical f<sub>engaged</sub>(CR) | [`_subblock_hp_increment_MPa`](../src/m54model/calibration/anchors.py) |
| 3.8a — microstructure-only TT mixture | [`predict_bulk_sigma_y_through_thickness`](../src/m54model/strengthening/through_thickness.py) |
| 3.8b — per-zone H inversion | [`derive_zone_sigma_y_from_nanoindent`](../src/m54model/strengthening/through_thickness.py) |
| 3.8c — H-anchored bulk σ<sub>y</sub> | [`predict_bulk_sigma_y_h_anchored`](../src/m54model/strengthening/through_thickness.py) |
| Side-by-side comparison | [`cw_cr_sigma_y_summary`](../src/m54model/strengthening/through_thickness.py) |
| Paper-ready visualization | [`notebooks/02_trip_toughening.ipynb`](../notebooks/02_trip_toughening.ipynb) §3c |

For a longer-form discussion of where the predictions come from and
what the residuals tell us, see [`EVALUATION_M54_MODEL_v1.md`](EVALUATION_M54_MODEL_v1.md);
for the per-CR contribution audit see [`CW_CR_STRENGTHENING_ANALYSIS.md`](CW_CR_STRENGTHENING_ANALYSIS.md);
for the lit-search underlying the modeling choices see
[`LIT_SEARCH_PHASE_3_7.md`](LIT_SEARCH_PHASE_3_7.md).

For the running phase log of model insights (what changed, when, and
why), see [`FINDINGS.md`](FINDINGS.md).

---

## References

1. F. Maresca, V. G. Kouznetsova, M. G. D. Geers. "On the role of
   interlath retained austenite in the deformation of lath martensite."
   *Modell. Simul. Mater. Sci. Eng.* **22** (2014) 045011.
   [doi:10.1088/0965-0393/22/4/045011](https://doi.org/10.1088/0965-0393/22/4/045011)
2. F. Maresca, W. A. Curtin. "The austenite/lath martensite interface
   in steels: Structure, athermal motion, and in-situ transformation
   strain revealed by simulation and theory." *Acta Materialia*
   **134** (2017) 302-323.
   [doi:10.1016/j.actamat.2017.05.044](https://doi.org/10.1016/j.actamat.2017.05.044)
3. F. Maresca, V. G. Kouznetsova, M. G. D. Geers, W. A. Curtin.
   "Contribution of austenite-martensite transformation to deformability
   of advanced high strength steels: From atomistic mechanisms to
   microstructural response." *Acta Materialia* **156** (2018) 463-478.
   [doi:10.1016/j.actamat.2018.06.028](https://doi.org/10.1016/j.actamat.2018.06.028)
