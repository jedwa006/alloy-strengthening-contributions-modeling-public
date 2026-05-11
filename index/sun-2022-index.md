# Sun et al. 2022 — Ausforming and Tempering of M54

> **Author note:** This paper is **co-authored by the user (Joshua Edwards)** while at UC Riverside, alongside the QuesTek team (Lin, Kozmel) and the Mathaudhu group. Treat it as the user's own work and the canonical source for the target M54 condition this project is modeling.

---

## 1. Bibliographic Header

- **Title:** Ausforming and tempering of a novel ultra-high strength steel
- **Authors:** Yiwei Sun (a), Johny Quan (a), Heather Salvador (a), **Joshua Edwards (c)**, Jeffrey Lin (b), Thomas Kozmel (b), Suveen Mathaudhu (a, c, corresp. — smathaudhu@mines.edu)
- **Affiliations:**
  - (a) Department of Mechanical Engineering, UC Riverside, CA
  - (b) **QuesTek® Innovations LLC**, Evanston, IL — the alloy designers themselves
  - (c) Metallurgical and Materials Engineering Department, Colorado School of Mines, CO
- **Journal:** Materials Science & Engineering A, **838** (2022) 142750
- **DOI:** [10.1016/j.msea.2022.142750](https://doi.org/10.1016/j.msea.2022.142750)
- **Received:** 15 Oct 2021 | **Revised:** 26 Jan 2022 | **Accepted:** 27 Jan 2022 | **Online:** 4 Feb 2022
- **Funding:** US Army DEVCOM Soldier Center + SBA SBIR, Contract W911QY-18-C-0127
- **License:** © 2022 Elsevier B.V. All rights reserved.

---

## 2. Alloy and processing — the target conditions for our model

### Composition (Table 1, wt%) — same as nominal Ferrium M54

| Fe | C | Co | Cr | Ni | Mo | W | V |
|----|---|----|----|----|-----|-----|-----|
| bal | 0.3 | 7 | 1 | 10 | 2 | 1.3 | 0.1 |

> Confirms the M54 composition we're modeling. V is 0.1 wt% (Zhu's alloy has none — Zhu cannot calibrate the MC term). W is 1.3 wt% (drives M6C primary carbides → 1060 °C austenitization).

### Processing tree explored in the paper

| Step | Treatments |
|------|------------|
| 1. Austenitization | **1060 °C / 1 h** (also solutionizes for downstream precipitation hardening) |
| 2. Ausforming (rolling, single pass) | Temps: 550 / 650 / 750 °C; Reductions: 30 / 45 / 60 % |
| 3. Oil quench | — |
| 4. Cryogenic | **liquid N₂ (~–196 °C) / 1 h** (note: deeper than the –73 °C dry-ice used by Zhu) |
| 5. Temper | 516 / 425 / 350 °C, up to **48 h** |

### Naming convention used throughout

- `DQ` — direct-quenched (no ausforming), conventional baseline
- `AF550/45` — ausformed at 550 °C with 45 % reduction
- `AF550/45 + T425/10` — also tempered at 425 °C for 10 h
- `DQ + T516/10` — the **conventional commercial M54 temper** (10 h at 516 °C)

### The condition the project is modeling

The user's stated target is **M54 ausformed and tempered at 516 °C / 10 h**. But Sun 2022's downselect is **AF550/45 + T425/10** (lower-T temper, time-equivalent to the conventional 516/10 due to ausforming-accelerated kinetics). The paper finds the conventional **DQ + T516/10** still gives 1762 MPa YS / 2050 MPa UTS / 14.9 % EL; ausforming-then-T425/10 gives **1726 MPa YS / 2222 MPa UTS / 15.5 % EL** — slightly lower YS, but +172 MPa UTS and +0.6 pp elongation.

**For the model**, we'll likely want to support both reference conditions:
- **DQ + T516/10** (conventional commercial M54): the standard baseline
- **AF550/45 + T425/10** (ausformed + lower-T temper): the user's enhanced processing route from this paper

---

## 3. Mechanical properties (Table 3) — the key benchmarks

| Condition | YS (MPa) | UTS (MPa) | EL % |
|-----------|---------:|----------:|-----:|
| AF550/45              | 1830 | 2291 | 14.4 |
| AF550/45 + T425/10    | **1726** | **2222** | **15.5** |
| DQ                    | 1420 | 1916 | 14.9 |
| **DQ + T516/10**      | **1762** | **2050** | **14.9** |

**Other reported M54 reference numbers (from text):**
- Conventional commercial spec: **54 HRC ≈ 618 HV**, K_IC ≈ **126 MPa·m^½** (cited from QuesTek/NAVAIR Tech Memo)
- Peak DQ+T516/10 hardness in this study: 618 HV at 10 h
- AF550/45 untempered hardness: 659 HV; +T425/10 peak: 629 HV; +T350/7 peak: 636 HV
- **The 516 °C DQ curve shows a secondary peak structure** — small peak at 3 h (606 HV) before main peak at 10 h (618 HV). Sun notes the 3 h peak is still unexplained, attributed to multiple competing carbide precipitation mechanisms; flags as future work.

---

## 4. Microstructure (Table 2)

| Condition | PAG width (µm) | Packet size (µm) | Block width (µm) |
|-----------|--------------:|-----------------:|------------------:|
| DQ                  | 100  | 13.1 | 1.18 |
| AF550/30            | 63   | 6.6  | 0.65 |
| AF550/45            | 47   | 6.7  | 0.48 |
| AF550/60            | 32   | 7.8  | 0.31 |
| AF650/45            | 49   | 8.4  | 0.53 |
| AF750/45            | 45   | 8.2  | 0.58 |

> Block width is the relevant length scale for Hall-Petch in lath martensite — and it varies by ~4× between DQ and AF550/60. **This is the dominant geometric strengthening lever for our model.**

### TEM features (Fig. 3)
- Lath width 70–200 nm (smaller than other martensitic UHSS reviewed at 270–500 nm)
- **Nano-scale lamellar features within laths — likely twinning** (Fig. 3e,f). Not quantified, but flagged as a strengthening contribution beyond block-size + dislocation.

---

## 5. Dislocation densities (Williamson–Hall, XRD)

| Condition | ρ (× 10¹⁵ m⁻²) |
|-----------|---------------:|
| AF550/45 (cryo)         | **7.81** |
| AF550/45 + T425/10      | 1.18 |
| DQ (cryo)               | 2.08 |
| DQ + T516/10            | 1.12 |

> Two huge takeaways:
> 1. **Ausforming gives 3.75× the dislocation density of DQ** before tempering.
> 2. **After tempering both conditions converge to ~1.1–1.2 × 10¹⁵ m⁻²**. The ausforming bonus in dislocation density is largely erased by recovery during tempering — but the **block-size refinement persists**.

---

## 6. Strengthening Equation (Eq. 1 in Sun 2022)

$$ \sigma = \sigma_0 + \sigma_s + \sigma_p + k_{HP}\,d^{-1/2} + \alpha\,G\,b\,\sqrt{\rho} $$

Sourced from ref **[20]** (G. Krauss, "Martensite in steel: strength and structure," MSEA 1999 — DOI [10.1016/S0921-5093(99)00288-9](https://doi.org/10.1016/S0921-5093(99)00288-9)).

### Variables and constants used in Sun 2022

- σ₀ = friction stress for pure iron
- σ_s = solid-solution strengthening
- σ_p = precipitation strengthening (M2C in our case)
- k_HP = Hall-Petch coefficient
- d = HAGB spacing = **martensite block size** (per ref [21] Galindo-Nava & Rivera-Díaz-Del-Castillo 2015)
- α = **0.38** (per ref [23] Bhadeshia & Honeycombe, *Steels* 3rd ed.) ← **differs from Zhu's 0.25**
- G, b = matrix shear modulus, Burgers vector

### k_HP fitted from this study (Fig. 7)

Hall-Petch plot of strength (from HV ≈ 3σ/9.81 conversion) vs d^(-1/2) gives:

**k_HP = 0.23 MPa·m^½ ≈ 230 MPa·µm^½**

(Note units conversion: 0.23 MPa·m^½ = 0.23 × √(10⁶) MPa·µm^½ = 230 MPa·µm^½.)

This is **~23 % lower than Zhu/Li's 300 MPa·µm^½** — pick a side carefully when implementing the model. The discrepancy may come from (a) HV-to-σ proxy used here vs direct tensile in Zhu/Li, (b) M54 vs different-composition test material, or (c) block-size vs lath-spacing being used as d.

### Quantitative strengthening decomposition (Sun's analysis, AF550/45 vs DQ)

Contribution to YS difference between AF550/45 and DQ:
- **Block-size strengthening:** +120 MPa (block 1.18 → 0.48 µm)
- **Dislocation strengthening:** +314 MPa (ρ 2.08 → 7.81 × 10¹⁵ m⁻²)
- **Sum:** 434 MPa
- **Measured ΔYS:** 410 MPa ✓ (good agreement)

Dislocation strengthening loss after tempering:
- DQ → DQ+T516/10: ~89 MPa lost from dislocation recovery
- AF550/45 → AF550/45+T425/10: **~397 MPa lost** (most of the ausforming dislocation gain is recovered out)

> The **net ausforming benefit after tempering** is mostly from the **persisting block refinement**, not from the dislocation density (which converges). Precipitation strengthening from M2C is invoked qualitatively but **not quantified** in Sun 2022 — that's the gap our model fills.

---

## 7. Discussion highlights

### 7.1 Microstructure refinement
- **Larger effective PAG boundary area** from ausforming-elongated PAGs + sub-grain boundaries (refs [13,17])
- **Promotion of self-accommodation** over plastic accommodation during martensitic transformation, due to strain-hardened PAGs (ref [18])
- Reduction > Temperature effect on block size (60 % reduction halves block width vs DQ; T 750→550 °C only trims ~17 %)
- **High Co (7 wt%) suppresses recovery** during ausforming → minor T effect (refs [6,25])

### 7.2 Tempering kinetics — ausforming-accelerated precipitation
- Ausforming → higher dislocation density → more nucleation sites for M2C → **lower T or shorter time to peak**
- Peak hardness times observed:
  - DQ @ 516 °C: 10 h (conventional)
  - DQ @ 425 °C: 3 h smaller peak; even after 48 h, hasn't fully reached the 516 °C / 10 h equivalent peak
  - DQ @ 350 °C: 7-10 h smaller peak
  - **AF @ 516 °C: 5 h** (peak brought forward from 10 h → 5 h)
  - AF @ 425 °C: 10 h peak (slight effect)
  - AF @ 350 °C: 7 h peak
- The 3-h hardness sub-peak in DQ @ 516 °C is **unexplained** in Sun 2022 — flagged as needing further investigation of M2C thermodynamics/kinetics. This is a potential modeling-question for our project.

### 7.3 Tempering trade-offs
- DQ: tempering **adds 338 MPa YS** from M2C precipitation, prevails over matrix softening.
- AF: tempering **subtracts 104 MPa YS** because dislocation recovery dominates, but +1.1 pp elongation.
- The ausformed-and-tempered specimen has the **best UTS-elongation balance** of all conditions tested.

---

## 8. References in Sun 2022 (28 refs — most relevant for our model)

Verbatim from the paper's ref list:

- [1] Lee et al., *Aircraft steels*, 2009 — DTIC ADA494348 (open-access US government)
- [2] C. Wang et al., *Microstructural refinement & toughness of low-C martensitic steel*, Scr. Mater. 2008 — [10.1016/j.scriptamat.2007.10.053](https://doi.org/10.1016/j.scriptamat.2007.10.053)
- [3] Chatterjee et al., *Hierarchical martensite & impact toughness in 9Cr-1Mo*, Int. J. Plast. 104 (2018) 104-133 — [10.1016/j.ijplas.2018.02.002](https://doi.org/10.1016/j.ijplas.2018.02.002)
- [4] Kitahara et al., *Crystallographic features of lath martensite*, Acta Mater. 54 (2006) 1279-1288 — [10.1016/j.actamat.2005.11.001](https://doi.org/10.1016/j.actamat.2005.11.001)
- **[5] H.J. Jou, *Lower-cost, Ultra-high-strength, High-Toughness Steel*, US Patent 9,051,635 B2 (2015)** — same as Zhu ref [26]; the M54 foundational patent.
- [6] Gao et al. 2019 — same as Zhu ref [9]
- [7] Lee/Stanley/Pregger/Lei, *Technical Information Memorandum*, Patuxent River, MD, 2015 — Navy tech memo, source of the M54 K_IC = 126 MPa·m^½ value
- **[8] Mondière et al. 2018** — same as Zhu ref [7]; OA on HAL
- [9] Seo et al., *Ausforming medium-C steel*, Mater. Sci. Technol. 31 (2015) — [10.1179/1743284714Y.0000000574](https://doi.org/10.1179/1743284714Y.0000000574)
- [10] Lv et al., *Ultrafine lamellar martensitic steel by warm rolling + tempering*, MSEA 2018 — [10.1016/j.msea.2018.06.073](https://doi.org/10.1016/j.msea.2018.06.073)
- **[11] Cho et al., *M2C precipitation kinetics in ausformed 13Co-8Ni steels***, Metall. Mater. Trans. A 46 (2015) 1535-1543 — [10.1007/s11661-015-2750-6](https://doi.org/10.1007/s11661-015-2750-6) — **HIGH PRIORITY for our model: this is the precipitation-kinetics analog for ausformed Co-Ni**
- [12] QuesTek, *Ferrium M54 Datasheet*, 2015 — http://www.cartech.com (likely www.questek.com/ferrium-m54 today)
- [13] Cho et al., *Rolling T effect on Co-Ni 0.28C steel*, MSEA 2010 — [10.1016/j.msea.2010.07.069](https://doi.org/10.1016/j.msea.2010.07.069)
- [14] Seifert et al., *Hardness & microstructure of stainless after ausforming*, Steel Res. Int. 88 (2017) — [10.1002/srin.201700010](https://doi.org/10.1002/srin.201700010)
- [15] S. Li et al., *Substructure effect on lath martensite in 0.1C-1.1Si-1.7Mn*, J. Alloys Compd. 675 (2016) — [10.1016/j.jallcom.2016.03.100](https://doi.org/10.1016/j.jallcom.2016.03.100)
- [16] S.L. Long et al., *Quench T on martensite multi-level structure in 20CrNi2Mo*, MSEA 676 (2016) — [10.1016/j.msea.2016.08.065](https://doi.org/10.1016/j.msea.2016.08.065)
- [17] Prawoto & Jasmawati, *PAG size on martensite morphology in medium-C*, J. Mater. Sci. Technol. 28 (2012) 461-466
- [18] Shigeta et al., *Ausforming on variant selection in Cr-Mo*, Q. J. Jpn. Weld Soc. 31 (2013) 178s-182s — [10.2207/qjjws.31.178s](https://doi.org/10.2207/qjjws.31.178s)
- [19] Morito et al., *Block size on lath martensite strength*, MSEA 2006 — [10.1016/j.msea.2005.12.048](https://doi.org/10.1016/j.msea.2005.12.048)
- **[20] G. Krauss, *Martensite in steel: strength and structure*, MSEA 1999** — [10.1016/S0921-5093(99)00288-9](https://doi.org/10.1016/S0921-5093(99)00288-9) — **source of Eq. (1) in Sun 2022; foundational equation reference for our model**
- **[21] Galindo-Nava & Rivera-Díaz-Del-Castillo, *Lath martensite model*, Acta Mater. 98 (2015) 81-93** — [10.1016/j.actamat.2015.07.018](https://doi.org/10.1016/j.actamat.2015.07.018) — **likely critical: provides the d = block-size definition Sun uses**
- [22] Nabarro, Basinski, Holt, *Plasticity of pure single crystals*, Adv. Phys. 13 (1964) — Taylor-hardening original
- [23] Bhadeshia & Honeycombe, *Steels* (3rd ed.) Chapter 14, Butterworth-Heinemann 2006 — α = 0.38 source
- [24] Han et al., *Hot-rolling T on Ti-microalloyed low-C martensitic*, MSEA 2012 — [10.1016/j.msea.2012.06.015](https://doi.org/10.1016/j.msea.2012.06.015)
- **[25] Kuehmann & Olson, *Nanocarbide Precipitation Strengthened Ultrahigh-Strength Corrosion Resistant Structural Steels*, US Patent 7,160,399 (2007)** — **Olson/QuesTek patent — likely the C64/Ferrium-C-family parent IP**
- [26] Bhadeshia & Honeycombe, *Steels* (3rd ed.) Chapter 9 — Tempering of martensite reference
- [27] Speich, Dabkowski, Porter — same as Zhu ref [35]; Fe-10Ni alloys
- [28] J.W. Yoo et al., *M2C precipitates in isothermal-tempered Co-Ni SH steel*, Metall. Mater. Trans. 27 (1996) 3466-3472 — **new ref, important for M2C kinetics in Co-Ni**

---

## 9. Cross-references to Zhu / C64 / cited-by papers

| Sun ref | Same as | Notes |
|---------|---------|-------|
| [5] | Zhu [26] | M54 patent (Jou) — confirms our citation-chart entry |
| [6] | Zhu [9] | Gao 2019 |
| [8] | Zhu [7] | Mondière 2018 |
| [27] | Zhu [35] | Speich 1973 |

New references introduced by Sun 2022 that should join our citation archive:
- Krauss MSEA 1999 (Sun [20]) — equation foundation
- Galindo-Nava & Rivera-Díaz-Del-Castillo Acta Mater 2015 (Sun [21]) — block-size definition for Hall-Petch
- Cho 2015 (Sun [11]) — **ausformed 13Co-8Ni M2C kinetics — directly relevant**
- Kuehmann & Olson US Patent 7,160,399 (Sun [25]) — QuesTek parent IP
- Yoo 1996 (Sun [28]) — M2C in isothermal-tempered Co-Ni
- Lee Tech Memo 2015 (Sun [7]) — source of M54 K_IC = 126 number

---

## 10. Implications for the project

### Calibration anchors we now have for the M54 model

| Quantity | Sun 2022 DQ+T516/10 value | Use |
|----------|---------------------------|-----|
| σ_y      | **1762 MPa**              | YS target for conventional M54 baseline |
| σ_UTS    | 2050 MPa                  | UTS target |
| ε_f      | 14.9 %                    | ductility target |
| Block d  | ~1.18 µm (DQ)             | Hall-Petch d input |
| ρ        | **1.12 × 10¹⁵ m⁻²**       | dislocation strengthening input |
| HV       | 618 HV                    | hardness target |
| K_IC     | 126 MPa·m^½ (commercial)  | toughness anchor (not measured in Sun 2022 itself) |

| Quantity | Sun 2022 AF550/45+T425/10 value | Use |
|----------|--------------------------------|-----|
| σ_y      | **1726 MPa**                   | YS target for ausformed enhanced route |
| σ_UTS    | **2222 MPa**                   | UTS target — note +172 MPa over conventional |
| ε_f      | **15.5 %**                     | ductility target |
| Block d  | 0.48 µm                        | Hall-Petch d input (refined) |
| ρ        | **1.18 × 10¹⁵ m⁻²**            | converged with DQ after tempering |

### Equation choice for the model

Sun 2022 uses a **linear sum** (same as Zhu) with **α = 0.38** (vs Zhu's 0.25) and **k_HP = 230 MPa·µm^½** (vs Zhu's 300). For an M54 model, I'd suggest:

- Adopt Sun's framework as the primary (it's the user's own work + a calibrated M54 study).
- Make α and k_HP configurable constants with defaults from Sun, alternatives from Zhu/Li.
- Add the σ_p term (which Sun does NOT quantify) using Zhu/C64's Pythagorean σ_p = √(σ_M2C² + σ_MC²) formulation. Note **no NiAl term needed in M54** — the alloy has no Al; precipitation is M2C + MC (V-rich), per Sun ref [8] (Mondière).

### Gaps that Sun 2022 leaves open (model targets)

1. **No σ_p quantification.** Sun shows the +338 MPa from precipitation in DQ+T516/10 *implicitly* (as the residual after dislocation/block-size effects) — but doesn't compute M2C contributions from Ashby-Orowan. **Our model can fill this.**
2. **The 3 h sub-peak in DQ @ 516 °C tempering** is unexplained. Could be a transient cementite or pre-M2C state. **Model opportunity** — if we can reproduce the secondary peak using a multi-carbide kinetics framework (cementite → M2C → coarsening), we learn something.
3. **Solid-solution strengthening σ_s** is in Eq. 1 symbolically but not computed; Sun doesn't provide values. Use Zhu's Fleischer β coefficients + Mondière's M2C partitioning data to compute it from first principles.
4. **MC carbide (V-rich) contribution** is not addressed at all in Sun. Mondière 2018 is the source.
5. **Nano-twins** in laths (Fig. 3) are noted but not quantified — potential additional Hall-Petch contribution beyond block-size.
