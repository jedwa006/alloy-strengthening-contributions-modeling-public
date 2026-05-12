# Literature search — Phase 3.7

Tool budget used: ~24 calls (Read PDFs in pdf-archive and reference docs; WebFetch
to api.crossref.org; no modifications to `reference docs/`).

Status flag legend: **VP** = verified from PDF I read; **VC** = verified from
Crossref metadata only (no full-text seen); **U** = unverified.

---

## Q1. Sub-block / cell-size Hall-Petch coefficient K_sub for cold-worked tempered martensitic UHSS

**The literature does not give a clean K_sub for sub-block boundaries specifically.**
What it does give is K_block (block boundaries, treated as effective HP barriers).
The user's K_sub = 150 MPa·µm^½ is in the lower end of plausible values, but
no paper I located reports an explicit sub-block coefficient for AerMet-class steels.

- **Galindo-Nava & Rivera-Díaz-del-Castillo, Acta Mater. 98, 81-93 (2015)**, DOI
  `10.1016/j.actamat.2015.07.018`. **VP**. Already cited (Ch 5 as
  `sun21_GalindoNava_2015`; main bib). They use **K_HP = 300 MPa·µm^½** for the
  *block boundary* contribution (their Eq. 8, σ_Mart = 300/√d_block + 0.25·M·µ·b·√ρ).
  This is fitted across 7 martensitic + 5 dual-phase steels and is the cleanest
  general-purpose value available. It is for *block*, not sub-block.

- **Morito, Yoshida, Maki, Huang, MSE A 438-440, 237-240 (2006)** = `sun19_Morito_2006`,
  DOI `10.1016/j.msea.2005.12.048`. **VP**. Already cited (Ch 5 + main).
  Hall-Petch slopes for **block boundaries** in Fe-0.2C: **0.85 MPa·m^½** for
  Fe-0.2C and **0.72 MPa·m^½** for Fe-0.2C-2Mn (≈ 850 and 720 MPa·µm^½ respectively).
  These are *block* values, not sub-block, and are higher than Galindo-Nava's
  300 because they are local fits, not multi-alloy averages.
  Sub-block widths reported (Table 2): 1.4 µm (large PAGS) and 0.7 µm (small PAGS),
  with sub-block misorientation 6°, lath-boundary misorientation ~3°. Morito does
  *not* give a sub-block HP coefficient and explicitly attributes block (high-angle)
  boundaries as the dominant strengthener.

- **Akama, Tsuchiyama, Takaki, ISIJ Int. 56(9), 1675-1680 (2016)**.
  **CRITICAL DOI ERROR FOUND**: Both Ch 4 and Ch 5 bibs list the DOI as
  `10.2355/isijinternational.ISIJINT-2016-077`, but Crossref shows that DOI
  belongs to *Chang et al., "Removal of Inclusions Using Micro-bubble Swarms..."*
  — a tundish/water-modeling paper, **not** Akama. Confirmed by reading the PDF
  attached at `reference docs/Chapter 5_Refs_Paper1/files/9788/Akama et al. ...pdf`
  which on inspection is the Chang/Guthrie tundish paper. **The correct DOI is
  `10.2355/isijinternational.isijint-2016-140`** (verified via Crossref keyword
  search; ISIJ Int. Vol. 56, Issue 9, pp. 1675-1680). The actual Akama paper PDF
  is **not present locally**, so I cannot confirm its quantitative claims from a PDF.
  This is the same misfile in both bibs — needs correcting before either chapter
  is submitted.

**Bottom line for Q1**: There is no published K_sub for an AerMet-class alloy.
K_block ≈ 300 MPa·µm^½ (Galindo-Nava, multi-alloy fit) is the most defensible
literature anchor. K_sub = 150 MPa·µm^½ (half of K_block) is consistent with
sub-block boundaries being lower-misorientation (and therefore weaker) than blocks,
but it remains a single-point fit. No contradiction — just no independent
calibration.

---

## Q2. Matrix-toughness K_matrix(d_subblock) scaling for tempered martensitic UHSS

- **Wang, Zhang, Huang et al., Materials 16, 6907 (2023)** = `wangEvolutionMicrostructure2023`
  (already cited in Ch 5). DOI `10.3390/ma16216907`. **VP**.
  AerMet 100 tempered at 482 °C / 1-20 h. Quantitative claim: K_IC tracks
  reverted-austenite content, *not* dislocation density or sub-block size directly.
  Their abstract: "K_IC is primarily influenced by the reverted austenite, so that
  K_IC increases gradually with the prolongation of the tempering time… a
  significant decrease in the dislocation density resulting from long-term tempering
  has a certain impact on K_IC, giving rise to a decrease in the rising amplitude of
  K_IC after tempering for 8 h or more." So Wang 2023 does NOT support a direct
  K_matrix(d_subblock) scaling — it actually attributes most of the K_IC change to
  reverted austenite films.

- **Maresca, Kouznetsova, Geers, Modelling Simul. Mater. Sci. Eng. 22, 045011 (2014)**.
  DOI `10.1088/0965-0393/22/4/045011`. **VC** (verified via Crossref; no PDF in
  either chapter folder, no abstract returned by Crossref). Already cited in Ch 4
  + Ch 5. Per their title and the way Ch 4 page 14 cites them, this is a continuum
  model of inter-lath retained austenite as a soft compliant layer — it does not
  directly give a K_matrix(d_subblock) closed form for UHSS.

- **No paper located** that gives a direct closed-form K_matrix(d_subblock)
  scaling. The literature treats UHSS toughness via (a) reverted austenite
  thickness/stability (Wang 2023; Mondière 2025), (b) carbide
  size/spacing (Mondière 2018), and (c) inclusion content. The user's
  observation (K_IC doubling with cold work) is most likely captured indirectly
  through the cold-work-induced *change in sub-block / dislocation arrangement*
  driving more interlath austenite stabilization — i.e. via Wang 2023's pathway,
  not via a sub-block toughness law.

**Recommended addition to bib**: nothing new — Wang 2023 already covers this and
should be cited *as the rebuttal to* a direct K_matrix(d_subblock) form.

---

## Q3. Maresca/Curtin austenite-martensite glissile interface framework

- **Maresca, Kouznetsova, Geers, Curtin, Acta Mater. 156, 463-478 (2018)**, DOI
  `10.1016/j.actamat.2018.06.028`. **VC** (Crossref-verified; abstract not
  returned). Title: "Contribution of austenite-martensite transformation to
  deformability of advanced high strength steels: From atomistic mechanisms to
  microstructural response." **Not yet in any of our bibs.** This is the
  full atomistic-to-microscale paper that Ch 4 should be citing alongside the
  Maresca 2014 paper. It supersedes the 2014 work in scope.

- The 2014 Maresca paper (already cited) provides the geometric layer model.
  The 2018 Maresca-Curtin paper provides the atomistic kinetic basis for the
  glissile interface. Neither provides a drop-in α/β replacement for Olson-Cohen;
  the Maresca framework is more about deformation accommodation than nucleation
  kinetics. **No quantitative substitute for Olson-Cohen α=3.55, β=0.30 found**
  for Fe-Ni-Co-Mo lath martensite specifically.

**Recommended addition to bib**: Maresca, Kouznetsova, Geers, Curtin 2018
(DOI 10.1016/j.actamat.2018.06.028) — currently missing.

---

## Q4. Šittner 2025 forward/reverse stress thresholds

- **Šittner, Heller, Iaparova, Kadeřávek, Molnárová, Tyc, Shape Mem. Superelast.
  11, 679-707 (2025)**, DOI `10.1007/s40830-025-00550-z`. **VP**. Already cited
  in Ch 4. From the σ-T diagrams in their Figs. 2-5 (read from PDF):
  - **σ^Y_A_slip** (austenite slip yield, extrapolated to RT): ~3 GPa (SE wire
    NiTi#1) and ~1.5 GPa (SME wire NiTi#5).
  - σ^FOR (forward MT under stress) and σ^REV (reverse MT) lines have the same
    slope in σ-T space but are *shifted* — i.e. there is a hysteresis ΔT (and
    correspondingly Δσ) between forward and reverse. The paper does not give a
    single closed-form ratio σ_REV/σ_FOR; it depends on temperature and on which
    of the two wires (SE vs SME).
  - Reading off Fig. 2a (NiTi#1) at T=0 °C: σ^FOR ≈ 350 MPa, σ^REV ≈ 250 MPa →
    **σ_REV/σ_FOR ≈ 0.7**. At higher T the ratio shifts.
  - Šittner explicitly notes (page 5): "The threshold stresses are different
    for forward and reverse MTs and characteristic for the SE and SME wire."
    There is **no claimed universal ratio**.
  - **No analogous quantitative claim for steels** is reported in this paper —
    Šittner is purely about NiTi. Any analogy to steel forward/reverse thresholds
    must come from elsewhere (Patel-Cohen σ_critical for steels, but that's a
    one-direction stress-assist criterion, not a hysteresis ratio).

---

## Q5. Akama 2016 quantitative numbers — saturation ρ, saturation CR%

**Cannot answer from local material.** The PDF at
`reference docs/Chapter 5_Refs_Paper1/files/9788/Akama et al. - 2016 - …pdf` is
**misnamed** — it is actually the Chang et al. tundish paper (DOI conflict
explained in Q1). The actual Akama 2016 paper (correct DOI
`10.2355/isijinternational.isijint-2016-140`, ISIJ Int. 56(9), 1675-1680) is
not present in either chapter folder or in `pdf-archive/`. WebFetch to the
J-STAGE article page was blocked.

**Recommended action**: User should re-pull the actual Akama PDF from J-STAGE
(open access) and replace the misnamed file. Until then, the "60% CR drop in
H_α′ being a saturation effect" claim cannot be cross-checked against Akama's
saturation curve. This gap is a real risk for Ch 4/Ch 5 if Akama is being
cited as the saturation evidence.

For dislocation-density saturation in cold-rolled lath martensite as a *concept*,
Galindo-Nava 2015 (Eq. 5) treats ρ in as-quenched lath martensite as inversely
proportional to lath thickness squared, and reports ρ ≈ 6×10^15 m^-2 for
Mart7 (0.56 wt% C) at room temperature. Cold-work saturation is not modeled
there.

---

## Q6. Spot-check of papers in Ch 4/Ch 5 bibs that we may not yet be using

- **Mondière 2025 (Ch 5 ref)**, DOI `10.1016/j.jmrt.2025.03.230`. **VP**.
  Already cited Ch 5 (`mondiereControlRetainedAustenite2025`). Key quantitative
  claim: **YS = 1978 − 68·γ%** (their Eq. 2), where γ% is retained austenite
  vol %. Linear softening of 68 MPa per 1 % RA, valid across the studied range
  for M54 itself. This is directly relevant to the user's strengthening model
  and worth pulling in as an empirical anchor for the RA softening term.

- **Wang 2023 AerMet 100 evolution (Ch 5)**, DOI `10.3390/ma16216907`. **VP**.
  Already cited. K_IC dominated by reverted-austenite, secondary effect of
  dislocation density only at long tempering times (≥ 8 h at 482 °C).

- **Oh, Kang, Jiang, Tasan 2024, MSE A 895, 146122**, DOI `10.1016/j.msea.2024.146122`.
  **VP**. Already cited Ch 4 + Ch 5. PH17-4 with reverted nano-austenite at two
  SFE levels (25 mJ/m² for SA+M, 19 mJ/m² for MA+M). RA fractions: 6.4 % (SA+M),
  12.6 % (MA+M). Average RA grain size 0.5-0.7 µm. Lower-SFE austenite undergoes
  TRIP at lower stress and reduces YS; higher-stability austenite mitigates strain
  localization at high strains. This is the cleanest published demonstration of
  SFE-dependent RA mechanical behavior in PH-class steels and supports treating
  RA stability (not just volume fraction) as a model variable.

---

## Recommended additions to project bib (NOT yet in any of our bibs)

1. **Maresca, Kouznetsova, Geers, Curtin, Acta Mater. 156, 463-478 (2018)** —
   DOI `10.1016/j.actamat.2018.06.028`. The atomistic-to-microscale companion to
   Maresca 2014. Belongs in Ch 4 alongside `marescaRoleInterlathRetained2014`.

## Bib corrections needed (high priority)

1. **Akama 2016 DOI is wrong in BOTH chapter bibs.** Both list
   `10.2355/isijinternational.ISIJINT-2016-077` (= Chang et al. tundish paper).
   Correct DOI is `10.2355/isijinternational.isijint-2016-140`. The local PDF
   in `Chapter 5_Refs_Paper1/files/9788/` is also the wrong paper (it is the
   Chang tundish PDF with an Akama filename). User should re-fetch the actual
   Akama PDF from J-STAGE (open access).

## Confidence summary

- High-confidence findings (verified from PDF): Galindo-Nava K_HP=300 MPa·µm^½;
  Morito 2006 block-boundary K=0.72-0.85 MPa·m^½; Wang 2023 K_IC pathway;
  Mondière 2025 YS = 1978 − 68·γ% relation; Oh 2024 SFE-dependent RA;
  Šittner 2025 σ-T diagram structure.
- Crossref-verified-only (no abstract or full text seen): Maresca-Curtin 2018,
  Maresca 2014.
- Open gaps: Akama 2016 actual content (PDF misfiled, web access blocked); no
  published K_sub anywhere in the literature I searched.
