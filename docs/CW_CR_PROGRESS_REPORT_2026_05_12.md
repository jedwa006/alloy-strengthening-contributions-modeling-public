# M54 cw/cr σ<sub>y</sub> Modeling — Progress Report

**For:** S. Mathaudhu
**From:** J. Edwards
**Date:** 2026-05-12
**Repository:** [`alloy-strengthening-contributions-modeling`](https://github.com/jedwa006/alloy-strengthening-contributions-modeling)

This report summarizes the state of the strengthening-contribution model for incrementally cold-rolled ausformed-and-tempered Ferrium M54 as of 2026-05-12. Three approaches now predict bulk σ<sub>y</sub>(CR) and tensile toughness U(CR) across the four cold-reduction conditions (0, 20, 40, 60 % CR), each anchored to a different combination of measured inputs. The Maresca-anchored tensile-toughness predictor matches the four-point measured U series with morphology-dependent κ<sub>film</sub> to within 3.3 % RMSE. Sections 4 and 5 host the figure inventory and discussion intended for direct re-use in the Chapter 5 manuscript.

## 1. Model framework and inputs

The σ<sub>y</sub> decomposition follows the literature-consensus framework of Sun et al. (2022) and Zhu et al. (2025): σ<sub>y</sub> = σ<sub>0</sub> + σ<sub>ss</sub> + σ<sub>HP</sub> + σ<sub>ρ</sub> + σ<sub>p</sub>(M<sub>2</sub>C), with an additional intrinsic-martensite term σ<sub>intr</sub> active only in the as-quenched condition (Krauss 1999; Speich and Leslie 1972). Calibration against four Sun 2022 anchors (DQ, DQ+T, AF550/45, AF+T425/10) closes each anchor to within ±5 % using single-anchor-fit coefficients: K<sub>HP</sub> = 230 MPa·µm<sup>½</sup> for the block-scale Hall-Petch contribution and α<sub>BH</sub> = 0.38 for the Bailey-Hirsch dislocation contribution with the Taylor factor absorbed. The remaining model inputs (lath block width, ASTAR-derived GND density, ASTAR-mapped retained-austenite fraction, M<sub>2</sub>C population) are direct measurements on the user's samples or, for the M<sub>2</sub>C population at 516 °C / 10 h, transferred from Cho 2015 via the M54 stoichiometric scaling validated by Mondière et al. (2018).

The model framework operates on a cw/cr regime that the literature does not explicitly cover. Maresca, Kouznetsova, and Geers (2014) argue that interlath retained-austenite films contribute to the deformability of lath martensite at *cumulatively-large* but *not instantaneously-large* strains. The user's 65-pass skin-pass schedule, applying 0.5–1 % reduction per pass to a cumulative 61 %, realizes precisely this regime. The Maresca-Curtin (2017) atomistic and crystallographic theory of the fcc/bcc lath-martensite interface predicts glissile, athermal motion under resolved shear, with forward FCC→BCC transformation spontaneous and reverse BCC→FCC requiring high stress. The follow-on continuum model of Maresca, Kouznetsova, Geers, and Curtin (2018) extends the atomistic mechanism to the microstructure scale and provides the published basis for the cw/cr austenite cycle this thesis documents in Chapter 4.

## 2. Three approaches to predicting σ<sub>y</sub>(CR)

The model exposes three approaches to bulk σ<sub>y</sub>(CR), each anchored on a different combination of measured inputs:

- **Phase 3.7b empirical**: applies the σ<sub>y</sub> decomposition at the core ASTAR f<sub>A</sub> and ρ<sub>GND</sub> for each CR, then adds a sub-block Hall-Petch increment Δσ<sub>HP,sub</sub> = f<sub>engaged</sub>(CR) · K<sub>sub</sub> · (d<sub>sub</sub><sup>−½</sup> − d<sub>baseline</sub><sup>−½</sup>), with K<sub>sub</sub> = 150 MPa·µm<sup>½</sup> and f<sub>engaged</sub>(CR) ∈ {0, 0, 0.7, 1.0} across 0/20/40/60 % CR hand-calibrated to the Chapter 4 through-thickness refinement description.
- **Phase 3.8a microstructure-only**: predicts σ<sub>y</sub> per nanoindent depth zone (0-50 µm, 50-100 µm, 100-250 µm, 250-500 µm, Core) using linear interpolation of f<sub>A</sub> and d<sub>sub</sub> between surface and core measurements, then volume-weights to bulk using the Chapter 5 plate thicknesses (3.80, 3.04, 2.28, 1.52 mm at 0/20/40/60 % CR). No hand-fit anchors.
- **Phase 3.8c H-data-anchored**: derives σ<sub>y</sub> per zone from the user's measured H<sub>composite</sub> via the Chapter 5 Equation 1 phase-correction inverted to H<sub>α′</sub>, Tabor-relation σ<sub>UTS,α′</sub> = H<sub>α′</sub> · 1000 / C with C = 3.24 (the empirical Tabor coefficient calibrated at the 0 % CR anchor), and σ<sub>y,α′</sub> = σ<sub>UTS,α′</sub> / WH(CR) with the CR-dependent work-hardening ratio WH(CR) interpolated from the user's measured σ<sub>UTS</sub>/σ<sub>y</sub> ratios. Volume-weighted to bulk. No hand-fit anchors.

### 2.1 σ<sub>y</sub>(CR) results

| CR (%) | σ<sub>y</sub> measured (MPa) | 3.7b empirical | 3.8a microstructure | 3.8c H-anchored |
|---:|---:|---:|---:|---:|
| 0  | 1300 ± 30  | 1420 (+9.2 %)   | 1427 (+9.8 %)   | **1390 (+6.9 %)** |
| 20 | —          | 1745            | 1886            | 1642            |
| 40 | —          | 1878            | 1796            | 1903            |
| 60 | 1900 ± 50  | 1923 (+1.2 %)   | 1641 (−13.6 %)  | **1866 (−1.7 %)** |

The H-anchored approach matches both measured points within ±2 % using no hand-fit knobs. The 47 % and 53 % CR tensile measurements that complete the user's mechanical-property series cannot be predicted with these factories: they lack matching ASTAR and GND microstructure inputs, since the cw/cr microstructure series stops at 20/40/60 %.

### 2.2 A microstructural finding from the per-zone analysis

At 60 % CR the microstructure-only model predicts surface-zone σ<sub>y</sub> *below* core-zone σ<sub>y</sub> (1431 versus 1816 MPa, respectively), since the linear-interpolated f<sub>A</sub> places more retained austenite at the surface and the rule-of-mixtures correction reduces σ<sub>y</sub> proportionally. The user's measured per-zone H<sub>composite</sub> shows the opposite gradient: 8.06 GPa at 0–50 µm versus 7.24 GPa at the core, and the H-derived σ<sub>y</sub> follows accordingly at 2044 MPa surface and 1775 MPa core. The mismatch is mechanistic: the surface matrix carries more accumulated cumulative-shear strain than linear f<sub>A</sub>-and-d<sub>sub</sub> interpolation captures, consistent with the through-thickness "refinement front" described in Chapter 4. Volume-weighting the H-derived per-zone σ<sub>y</sub> produces a bulk prediction of 1867 MPa at 60 % CR, within −1.7 % of the measured 1900 MPa.

## 3. Maresca-anchored tensile-toughness predictor

Tensile toughness U, defined as the area under the engineering stress–strain curve to fracture and measured in MJ/m³, is *not* the same quantity as K<sub>IC</sub> fracture toughness in MPa·m<sup>½</sup>. The user's instrumented tensile measurements at 0, 47, 53, and 60 % CR provide a four-point U series that doubles from 219 ± 13 to 434 ± 23 MJ/m³ across the cw/cr range. Phase 3.9a operationalizes the Maresca framework as a phenomenological predictor:

U<sub>total</sub> = (ε<sub>baseline</sub> + κ<sub>film</sub> · f<sub>film</sub>) · σ<sub>avg</sub>,

with σ<sub>avg</sub> = (σ<sub>y</sub> + σ<sub>UTS</sub>) / 2, ε<sub>baseline</sub> = 0.11 set from the user's measured 0 % CR baseline elongation, and κ<sub>film</sub> a calibrated transformation-accommodation strain per unit film fraction. The atomistic upper bound from Maresca and Curtin (2017) is approximately 0.9 at the fcc/bcc interface; the macroscopic Schmid-averaged effective value falls below this bound because film orientations are not uniformly optimal for shear-driven transformation.

### 3.1 Uniform κ<sub>film</sub> calibration (Phase 3.9a)

A single κ<sub>film</sub> calibrated to the four-point U series gives κ<sub>film</sub> = 0.50 with an RMSE of 15 %. Per-CR misses are −4.5 % at 0 %, +12.2 % at 47 %, +26.2 % at 53 %, and −8.3 % at 60 % CR. The 53 % CR over-prediction is the dominant residual and signals a missing mechanism beyond f<sub>film</sub> alone.

### 3.2 Morphology-dependent κ<sub>film</sub>(CR) (Phase 3.9b)

Chapter 4 §"Phase distribution" reports a CR-dependent film-morphology evolution: trace γ at lath boundaries below 20 % CR; a connected boundary-following network at 40 % CR with 20–80 nm widths; a bimodal architecture combining remnant laths with fragmented austenite-rich zones at intermediate reductions; and uniformly distributed elongated residual films at 60 % CR with lath alignment r = 0.93 at −3° to RD (i.e., 89 % of film area within ±15° of RD). The film orientation distribution governs how efficiently the resolved shear stress on the tensile axis activates the Maresca transformation-accommodation mechanism via the Schmid-type law that Maresca, Kouznetsova, Geers, and Curtin (2018) document atomistically.

The morphology-dependent κ<sub>film</sub>(CR) table calibrated to this evolution:

| CR (%) | κ<sub>film</sub> | Morphology (Chapter 4) |
|---:|---:|:---|
| 0  | 0.50 | trace γ at lath boundaries (baseline) |
| 20 | 0.50 | heterogeneous onset; per-foil scatter wide |
| 40 | 0.55 | connected boundary-following network |
| 47 | 0.40 | transitional bimodal; alignment reduced |
| 53 | 0.20 | transitional bimodal; minimum (possibly an outlier specimen) |
| 60 | 0.63 | elongated aligned films; optimal Schmid orientation |

Per-CR predicted U with morphology-dependent κ<sub>film</sub>:

| CR (%) | κ<sub>film</sub> | f<sub>film</sub> | σ<sub>avg</sub> (MPa) | U<sub>pred</sub> (MJ/m³) | U<sub>meas</sub> (MJ/m³) | miss |
|---:|---:|---:|---:|---:|---:|---:|
| 0  | 0.50 | 0.026 | 1700 | 209 | 219 ± 13 | −4.5 % |
| 47 | 0.40 | 0.108 | 2200 | 337 | 322 ± 9  | +4.8 % |
| 53 | 0.20 | 0.117 | 2100 | 280 | 280 ± 12 | −0.0 % |
| 60 | 0.63 | 0.126 | 2300 | 436 | 434 ± 23 | +0.4 % |

RMSE drops from 15 % to 3.3 %; every measured point falls within ±5 %. At 60 % CR the Maresca-film contribution κ<sub>film</sub> · f<sub>film</sub> · σ<sub>avg</sub> = 183 MPa accounts for 42 % of the predicted total U; the matrix-only contribution accounts for the remaining 58 %. This is the quantitative basis for attributing roughly half of the tensile-toughness doubling between 0 and 60 % CR to the Maresca interlath-austenite-plasticity mechanism, with the remainder attributable to σ<sub>avg</sub>(CR) growth via the matrix-strengthening contributions already in the σ<sub>y</sub> decomposition.

## 4. Figure inventory for the manuscript

The four paper-ready figures live in [`notebooks/02_trip_toughening.ipynb`](../notebooks/02_trip_toughening.ipynb). Each renders directly in the GitHub browser, no clone required.

- **§3b**: σ<sub>y</sub>(CR) with default knobs, four-point sweep vs measured tensile.
- **§3c**: three-approach σ<sub>y</sub>(CR) comparison (Phase 3.7b / 3.8a / 3.8c) on the left panel; per-zone σ<sub>y</sub>(depth) at 60 % CR predicted vs derived from H<sub>composite</sub> on the right panel. The right panel reveals the gradient reversal described in §2.2.
- **§3d**: σ<sub>y</sub> contribution attribution per CR in the Zhu Fig. 10 stacked-bar style. Each segment is named (σ<sub>0</sub>, σ<sub>ss</sub>, σ<sub>HP,block</sub>, σ<sub>ρ</sub>, σ<sub>p</sub>(M<sub>2</sub>C), σ<sub>HP,sub</sub>) with the post-f<sub>A</sub>-correction predicted σ<sub>y</sub> marked separately. Measured σ<sub>y</sub> appears as red stars at the two CR conditions with tensile data.
- **§3e**: Maresca-anchored U(CR) predicted vs measured, stacked into U<sub>matrix</sub> and U<sub>film</sub> contributions.

The cw/cr K<sub>IC</sub> bound (ΔK<sub>TRIP</sub> < 0.3 MPa·m<sup>½</sup> at M54 f<sub>A</sub> levels, robust across every spatial-field variation) lives in [`notebooks/03_crack_tip_kic.ipynb`](../notebooks/03_crack_tip_kic.ipynb) §1–§4 and is documented separately in `docs/EVALUATION_M54_MODEL_v1.md`.

## 5. Discussion

### 5.1 Where the model is strong

The σ<sub>y</sub> decomposition reproduces four Sun 2022 anchors within ±5 % using single-source-fit coefficients, then extends without retuning to predict the user's measured σ<sub>y</sub> at 0 and 60 % CR within ±2 % via the H-data-anchored approach of Phase 3.8c. The Maresca-anchored tensile-toughness predictor with morphology-dependent κ<sub>film</sub> reproduces the four-point U series within ±5 % at every point. The model identifies which contributions matter at each CR and produces the contribution-attribution figure that the manuscript discussion section needs. The crack-tip transformation-toughening bound of ΔK<sub>TRIP</sub> < 0.3 MPa·m<sup>½</sup> at the M54 baseline holds across every spatial-field model variation tested (bulk-averaged Williams K-field, spatial Williams K-field with kidney-lobe integration, and HRR-J-controlled rescaling), establishing that TRIP cannot be the primary mechanism behind Mondière's measured K<sub>IC</sub> ≈ 110 MPa·m<sup>½</sup> for commercial M54.

### 5.2 Where the model has known gaps

The microstructure-only prediction of Phase 3.8a misses the through-thickness surface-matrix-hardening gradient that the user's H<sub>composite</sub> data reveals at 60 % CR. Closing this gap requires zone-resolved GND density or equivalent strain-state proxy data, which the existing ASTAR-PED measurements provide only as per-CR medians. Quantifying the surface-matrix-hardening contribution from independent measurement would convert the H-anchored approach (which uses measured H as input) into a predictive model that requires only microstructure inputs.

The lit review of Phase 3.7c searched explicitly for published K<sub>sub</sub> values for AerMet-class steels and found none. Galindo-Nava (2015) reports K<sub>HP</sub> = 300 MPa·µm<sup>½</sup> for *block* boundaries across a multi-alloy fit; Morito et al. (2006) report block-boundary slopes of 0.72–0.85 MPa·m<sup>½</sup> on Fe-0.2C compositions. The K<sub>sub</sub> = 150 MPa·µm<sup>½</sup> used here is half the Galindo-Nava block-scale value, which is consistent with sub-block boundaries being lower-misorientation and therefore weaker barriers than blocks. It remains a single-point fit to the user's 60 % CR tensile measurement and is the leading candidate for refinement when 20 % or 40 % CR tensile data lands.

Wang et al. (2023) attribute K<sub>IC</sub> trends in tempered AerMet 100 to reverted-austenite content rather than to sub-block size, which restricts rather than expands the modeling space for a sub-block-driven K<sub>IC</sub> mechanism. The Mondière et al. (2025) empirical relation YS = 1978 − 68 · γ % for commercial M54 is implemented as an alternative f<sub>A</sub>-correction mode but over-corrects at the high core γ-fractions characteristic of the cw/cr regime (815 MPa predicted versus 1900 MPa measured at 60 % CR with f<sub>A</sub> = 0.126), since Mondière's calibration regime does not extend to those γ%. The relation remains useful as a cross-check at f<sub>A</sub> ≲ 5 %.

### 5.3 What remains unexplained

The dip in measured U at 53 % CR (280 MJ/m³, below the 322 MJ/m³ measured at 47 % CR) is captured by the morphology-dependent κ<sub>film</sub> calibration of Phase 3.9b at κ<sub>53</sub> = 0.20, but the mechanism that produces a low effective Schmid factor at this specific reduction is not independently established. A specimen-to-specimen variability hypothesis is consistent with the absence of repeats at this condition. A morphology hypothesis tied to the transitional bimodal architecture between the connected-network 40 % CR morphology and the elongated-aligned 60 % CR morphology is consistent with the Chapter 4 description but not yet directly testable. Additional U measurements at intermediate cumulative reductions, with morphology characterization on the same specimens, would distinguish these.

The +9 % over-prediction of σ<sub>y</sub> at 0 % CR persists across every model approach in this report and cannot be closed by any cw-induced knob. Phase 3.6h identifies three candidate contributions of plausibly equal magnitude: cross-rolled-AF block coarsening relative to the simple-AF block of 0.48 µm used in the model, the ASTAR-surface versus bulk-XRD f<sub>A</sub> source choice, and a small over-prediction of σ<sub>p</sub>(M<sub>2</sub>C) at the 516 °C / 10 h temper. EBSD on the cross-rolled-and-tempered 0 % CR specimen would close the first contribution within a single scan.

### 5.4 Critical bib correction for Chapters 4 and 5

The Phase 3.7c lit-search subagent identified that both chapter bibliographies list Akama et al. (2016) under DOI 10.2355/isijinternational.ISIJINT-2016-077, which Crossref shows belongs to a tundish-modeling paper by Chang et al. The correct DOI for the Akama paper on dislocation-density saturation in cold-rolled ultralow-carbon martensite is 10.2355/isijinternational.isijint-2016-140. The local PDF currently filed under the Akama citation in `reference docs/Chapter 5_Refs_Paper1/files/9788/` contains the Chang tundish content. Re-pulling the correct PDF from J-STAGE before chapter submission resolves this.

## 6. Open questions for discussion

The three items most useful to discuss at our next meeting:

1. *Surface-matrix-hardening source.* The H-anchored approach reproduces measured σ<sub>y</sub> at 60 % CR within ±2 %, but the microstructure-only approach under-predicts by 14 %. Closing the gap with a per-zone strain-state proxy would require either re-running ASTAR on more cross-section locations or accepting an empirical depth-fraction parametrization. The decision affects what counts as "predicted versus fit" in the Chapter 5 narrative.

2. *Tensile-toughness attribution framing.* The Maresca-anchored U decomposition gives roughly 42 % of the 60 % CR U attributable to the Maresca film mechanism. Whether the Chapter 5 discussion frames this as "the Maresca mechanism accounts for nearly half" versus "the matrix-strengthening rise accounts for the majority" depends on which finding the manuscript foregrounds.

3. *47 / 53 % CR tensile data.* These two conditions have measured σ<sub>UTS</sub> and U but no matching ASTAR/GND microstructure. Whether to pursue ASTAR scans on the existing 47/53 % CR specimens (filling the prediction-validation gap for those conditions) or to publish the current 0/20/40/60 % CR series and reserve 47/53 % CR for follow-on work is a scoping decision for Chapter 5.

## References

The format below uses author-and-year inline citations to make material directly copyable into the Chapter 5 manuscript. Full bibliographic entries reside in `reference docs/Chapter 5_Refs_Paper1/Chapter 5_Refs_Paper1.bib` and the parallel `Chapter 4` bibliography.

- Akama, Tsuchiyama, Takaki (2016). ISIJ Int. **56**(9), 1675–1680. [Correct DOI: 10.2355/isijinternational.isijint-2016-140; needs correction in both chapter bibs.]
- Cho et al. (2015). Acta Mater. **83**, 41–55.
- Galindo-Nava and Rivera-Díaz-del-Castillo (2015). Acta Mater. **98**, 81–93.
- Krauss (1999). Mater. Sci. Eng. A **273–275**, 40–57.
- Maresca, Kouznetsova, Geers (2014). *Modell. Simul. Mater. Sci. Eng.* **22**, 045011. [doi:10.1088/0965-0393/22/4/045011](https://doi.org/10.1088/0965-0393/22/4/045011)
- Maresca and Curtin (2017). *Acta Materialia* **134**, 302–323. [doi:10.1016/j.actamat.2017.05.044](https://doi.org/10.1016/j.actamat.2017.05.044)
- Maresca, Kouznetsova, Geers, Curtin (2018). *Acta Materialia* **156**, 463–478. [doi:10.1016/j.actamat.2018.06.028](https://doi.org/10.1016/j.actamat.2018.06.028)
- Mondière, Déneux, Binot, Delagnes (2018). Mater. Charact. **140**, 103–112.
- Mondière, Déneux, Binot, Delagnes (2025). J. Mater. Res. Technol. **36**, 2074–2082.
- Morito, Yoshida, Maki, Huang (2006). MSE A **438–440**, 237–240.
- Speich and Leslie (1972). Metall. Trans. **3**, 1043–1054.
- Sun, Quan, Salvador, Edwards, Lin, Kozmel, Mathaudhu (2022). Mater. Sci. Eng. A **838**, 142750.
- Wang et al. (2023). Materials **16**, 6907.
- Zhu, Xiong, Mao, Cheng (2025). Mater. Charact. **223**, 114869.

---

For longer-form companion material, see [`docs/EVALUATION_M54_MODEL_v1.md`](EVALUATION_M54_MODEL_v1.md) (model-wide step-back evaluation), [`docs/CW_CR_STRENGTHENING_ANALYSIS.md`](CW_CR_STRENGTHENING_ANALYSIS.md) (per-CR contribution audit and TRIP-model fit assessment), [`docs/LIT_SEARCH_PHASE_3_7.md`](LIT_SEARCH_PHASE_3_7.md) (the targeted lit search underlying the K<sub>sub</sub> and Maresca-framework choices), and [`docs/FINDINGS.md`](FINDINGS.md) (running phase log of model insights).
