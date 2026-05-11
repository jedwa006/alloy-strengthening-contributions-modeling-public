# Main Article Index — Zhu et al. 2025

> **Note on title:** Several papers in our "cited-by" folder misquote this paper's title as ending with **"via dual Patel-Cohen deformation"**. The actual published title is **"via dual precipitation"**. Patel-Cohen mechanics surface only indirectly — through the stress-assisted austenite→martensite transformation invoked in the toughening discussion (§4.2.2). For our M54 model we are still well-grounded in invoking Patel-Cohen as the criterion for the strain-induced transformation, but we should NOT cite Zhu 2025 as if it presented a Patel-Cohen analysis itself; it does not.

---

## 1. Bibliographic Header

- **Title:** Achieving ultra-high strength, good toughness and cost reduction in secondary hardening steel via dual precipitation
- **Authors:** Haofei Zhu, Zhiping Xiong (corresp., zpxiong@bit.edu.cn), Jianwen Mao, Xingwang Cheng
- **Affiliations:**
  - (a) National Key Laboratory of Science and Technology on Materials under Shock and Impact, School of Materials Science and Engineering, Beijing Institute of Technology, Beijing 100081, China
  - (b) Tangshan Key Laboratory of High-Performance Metals and Ceramics, Tangshan Research Institute BIT, Tangshan 063000, China
- **Journal:** Materials Characterization, **223** (2025) 114869
- **DOI:** [10.1016/j.matchar.2025.114869](https://doi.org/10.1016/j.matchar.2025.114869)
- **Received:** 21 November 2024 | **Revised:** 3 February 2025 | **Accepted:** 22 February 2025 | **Online:** 25 February 2025
- **License:** © 2025 Elsevier Inc. All rights reserved. (Not open access.)

---

## 2. Alloy Studied (Table 1, wt%)

| C    | Co | Ni | Cr | Mo  | Al |
|------|----|----|----|-----|----|
| 0.25 | 5  | 11 | 3  | 1.5 | 1  |

- A novel **low-cobalt M2C + NiAl dual-precipitation secondary hardening UHSS**.
- Composition deliberately reduces Co from 13–15 wt% (AerMet 100 / AerMet 310 / AF1410) to **5 wt%** — the central cost-reduction lever.
- Comparison to Ferrium M54: M54 is 7 wt% Co, 10 Ni, 1 Cr, 2 Mo, 0.3 V, 1.3 W, 0.10 C. **This Zhu alloy is NOT M54** — but mechanism overlap is high (M2C-driven secondary hardening + Ni–Al/Co matrix).

### Processing route

1. VIM + ESR (vacuum induction melting + electroslag remelting)
2. Solution treatment **900 °C / 1 h**, oil quench (Q)
3. Cryogenic **–73 °C / 1 h**, air warm (gives "Q-C" baseline)
4. **Ageing 482 °C** for **1 h, 5 h, 16 h, 32 h, 100 h, 150 h** — the principal independent variable

### Characterization toolkit (transferable to our M54 work)

- SEM: Zeiss Supra 55
- XRD: Bruker AXS D8 (Cu Kα), 40–105°, step 0.01°. Modified Miller for V_γ; modified Williamson–Hall for ρ.
- TEM: FEI Talos F200X w/ EDS; 50 µm twin-jet electropolished in 10% HClO₄ / 90% C₂H₅OH at –30 °C
- McCall–Boyd (1969) for precipitate volume fraction from dark-field TEM
- Vickers HV0.5 (500 gf, 10 s dwell)
- Tensile per GB/T 228.1-2021, Ø5 × 30 mm gauge, ε̇ = 5×10⁻⁴ s⁻¹, Instron 8501
- Charpy V-notch per GB/T 229-2020, 55 × 10 × 10 mm³, MTS ZBC 230, **instrumented** load-displacement (separates W_i / W_p)
- Hopkinson bar compression at ε̇ ≈ 2000 s⁻¹ for high-strain-rate response

---

## 3. Key Concepts & Takeaways

### 3.1 The dual-precipitation thesis

- **NiAl (B2-ordered, BCC, a ≈ 0.2866 nm)** is fully coherent with α′ martensite (Δa < 0.5 %). Low nucleation barrier → rapid nucleation, **high number density**, **slow coarsening**. Sub-stoichiometric clusters initially; reach ~stoichiometric over time.
- **M2C (hexagonal, M = Cr/Mo)** has different crystal structure than BCC matrix → heterogeneous nucleation on dislocations/2nd-phase sites, slower nucleation, **lower density**, **faster coarsening**.
- The "dual precipitation" payoff: NiAl saturates first (≤5 h) → big YS jump. M2C catches up later (16–32 h) → sustains YS during second peak while NiAl coarsens.

### 3.2 The mechanism map (Table-like summary across ageing time)

| Ageing | Dominant strengthener | Toughness behavior | Notes |
|--------|----------------------|--------------------|-------|
| Q-C (no age) | dislocation ρ (4.73 × 10¹⁵ m⁻²) | low Akv2 | high YS from dislocation forest, not precipitates |
| **5 h** | **NiAl (saturated, r = 1.10 nm, N = 3.52 × 10²³ m⁻³)** + dislocation | Akv2 = 17 J (poor) | first YS peak 1875 MPa; UTS peak 2183 MPa |
| 16 h | NiAl coarsening + M2C developing | Akv2 = 26.2 J | YS = 1853 MPa |
| **32 h** | **M2C + NiAl** dual peak | Akv2 = 28 J (+65 %) | second YS peak 1895/1896 MPa, UTS 2088; **comparable to AerMet 310** at 36 % less raw-material cost |
| 100 h | M2C coarsening; reversed austenite ↑ | Akv2 ≈ 29.8 J | YS drifts down; film-like reversed γ grows from 15.8 → 36.4 nm |

### 3.3 Toughening narrative

- **Crack initiation** (W_i, before peak load): suppression by uniform plasticity at crack tip, which is enabled when M2C is dense enough to support cross-slip rather than NiAl-induced planar slip. (W_i increases 16.4 → 25.4 J, 5h→32h.)
- **Crack propagation** (W_p, after peak load): driven by (a) lower density of brittle NiAl → fewer cleavage facets / micro-crack nucleation sites; (b) **film-like reversed austenite at lath boundaries** (15.8 nm at 32 h, 36.4 nm at 100 h) → crack deflection and/or **stress-induced austenite→martensite transformation** with volume expansion (TRIP-style stress relief). This is where Patel-Cohen physics enters the picture, although Zhu does not write the Patel-Cohen criterion explicitly.

### 3.4 Cost narrative (Fig. 2d)

| Steel | Raw-material cost (USD/t) | Δ vs AerMet 310 |
|-------|---------------------------|-----------------|
| AF1410 | ~7800 | — |
| AerMet 100 | ~8000 | — |
| **M54** | ~6800 | –17 % vs AerMet 310 |
| **Zhu 482 °C / 32 h** | ~5700 | **–36 %** vs AerMet 310 |
| AerMet 310 | ~9100 | baseline |
| AerMet 340 | ~9500 | — |

---

## 4. Equations (full catalog with variables)

> All numbered exactly as in the paper. Use these as the canonical reference for our model implementation.

### Eq. (1) — Retained-austenite volume fraction (Modified Miller, ref [21])

$$ V_\gamma = \frac{1.4\,I_\gamma}{I_\alpha + 1.4\,I_\gamma} $$

- I_α = integrated intensity of martensite peaks (200, 211)
- I_γ = integrated intensity of austenite peaks (200, 220)

### Eq. (2) — Modified Williamson–Hall, dislocation density (ref [22])

$$ \Delta K \approx \frac{0.9}{D} + b A^2 \left(\frac{\pi \theta^2}{2}\right)^{1/2} K\,\bar{C}^{1/2} $$

where:
- ΔK = 2 Δθ cosθ / λ (peak width converted to reciprocal space)
- K = 2 sinθ / λ
- D = crystallite size
- b = Burgers vector
- A = constant
- ρ = dislocation density (extracted)
- C̄ = average dislocation contrast factor
- (110)_α, (200)_α, (211)_α, (220)_α peaks used

### Eq. (3) — McCall–Boyd volume fraction from dark-field TEM (ref [23])

$$ f = \left(\frac{1.4\,\pi}{6}\right) \left(\frac{n\,D^2}{S}\right) $$

- n = number of particles
- D = mean diameter
- S = area of the chosen TEM region

### Eq. (4) — Number density from f and equivalent radius

$$ N = \frac{3 f}{4 \pi \bar{r}^3} $$

- r̄ = equivalent radius of precipitates

### Eq. (5) — M2C / matrix lattice misfit

$$ \delta = 2\,\frac{d_{M_2 C} - d_\alpha}{d_{M_2 C} + d_\alpha} $$

Observed values: **δ = 2.5 %** (5 h), increases to **4.7 %** by 32 h, stays **<5 %** at 100 h → M2C remains coherent through the second YS peak.

### Eq. (6) — Total yield strength sum (rule of mixtures)

$$ \sigma_Y = \sigma_0 + \sigma_{ss} + \sigma_{H\text{-}P} + \sigma_\rho + \sigma_p $$

- σ_0 ≈ **50 MPa** (intrinsic friction stress for secondary hardening steels, ref [12])
- Note: Zhu uses a **purely linear sum** — no in-quadrature combination at the top level. (The C64 paper from our cited-by set uses (σ_d² + σ_p²)^½ instead — be aware of this difference when comparing.)

### Eq. (7) — Solid-solution strengthening (Fleischer, ref [37])

$$ \sigma_{ss} = \left(\sum_i \beta_i^2\,x_{i,\alpha}\right)^{1/2} $$

- x_{i,α} = atomic fraction of substitutional element i in the martensite matrix
- β_i = strengthening coefficient (MPa) capturing lattice + modulus mismatch
- Per **Table 3** of the paper:

  | Element | Co  | Ni    | Cr    | Mo    | Al  |
  |---------|-----|-------|-------|-------|-----|
  | β_i (MPa) | 200.0 | 405.8 | 174.0 | 953.5 | 196 |

- Matrix at% remaining after precipitation (Table 3):
  - 5 h:  Co 4.87, Ni 8.83, Cr 2.51, Mo 0.36, Al 0.52
  - 32 h: Co 4.84, Ni 8.14, Cr 2.33, Mo 0.35, Al 0.51

- The paper explicitly **neglects C solid-solution strengthening** in martensite for secondary hardening steels because C drops to ~0.0033 wt% after M2C consumption (ref [39]).

### Eq. (8) — Hall–Petch / lath strengthening (refs [37,41])

$$ \sigma_{H\text{-}P} = K_{H\text{-}P}\,d^{-1/2} $$

- K_{H-P} ≈ **300 MPa·µm¹ᐟ²**
- d = **average lath spacing**, not block/packet: 0.239 µm at 5 h, 0.242 µm at 32 h
- ⇒ σ_{H-P} ≈ 607 MPa (5 h), 552 MPa (32 h) per Fig. 10 contribution chart

### Eq. (9) — Dislocation strengthening (Bailey–Hirsch, ref [42])

$$ \sigma_\rho = \alpha\,M\,G\,b\,\sqrt{\rho} $$

- α = **0.25**
- M = **2.5** (Taylor factor)
- G = **80 GPa** (matrix shear modulus)
- b = **0.25 nm** (Burgers vector)
- ρ = dislocation density (m⁻²)
- ρ_{Q-C} = 4.73 × 10¹⁵ m⁻² → ρ_{5h} = 2.36 × 10¹⁵ → continues to drift down
- ⇒ σ_ρ = 755 MPa (5 h), 700 MPa (32 h estimate from Fig. 10)

### Eq. (10) — Order strengthening (NiAl shearing, APB cutting; refs [14,43])

$$ \sigma_{order} = \frac{M\,\gamma_{apb}^{3/2}}{b} \left(\frac{4\,r_s\,f}{\pi\,T_l}\right)^{1/2} $$

- γ_apb = antiphase boundary energy of NiAl
- r_s = √(2/3)·r̄ (average radius of particles in the glide plane)
- r̄ = average radius
- f = volume fraction of NiAl
- T_l = Gb²/2 (dislocation line tension)
- ΔG = (G_NiAl − G_matrix), G_NiAl = **88 GPa**

### Eq. (11) — Modulus mismatch strengthening (NiAl; refs [14,43])

$$ \sigma_{modulus} = \frac{M\,\Delta G}{4\pi^2}\left(\frac{3\,\Delta G}{G\,b}\right)^{1/2}\left[0.8 - 0.143\,\ln(r/b)\right]^{3/2} r^{1/2} f^{1/2} $$

### Eq. (12) — Coherency strengthening (NiAl; refs [14,43])

$$ \sigma_{coherency} = 4.1\,M\,G\,\delta^{3/2}\,f^{1/2}\left(\frac{r}{b}\right)^{1/2} $$

- δ = NiAl/matrix lattice misfit (~0.5 %, from cluster lattice parameter near matrix value)

### Eq. (13) — Ashby–Orowan (M2C bypass; ref [45])

$$ \sigma_{M_2 C} = 0.26\,\frac{G\,b}{r_{M_2 C}}\,f_{M_2 C}^{1/2}\,\ln\!\left(\frac{r_{M_2 C}}{b}\right) $$

- r_{M_2C} = ∛((3 (l/2)²·w)/4) — **equivalent radius** from M2C length l and width w
- f_{M_2C} = M2C volume fraction
- **M2C is treated as non-shearable** throughout (the paper cites ref [44] — Wen et al. 2024).

### Eq. (14) — Pythagorean addition for total precipitation strengthening (ref [14,46])

$$ \sigma_p = \sqrt{\sigma_{NiAl}^{\,2} + \sigma_{M_2 C}^{\,2}} $$

- σ_{NiAl} = max(σ_order, σ_coherency, σ_modulus) — usually the dominant of the three is chosen as the "shearing" contribution. Note: the paper does not write this max() rule explicitly; convention from refs [14,43] is to take the dominant term.

### Critical radius for NiAl shearing→looping transition

- **r_c = 3.8 nm** (cited from ref [47] — Yang 2023)
- All observed NiAl radii (1.10 → 1.61 nm across 5–100 h) are **sub-critical** ⇒ NiAl always shearable; M2C always Orowan-bypassed.

---

## 5. Numerical contributions to YS (Fig. 10, MPa)

| Component | 5 h | 32 h |
|-----------|-----|------|
| σ_0 (friction) | 50 | 50 |
| σ_ss (Fleischer) | (lumped) 393 with σ_NiAl portion of σ_p | (lumped) 465 |
| σ_H-P (lath) | 607 | 552 |
| σ_ρ (dislocation) | 755 | 817 |
| σ_p_total | 852 (= σ_NiAl 393 + σ_M2C ≈ √(393² + σ_{M2C}²); see Fig. 10 stack) | **950** |
| **σ_Y,calc total** | **1898** | **1935** |
| σ_Y,test | 1875 | 1896 |

> Reading Fig. 10 carefully: the stacked bars label σ_NiAl = 393 MPa (5 h) and σ_NiAl+M2C aggregate = 950 MPa (32 h). At 5 h, M2C contribution is essentially zero (M2C still too few/small). At 32 h, M2C contributes the +98 MPa increment that recovers YS even as dislocation density drops. **This is the dual-precipitation magic.**

---

## 6. Figures (captions, what they tell us)

- **Fig. 1** — Vickers HV0.5 vs ageing time at 482 °C. Sharp rise from Q-C ~540 HV to **peak ≈ 640 HV at ~5 h**, then monotonic decay. Note absence of true secondary peak in hardness — secondary peak is visible only in YS.
- **Fig. 2** — (a) UTS / YS / EL vs ageing time, showing **first YS peak at 5 h (1875 MPa)** and **second YS peak at 32 h (1896 MPa)**; (b) Akv2 vs ageing time, asymptotic rise to ~30 J; (c) Akv2 vs YS scatter plot benchmarking against AF1410, AerMet 100, AerMet 310, AerMet 340, M54 — our 482 °C/32 h sits on the Pareto front; (d) raw-material cost bar chart with **–36 %** advantage over AerMet 310.
- **Fig. 3** — Instrumented Charpy load–displacement at 5/16/32/100 h, partitioning Akv2 into W_i (crack initiation) and W_p (crack propagation). Key insight: W_i dominates Akv2 (>85 %) at all conditions; the 32 h improvement is mostly W_i.
- **Fig. 4** — SEM fractographs at 5/16/32/100 h. Cleavage facet area fraction decreases with ageing; dimple size increases.
- **Fig. 5** — SEM microstructure at Q-C, 5/16/32/100 h. Distinct lath martensite by 5 h; **bright film-like phase visible at lath boundaries by 32 h**; this is reversed austenite.
- **Fig. 6** — (a) XRD patterns; (b) bar chart of V_γ and ρ vs ageing time. V_γ rises from 1.4 vol% (Q-C) → 2.58 vol% (32 h) → 4.80 vol% (100 h). ρ drops from 4.73 × 10¹⁵ → 2.36 × 10¹⁵ m⁻².
- **Fig. 7** — TEM bright-field + Ni EDS map of reversed austenite films at lath boundaries. Film thickness **15.8 ± 2.8 nm (32 h) → 36.4 ± 4.5 nm (100 h)**; Ni-enriched.
- **Fig. 8** — TEM at 5 h: needle M2C along [100] (zone [001]_α), **δ = 2.5 %** at coherent interface; spherical NiAl with B2 superlattice spots in SADP.
- **Fig. 9** — TEM at 32 h: M2C grown, EDS shows Cr (g₁ map) and Mo (g₂) enrichment; NiAl shows Ni and Al enrichment; HRTEM (g₂) gives **δ = 4.7 %** for M2C at 32 h.
- **Fig. 10** — **The key strengthening-contribution bar chart**. 5 h vs 32 h stacked bars: σ_NiAl (393 → 465), σ_M2C (—  → ~485), σ_H-P (607 → 552), σ_ρ (755 → 817), σ_ss + σ_0 (~393 / ~465 lumped), total 1898 / 1935 calculated vs 1875 / 1896 tested.
- **Fig. 11** — Cross-sectional fractography at 5 h vs 32 h: crack propagation distance 147 → 153 µm; crack-tip plastic zones; **secondary cracks abundant at 5 h, fewer at 32 h** (because brittle NiAl crack-nucleation sites are diluted by coarsening).
- **Fig. 12** — Hopkinson-bar true stress–true strain at 2000 s⁻¹: 5 h sample shows higher compressive flow stress than 32 h sample (more short-range obstacles → phonon drag effect). Relevant if our model needs strain-rate sensitivity.

---

## 7. Tables

- **Table 1** — Chemical composition (wt%): C 0.25, Co 5, Ni 11, Cr 3, Mo 1.5, Al 1.
- **Table 2** — Precipitate characteristics vs ageing time:

  | Time | M2C L (nm) | M2C W (nm) | N_{M2C} (10²³ m⁻³) | f_{M2C} (%) | r_{NiAl} (nm) | N_{NiAl} (10²³ m⁻³) | f_{NiAl} (%) |
  |------|------------|------------|---------------------|-------------|---------------|---------------------|--------------|
  | 5 h   | 7.80 ± 1.02  | 1.61 ± 0.60 | 9.63 ± 0.52 | 1.53 ± 0.35 | 1.10 ± 0.24 | 3.52 ± 0.82 | 1.96 ± 1.28 |
  | 16 h  | 9.15 ± 1.52  | 2.02 ± 0.40 | 6.82 ± 0.31 | 1.24 ± 0.43 | 1.24 ± 0.22 | 2.45 ± 0.32 | 1.98 ± 0.43 |
  | 32 h  | 11.45 ± 1.52 | 2.65 ± 0.42 | 4.69 ± 0.24 | 2.96 ± 0.58 | 1.37 ± 0.32 | 1.05 ± 0.30 | 2.01 ± 0.25 |
  | 100 h | 15.48 ± 1.58 | 3.61 ± 0.51 | 4.42 ± 0.22 | 2.98 ± 0.58 | 1.61 ± 0.38 | 1.05 ± 0.30 | 2.03 ± 0.25 |

  > Note: M2C is rod-shaped; NiAl is spherical. Direct r_{M2C} comparison requires Eq. (13)'s equivalent radius.

- **Table 3** — Solid-solution composition (at%) and β_i coefficients (above).

---

## 8. Implications for our Ferrium M54 (ausformed, 516 °C/10 h) model

1. **Equation set is directly transferable.** Eqs. (6)–(14) define a complete σ_Y decomposition that maps onto M54 — but we must:
   - Replace the NiAl population with M54's η-phase / Ni₃(Ti,Al)-type precipitates if present (M54 has no Al in nominal spec; check Mondiere 2018 for actual minor-phase chemistry).
   - Keep the M2C term, which is the dominant secondary hardener in M54.
   - Add an MC carbide term (V- and possibly W-bearing) — M54 has V (0.3 wt%) and W (1.3 wt%) that Zhu's alloy lacks.

2. **The Pythagorean precipitate-sum (Eq. 14)** vs **linear sum (Eq. 6)** at the top level is a recipe choice. C64 paper from the cited-by set uses (σ_d² + σ_p²)^½ at the top. We will need to pick one and stay consistent — recommend Zhu's linear-sum-at-top + Pythagorean-within-precipitation, since it follows ref [14] (Xiong 2021 Prog. Mater. Sci.), a senior reference in the field.

3. **Ausforming** is **not** treated in Zhu — Zhu's alloy is solution-quenched, not deformed prior to ageing. We need a dislocation-density input that reflects M54's deformed state. Sun 2022 (ausformed-tempered M54) should give us ρ values for the as-deformed condition; expect ρ ≫ 4.73 × 10¹⁵ m⁻² (Zhu's Q-C baseline). Also, ausforming will refine laths d, raising σ_{H-P}.

4. **Tempering at 516 °C / 10 h** is in the same regime as Zhu's 482 °C / 5–16 h band — high M2C density, M2C coherent (δ < 5 %), NiAl/Ni₃(Ti,Al) sub-critical (shearable). Expect M54 behavior in this regime to follow the 5–16 h Zhu pattern (NiAl-dominated YS, low-to-moderate impact).

5. **Reversed austenite term** at lath boundaries will likely matter at 516 °C / 10 h for M54 — Sun 2022 reports an analogous film-like reversed-γ formation. We should plan an austenite-fraction-modified YS option, like the C64 paper's (1 – f_A)·σ_M + f_A·σ_A construction.

6. **Patel-Cohen criterion enters via the toughening pathway**, not the YS sum. To use Patel-Cohen, we will need: chemical free energy ΔG_chem(T), σ-applied resolved on habit plane (Patel-Cohen mechanical driving force U), and the criterion U + ΔG_chem ≤ –ΔG_crit. This isn't in Zhu's paper text but is consistent with Zhu's qualitative claim about stress-induced γ→α′ at the crack tip.

7. **Cost reduction is not our primary objective** — we are modeling an existing alloy (M54) at a specific known temper. Skip the cost calculation. Keep the strengthening physics.

---

## 9. Reference list overview (52 refs — full citation chart in `/references/citation-chart.md`)

Reference clusters at a glance:
- **Refs 1, 5–12, 25–27, 35**: secondary hardening / UHSS background (M54, AerMet, AF1410, 300M, AerMet 310, AerMet 340 family, QuesTek patents). High-priority for our M54 work.
- **Refs 2, 7, 12, 41**: explicit M54 papers. **Must-have** for the model. Ref 7 is **Mondiere 2018 (M54 MC/M2C balance)** — the user has already flagged this. Ref 41 is **Wang 2024 (M54 multi-carbide evolution)** — likely critical.
- **Refs 14, 16, 37, 38, 39, 43, 44, 46**: strengthening-equation provenance (Xiong, Grujicic, Niu, Wang, Ghosh-Olson, Zhou, Wen). These define our equation pedigree.
- **Refs 13, 17, 19, 27, 47**: NiAl- and Cu-cluster strengthening corollaries.
- **Refs 21, 22, 23**: experimental quantification methods (Miller, Williamson-Hall, McCall-Boyd).
- **Refs 28–31, 36**: reversed austenite physics (Jacques, Kumar-Singh, Feitosa, Gruber, Oh). Important for our 516 °C / 10 h M54 case.
- **Refs 34, 49–51**: high-strain-rate / dynamic response. Lower priority unless we extend to dynamic loading.
- **Refs 32, 33, 40, 42, 45, 48, 52**: classical/seminal references (Hall 1951, Bailey-Hirsch 1960, Gladman 1999, etc.).
