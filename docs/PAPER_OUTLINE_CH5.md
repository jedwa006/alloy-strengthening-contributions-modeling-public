# Chapter 5 / Paper 1 — Outline and Model-Anchor Mapping

**Working title**: Contributions to Strength and Plasticity in Incremental Cold Rolled Ausformed and Tempered Ferrium M54

**Status**: skeleton for advisor review; intended to map the existing draft sections to the model deliverables in this repository so the manuscript revision can pull from a single audit-able source. The structure below mirrors the v0.X draft section sequence rather than proposing a restructure. Restructure decisions remain with the chapter author per the §10 baseline-lock convention in the Chapter 2 STYLE_GUIDE.

---

## Section 1. Introduction

**Function**: motivate the cw/cr regime as a previously-untreated processing window for fully ausformed-and-tempered Co-Ni secondary-hardening UHSS, and frame the four-point measured property series the chapter reports.

**Content already present in draft**: standard UHSS family lineage (AF1410, AerMet® 100, Ferrium® S53, M54), commercial reference σ<sub>y</sub> and K<sub>IC</sub> figures from the Carpenter (2025) datasheet, processing route through ausforming and 516 °C / 10 h temper, and the literature gap regarding cw of fully-tempered UHSS.

**Model contributions to weave in**:

- The Phase 3.6 series establishes that the σ<sub>y</sub> decomposition of Sun et al. (2022) and Zhu et al. (2025) extends to the cw/cr regime with three independent prediction paths that bracket the measured σ<sub>y</sub> at both 0 % and 60 % CR. This is the framing for "the present study extends the conventional decomposition into the post-temper deformation regime."
- The TRIP-toughening literature (Patel and Cohen 1953; Olson and Cohen 1975) predicts < 0.3 MPa·m<sup>½</sup> ΔK<sub>TRIP</sub> at M54 f<sub>A</sub> levels. The user's measured tensile-toughness doubling from 219 to 434 MJ/m³ across cw/cr is therefore *not* a TRIP K<sub>IC</sub> story; the Maresca framework that this thesis adopts in Chapter 2 §2.5 is the published basis for interlath-austenite-plasticity at cumulatively-large strain.

**Citations to land**: Sun et al. 2022; Mondière et al. 2018; Mondière et al. 2025; Zhu et al. 2025; Wang et al. 2023; Maresca-Curtin 2017; Maresca, Kouznetsova, Geers, Curtin 2018; Patel and Cohen 1953; Olson and Cohen 1975.

---

## Section 2. Materials and Methods

**Function**: document the user's processing route, mechanical-testing setup, ASTAR-PED protocol, nanoindentation protocol, and tensile-test conditions.

**Status**: largely complete in draft; the model side adds only the strain-rate caveat for cross-comparison to Sun 2022 quasi-static measurements (Phase 3.5.2). The user's tensile tests run at 10⁻¹ s⁻¹ versus Sun 2022's 5 × 10⁻⁴ s⁻¹; for tempered M54 with strain-rate sensitivity m ≈ 0.01, the multiplicative correction is (200)<sup>0.01</sup> ≈ 1.054. Documenting this conversion permits direct comparison between the present measurements and the published Sun anchor values.

**Citations to land**: Sun et al. 2022 for the strain-rate baseline; Roberts 1978 or equivalent for the m ≈ 0.01 strain-rate-sensitivity convention.

---

## Section 3. Results

### 3.1 Retained austenite quantification

**Function**: present the ASTAR f<sub>A</sub>(CR) trajectory at surface and core locations.

**Already in draft**: Table 2 phase fractions; Figure 2 surface/core RA vs CR; partial reverse-transformation observation between 40 and 60 % CR.

**Model contribution**: confirms that the multi-axial-PC reverse-transformation framework of Chapter 4 §"Origin of the Retained-Austenite Cycle" applies under the rolling stress state. Quantitative U<sub>max</sub>(σ) calculations for tension, compression, and hydrostatic loading at the user's measured rolling pressures show that triaxial compression at the bite contributes negatively to U<sub>max</sub> (the +0.04 volumetric Bain strain works against the hydrostatic-compression component), consistent with the partial reverse transformation observed at 60 % CR.

### 3.2 Hardness and modulus depth profiles

**Function**: present nanoindentation H<sub>composite</sub> and E<sub>r</sub> per through-thickness zone for each CR.

**Already in draft**: Figure 2 depth profiles; Figure 4 H–E<sub>r</sub> plane scatter.

**Model contribution**: the Chapter 5 phase-correction Equation 1 (H<sub>α′</sub> = (H<sub>composite</sub> − f<sub>γ</sub> · H<sub>γ</sub>) / (1 − f<sub>γ</sub>) with H<sub>γ</sub> = 4.0 GPa) is implemented in `m54model.strengthening.derived_properties.phase_corrected_alpha_prime_hardness_GPa`. Forward-calculation gives H<sub>α′</sub> predictions within ±6 % of the Chapter 5 measured values at 0 % and 20 % CR; at 40 % and 60 % CR the gap reaches 14 %, consistent with the σ<sub>y</sub> under-prediction at high CR captured by the Phase 3.8a microstructure-only model.

### 3.3 Phase-corrected martensite hardness

**Function**: present H<sub>α′</sub>(CR) and interpret the apparent H plateau between 20 and 40 % CR as an austenite-dilution artifact.

**Already in draft**: Figure 5 H<sub>α′</sub>(CR) with Akama-style dislocation-saturation interpretation at 60 % CR.

**Model contribution**: the Tabor calibration C = 3.24 anchored at the 0 % CR baseline (H<sub>α′</sub> = 6.8 GPa, σ<sub>UTS</sub> = 2100 MPa) propagates to predicted H<sub>α′</sub> at each CR with no additional fit parameters. Reports the through-zone consistency of σ<sub>y</sub> derived via H<sub>composite</sub> + Equation 1 + Tabor (the Phase 3.8c chain).

### 3.4 Tensile response

**Function**: report σ<sub>y</sub>, σ<sub>UTS</sub>, total elongation, and tensile toughness U at the cw/cr conditions tested.

**Already in draft**: Table 3 tensile properties; Figure 3 engineering stress–strain curves and U(CR) bar chart.

**Model contribution**: σ<sub>y</sub>(CR) predicted by the Phase 3.8c H-anchored approach reproduces measured tensile σ<sub>y</sub> within ±2 % at both 0 % and 60 % CR with no hand-fit knobs. The σ<sub>y</sub> contribution decomposition figure (notebook 02 §3d, Zhu Fig. 10 style) provides the source-by-source attribution needed for the discussion of which mechanisms move with CR. The Maresca-anchored U(CR) predictor (notebook 02 §3e) reproduces the measured U series within ±5 % at every measured point, attributing approximately 42 % of the 60 % CR U to the Maresca interlath-austenite-plasticity mechanism and the remainder to σ<sub>avg</sub>(CR) growth via matrix strengthening.

---

## Section 4. Discussion

### 4.1 Origin of the retained-austenite cycle

**Already in draft**: §4.1 invokes the Patel-Cohen criterion for stress-assisted reverse BCC→FCC transformation under rolling plane-strain compression.

**Model contribution**: provides the explicit U<sub>max</sub>(σ) tension/compression/hydrostatic decomposition (see [`docs/CW_CR_STRENGTHENING_ANALYSIS.md`](CW_CR_STRENGTHENING_ANALYSIS.md) §3 for the quantitative cross-tab). The Maresca-Kouznetsova-Geers-Curtin (2018) atomistic basis for the forward-FCC→BCC-spontaneous and reverse-BCC→FCC-stress-requiring asymmetry strengthens the published support for this section.

### 4.2 Hardness–modulus decoupling

**Already in draft**: H tracks dislocation density and precipitate interactions; E<sub>r</sub> tracks phase fraction and crystallographic texture. The two evolve along decoupled trajectories in H–E<sub>r</sub> space.

**Model contribution**: the Equation 1 phase-correction quantifies the magnitude of austenite-dilution effect on bulk H, separating the H<sub>α′</sub> matrix evolution from the f<sub>γ</sub>-driven contribution. The pure-martensite H<sub>α′</sub>(CR) saturation at 60 % CR follows directly from the inverted equation.

### 4.3 Strengthening attribution per CR

**Status in draft**: the user has noted the need to discuss "strength due to increases in dislocation density in the martensite and plasticity due to the presence and morphology of the austenite."

**Model contribution**: this is the natural home for the Zhu Fig. 10-style σ<sub>y</sub> contribution-attribution figure (notebook 02 §3d). The figure decomposes the +600 MPa rise from σ<sub>y</sub>(0 %) = 1300 to σ<sub>y</sub>(60 %) = 1900 into +315 MPa from σ<sub>ρ</sub> (the GND density rise from 1.6 to 6.3 × 10¹⁵ m⁻²), +194 MPa from σ<sub>HP,sub</sub> (the cw-induced sub-block Hall-Petch term at K<sub>sub</sub> = 150 MPa·µm<sup>½</sup>), and small residual contributions from the f<sub>A</sub> correction and the strain-rate factor.

### 4.4 TRIP effect and the 40 % CR processing window

**Already in draft**: §4.4 identifies 40 % CR as the optimal processing window combining peak H<sub>α′</sub> with the largest TRIP-active RA reservoir.

**Model contribution**: the Maresca-anchored tensile-toughness predictor with morphology-dependent κ<sub>film</sub> (Phase 3.9b) supplies the quantitative attribution: at 40 % CR, κ<sub>film</sub> = 0.55 and f<sub>film</sub> = 0.099 give U<sub>film</sub> = 121 MJ/m³, approximately 35 % of total predicted U. The framework explains the apparent dip in measured U at 53 % CR via the transitional bimodal morphology and recovers the peak U at 60 % CR via the RD-aligned elongated-film morphology that maximizes the Schmid-averaged effective transformation strain.

### 4.5 K<sub>IC</sub> framing note

**Status in draft**: the chapter's "toughness" metric is tensile-area-under-curve in MJ/m³ rather than fracture K<sub>IC</sub> in MPa·m<sup>½</sup>; the distinction needs to be explicit in the discussion to avoid the units conflation observed in some derivative materials.

**Model contribution**: provides the ΔK<sub>TRIP</sub> < 0.3 MPa·m<sup>½</sup> bound at M54 f<sub>A</sub> levels as the bounding statement on the K<sub>IC</sub>-side TRIP contribution, which Chapter 5 explicitly excludes from scope.

---

## Section 5. Conclusion

**Draft conclusion already present**: 6 numbered findings spanning skin-pass-rolling viability, interlath film network architecture, bimodal microstructure at 40 % CR, texture sharpening then anomalous decrease at 60 % CR, lath morphological-texture evolution, and depth-resolved through-thickness asymmetry. These align with the Chapter 4 conclusion and require no model-specific additions.

**Suggested model-side conclusion items**:

- σ<sub>y</sub>(CR) prediction within ±2 % at the two measured CR conditions using the Phase 3.8c H-data-anchored approach, with no hand-fit knobs.
- Tensile toughness U(CR) prediction within ±5 % at all four measured CR conditions using the Maresca-anchored Phase 3.9b morphology-dependent κ<sub>film</sub>.
- Quantitative attribution of approximately 42 % of the 60 % CR tensile toughness to the Maresca interlath-austenite-plasticity mechanism with the remainder traceable to σ<sub>avg</sub>(CR) growth.

---

## Section 6. Critical pre-submission corrections

These items must close before manuscript submission. They are not modeling questions; they are housekeeping that has surfaced during this work.

1. *Akama 2016 DOI in both chapter bibs.* Listed under DOI 10.2355/isijinternational.ISIJINT-2016-077, which Crossref shows belongs to Chang et al. (a tundish-modeling paper). Correct DOI: 10.2355/isijinternational.isijint-2016-140. The local PDF at `reference docs/Chapter 5_Refs_Paper1/files/9788/` is the wrong content as well; re-pulling the correct file from J-STAGE before submission closes both issues.
2. *Maresca-Curtin 2017 and Maresca-Kouznetsova-Geers-Curtin 2018 citations.* Both papers are now in the user's general references bib via the 2026-05-11 Zotero re-export. They need to be added to the Chapter 4 and Chapter 5 reference lists where the Maresca framework is invoked. The chapter draft already cites Maresca, Kouznetsova, Geers 2014 alongside.
3. *Tensile-toughness units convention.* The draft slide values 219/322/280/434 are MJ/m³ (the slide label "MPa/m²" was a notation issue; numerically MJ/m³ equals MPa for dimensionless strain). The Chapter 5 §"Toughness" text needs to harmonize internally: the §3.4 Fig. 3b bars use MJ/m³ matching the slide trend (toughness increases with CR), while the body text claim "fell to roughly half of the baseline value" describes a decreasing trend that contradicts both the slide and the figure. This needs resolution before submission.

---

## Section 7. Repository mapping for the manuscript writer

| Manuscript section | Repository deliverable |
|:---|:---|
| §1 Introduction (model-extension framing) | [`docs/EVALUATION_M54_MODEL_v1.md`](EVALUATION_M54_MODEL_v1.md) §1; [`docs/CW_CR_PROGRESS_REPORT_2026_05_12.md`](CW_CR_PROGRESS_REPORT_2026_05_12.md) §1 |
| §2 Materials and Methods (strain-rate note) | `m54model.calibration.strain_rate` module + FINDINGS Phase 3.5.2 entry |
| §3.1 RA quantification (mechanism interp.) | [`docs/CW_CR_STRENGTHENING_ANALYSIS.md`](CW_CR_STRENGTHENING_ANALYSIS.md) §3 (multi-axial PC analysis) |
| §3.2 Hardness depth profiles + Eq. 1 | `m54model.strengthening.derived_properties.composite_hardness_GPa` and `phase_corrected_alpha_prime_hardness_GPa` |
| §3.3 Phase-corrected H<sub>α′</sub> | Tabor calibration in `derived_properties.tabor_hardness_GPa_from_sigma_uts` |
| §3.4 Tensile response + U(CR) | Notebook 02 §3b, §3d (σ<sub>y</sub>); §3e (Maresca U) |
| §4.1 RA cycle origin | [`docs/CW_CR_STRENGTHENING_ANALYSIS.md`](CW_CR_STRENGTHENING_ANALYSIS.md) §3 + Chapter 4 §"Origin" |
| §4.3 Strengthening attribution | Notebook 02 §3d (Zhu Fig. 10 stacked-bar attribution) |
| §4.4 40 % CR processing window | Notebook 02 §3e (Maresca decomposition with morphology κ<sub>film</sub>) |
| §4.5 K<sub>IC</sub> framing note | Notebook 03 §1–§4 (ΔK<sub>TRIP</sub> bound) |

For the running log of model-side decisions and the per-phase chronology that produced each deliverable, see [`docs/FINDINGS.md`](FINDINGS.md).
