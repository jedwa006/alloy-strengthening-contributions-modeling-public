# Cited-By Papers — Summaries

> Five papers in `reference docs/Articles that CITE main article/` cite Zhu et al. 2025. They range from highly relevant (Ferrium C64 sister alloy with a near-complete strengthening decomposition) to a clearly misfiled agricultural-machinery review. Triage table at the top.

## Triage at a glance

| # | Short name | File | Relevance | What it gives us |
|---|------------|------|-----------|------------------|
| 1 | **Li 2026 — Ferrium C64 tempering** | `1-s2.0-S1044580326003426-main.pdf` | ★★★★★ | Full strengthening-contribution model on M54's sister alloy. Direct equation recipes + numerical bounds for our M54 model. |
| 2 | **Duan 2025 — NiAl-clusters in 300M-like UHSS** | `1-s2.0-S1044580325007697-main.pdf` | ★★★☆☆ | Independent benchmark for NiAl B2 cluster size, density, misfit, and a K_IC method. Low-T temper, so not directly M54 — but anchor for NiAl population values. |
| 3 | **Zhu 2025 (ESOMAT) — Low-Co solution-treatment study** | `1-s2.0-S2452321625002409-main.pdf` | ★★★★☆ | Same group as the MAIN article. Establishes T_ss optimum (900 °C) and shows how primary-carbide dissolution sets matrix C for ageing. Complements MAIN. |
| 4 | **Wu 2025 — Mg-Gd-Y-Zn-Zr fracture** | `1-s2.0-S0925838825042896-main.pdf` | ★☆☆☆☆ | Tangential. Borrows Zhu only for the generic claim that strain-hardening exponent affects K_IC. Somekawa-style K_IC fit (Eqs. 2-6) might be a sanity check tool. |
| 5 | **Zhang 2025 — Digital twins for agricultural machinery** | `qwaf097.pdf` | ☆☆☆☆☆ | Misfiled. One-sentence courtesy cite. Ignore. |

---

## 1. Li et al. 2026 — Ferrium C64 tempering (★★★★★)

- **Citation:** Huafei Li, Yi Xiong, Yong Li, Xiaoqin Zha, Xiuju Du, YiYi Wang, Fengzhang Ren, Shubo Wang. *Microstructural tailoring for enhanced strength–toughness synergy in Ferrium C64 gear steel via controlled tempering temperature.* Mater. Charact. **235** (2026) 116305. [10.1016/j.matchar.2026.116305](https://doi.org/10.1016/j.matchar.2026.116305)

- **Why critical:** Ferrium C64 is QuesTek's gear-steel sister of M54. Same family (Co-Ni-Mo-Cr secondary hardening), different niche (gear vs structural). C64 here is C 0.095, Ni 7.50, Mo 1.82, Cr 3.48, W 0.23, Co 16.43 — note **higher Co** and **no V/Al/Ti** vs M54 (so no NiAl/MC term needed). The strengthening-decomposition recipe used here is the closest thing in the literature to the framework we are building for M54.

- **Heat treatment matrix:** 1000 °C/1 h oil quench → –73 °C/2 h cryo → temper at **300/430/465/485/495/505/525/560/600 °C × 12 h**.

- **Precipitates identified:**
  - M2C (HCP, Cr+Mo-rich): first appears **430 °C**, peaks **495 °C** (r_e = 3.5 nm, N = 686 µm⁻², f = 5.6 %, spacing 12.4 nm), coarsens at 525+ °C. Lattice misfit δ ≈ 2 % (coherent at peak).
  - M3C (cementite): dominant ≤300 °C; persists at 430 °C as coarse boundary cementite (the 430 °C embrittlement culprit); decomposed by 495 °C.
  - M7C3 (Cr-rich, blocky): appears at 600 °C, 30 nm at grain boundaries — detrimental.
  - Reversed/retained γ: <3 % through 525 °C; **8 % at 560 °C; ~15 % at 600 °C** — needs the (1-f_A)σ_M + f_A·σ_A correction at high T.

- **Strengthening equation set** (Section 4.2): essentially the **same** as Zhu Eqs. (6)–(13), but with two differences worth noting:
  - **Top-level combination is Pythagorean-on-dislocation-and-precipitation:**
    $$ \sigma_Y = \sigma_f + \sigma_{ss} + \sigma_g + \sqrt{\sigma_d^2 + \sigma_p^2} $$
  - **Dislocation term is M2C-aware:**
    $$ \sigma_M = \frac{300}{\sqrt{d}} + 0.25\,M\,\mu\,b\,\sqrt{\rho} $$
    where the first term is the Hall-Petch contribution rolled into σ_M, and the second is Taylor.
  - All carbides treated as **Orowan-only** (assumed non-shearable at all sizes here).

- **Fleischer β coefficients (Table 3):** β_Ni = 405.8, β_Mo = 953.5, β_Cr = 174.0, β_Co = 200.0 MPa — **matches Zhu Table 3 exactly** — confirms a shared lineage from refs [37,38].

- **σ_0 = 50 MPa, M = 2.5, µ = 80 GPa, b = 0.25 nm, σ_A (austenite YS) = 360 MPa** — same constants as Zhu.

- **YS_calc vs YS_exp comparison** (Table 5): rel error from **–10.0 % (430 °C, under-predict)** to **+7.4 % (495 °C, over-predict)** across Q / cryo / 430 / 495 / 600 °C. The framework tends to **over-predict at peak hardening** and **under-predict at no-precipitate states**. This is a useful calibration caveat for our M54 model.

- **For M54 at 516 °C / 10 h:** the closest C64 condition is **505 °C / 12 h** (post-peak, still strong, M2C beginning to coarsen). C64 at this temper shows YS ≈ 1350 MPa, KU2 ≈ 100 J. M54's higher Mo (2.0 vs 1.82) and presence of V/W will modify M2C population and add MC contribution; this is the gap our model fills.

- **Zhu citation context:** [32] in C64 paper. Cited twice — once for "M2C carbide composition agrees with Zhu" and once for the lattice-mismatch formula (Eq. 5 in C64 = Eq. 5 in Zhu). Confirms Zhu's status as the canonical low-Co-secondary-hardening reference.

---

## 2. Duan et al. 2025 — NiAl-toughened low-alloy UHSS (★★★)

- **Citation:** Xiaohan Duan, Xin Cao, Yangxin Wang, Hongshan Zhao, Chundong Hu, Han Dong. *Making low alloy ultrahigh strength steel tough by high-density NiAl clusters.* Mater. Charact. **229** (2025) 115480. [10.1016/j.matchar.2025.115480](https://doi.org/10.1016/j.matchar.2025.115480)

- **Alloys:** 0Al baseline (Fe-0.32C-2Si-1Mn-1Cr-3.4Ni-0.56Mo-0.09V-0.03Al) and 1.3Al (same + Ni→5.1, Al→1.3). VIM+VAR, 970 °C/1 h WQ, **180 °C/2 h temper** — this is a *low-T-tempered* 300M-class steel, NOT secondary hardening.

- **Relevance to our M54 work** is **NiAl benchmarking only**:
  - NiAl is B2-ordered BCC, lattice 0.2882 nm, **misfit ~0.5 %** vs α-Fe
  - r ≈ **0.57 nm** (equivalent), N = **4.88 × 10²⁴ m⁻³** (extremely high density)
  - Sub-stoichiometric Ni-Al at cluster centers (~13 at% Ni vs 50 stoichiometric)
  - These bound the NiAl regime at the **very-early-stage** end (denser, smaller than Zhu's r = 1.1 nm 5 h precipitates).

- **No explicit strengthening decomposition** — paper is a microstructure-toughness study, not a quantitative model paper. Only Eqs. (1) K_IC = (F·S/B·W^1.5)·f(a/W) (ASTM E399) and (2) Williamson-Hall.

- **Numerical benchmarks:** 1.3Al, 180 °C / 2 h: YS = 1272, UTS = 1876, TE = 13.7 %, KU2 = 80 J, **K_IC = 108 MPa·m^½**. Compare to baseline 0Al: 97.6 MPa·m^½. So NiAl adds ~10 MPa·m^½ to K_IC at this composition.

- **Zhu citation:** ref [16], one-line invocation in intro of "dual-precipitation works." No equations borrowed.

---

## 3. Zhu et al. 2025 (ESOMAT) — Solution-treatment study (★★★★)

- **Citation:** Haofei Zhu, Zhiping Xiong, Jianwen Mao, Xingwang Cheng. *Effect of solid-solution temperature on the microstructure and mechanical properties in low-cobalt secondary hardening ultra-high strength steel.* Procedia Structural Integrity **69** (2025) 113–120 (ESOMAT 2024 proceedings, Elsevier). [10.1016/j.prostr.2025.07.016](https://doi.org/10.1016/j.prostr.2025.07.016) (open access, CC BY-NC-ND).

- **Same alloy** as the MAIN article (Fe-0.23C-5Co-11Ni-3Cr-1Mo-1Al) — verify whether this is the C-0.23 variant or C-0.25 variant from MAIN; appears to be a **slightly earlier formulation** (0.23 vs 0.25 C). Same group at BIT.

- **What it adds:** Maps the role of **solution-treatment temperature** (870/900/930/960 °C × 1 h, then cryo at –73 °C/1 h, then age 482 °C/5 h). The MAIN article fixes T_ss at 900 °C and varies ageing time; this ESOMAT paper varies T_ss at fixed ageing.

- **Key findings:**
  - Equilibrium dissolution T of M7C3 primary carbides: **~862 °C** (Thermo-Calc).
  - **T_ss = 900 °C is the optimum** — balances PAG size (~15 µm), residual M7C3 (mostly dissolved), C return to matrix for M2C ageing, and toughness retention.
  - Increasing T_ss coarsens PAG (14.2 → 17.9 µm) and slightly raises reversed austenite (1.52 → 1.98 vol%).
  - **Aged optimum (T_ss = 900 °C, aged 482 °C/5 h):** YS = 1875 ± 4 MPa, UTS = 2185 ± 3 MPa, TE = 13.84 %, Akv2 = **16.2 J** — matches MAIN article's 5 h values almost exactly.

- **Equations:** Only Eq. (1) for V_γ (same modified Miller as MAIN Eq. 1). No strengthening decomposition; mechanisms invoked only qualitatively.

- **Useful comparators for M54 motivation (Sec. 1 of ESOMAT paper):**
  - **300M:** K_IC/YS ≈ 60 MPa·m^½ / 1570 MPa
  - **AerMet 100:** K_IC/YS ≈ 126 / 1724; 13.4 wt% Co; raw material cost ~10× 300M
  - **Ferrium M54:** K_IC/YS ≈ **115 MPa·m^½ / 1723 MPa**; Co cut to 7 wt%; but 1.3 wt% W induces primary M6C → forces T_ss up from 885 to **1060 °C** (higher furnace cost)
  - **New low-Co alloy (this study):** Aged Q-C, T_ss = 900 °C: YS 1875 / UTS 2185 / TE 13.8 / Akv2 16.2 J

- **Action item:** This paper *and* MAIN are companion publications. Index both together. The W-driven 1060 °C T_ss number for M54 is a useful constraint for any Thermo-Calc modeling we do.

---

## 4. Wu et al. 2025 — Mg-Gd-Y-Zn-Zr fracture toughness (★)

- **Citation:** Ang Wu, Zhimin Zhang, Jianmin Yu, Yong Xue, Xueli Wang. *The analysis of fracture toughness and fracture mechanism of Mg-Gd-Y-Zn-Zr alloy under different temperatures.* J. Alloys Compd. **1038** (2025) 182728. [10.1016/j.jallcom.2025.182728](https://doi.org/10.1016/j.jallcom.2025.182728)

- **Tangential.** Mg alloy, HCP, no martensite, no Patel-Cohen, no strengthening decomposition.

- **One transferable concept:** the **Somekawa-style tensile-property → K_IC fit** (Eqs. 2-6):
  - r_p ≈ (1/6π)(K_IC/σ_s)²
  - K_IC = √(2E σ_b ε_f* r_p)
  - Empirical fit (R² = 0.993): K_IC = [20.7 · log(σ_f'²/σ_s·σ_b)/log(500 ε_f)] · (σ_s ε_f)^½ + 1.15

  Could be a useful **sanity-check predictor** for our M54 model — feed predicted YS, UTS, ε_f into this kind of correlation to estimate K_IC. Constants would need re-fitting from a martensitic steel dataset (don't use 20.7 / 1.15 as-is).

- **Zhu citation:** ref [41], one-line invocation as a "n affects toughness" reference.

---

## 5. Zhang et al. 2025 — Agricultural-machinery digital twin review (—)

- **Citation:** Chunpeng Zhang, Jiaru Song, Xiangyu Yin, Jie Cai, Yuchen Liang, Jinzhong Lu. *Digital twin-based approaches for agricultural machinery damage prediction and maintenance: A review.* J. Computational Design and Engineering **12**(10) (2025) 87–117. [10.1093/jcde/qwaf097](https://doi.org/10.1093/jcde/qwaf097) (open access).

- **Why it's in the folder:** Zhu 2025 is cited **once**, on p. 108 §6.1 ("Material and process limitations"), as a courtesy reference for "high-strength low-cost alloys could feed AM-repair of agricultural machinery." No metallurgical content.

- **Action:** Ignore for the model. Consider moving out of "Articles that CITE main article" into a "misfiled" folder if we want a clean dataset.

---

## Cross-cutting takeaways for the M54 model

1. **The strengthening framework is well-established and stable.** Both Zhu MAIN and Li (C64) use the same equation set (σ_0 + σ_ss + σ_{H-P} + σ_ρ + σ_p), same Fleischer β coefficients, same constants (σ_0 = 50, M = 2.5, µ/G = 80 GPa, b = 0.25 nm, K_{H-P} = 300 MPa·µm^½). The only real choice is **whether to use linear sum (Zhu) or Pythagorean (σ_d²+σ_p²)^½ on dislocation+precipitation (Li/C64)**. Recommend documenting both and reporting both for our M54 case.

2. **The NiAl population at our M54 temper window** is bounded:
   - Lower-r: Duan 2025, r = 0.57 nm, N = 4.88 × 10²⁴ (very early stage)
   - Higher-r: Zhu MAIN at 32 h, r = 1.37 nm, N = 1.05 × 10²³
   - Our M54 at 516 °C / 10 h likely sits between these.

3. **Reversed austenite films will matter at 516 °C / 10 h.** Both Zhu MAIN and C64 show them. Plan for an explicit f_A term (rule-of-mixtures, with σ_A ≈ 360 MPa per C64) and an additional toughness contribution via crack deflection / TRIP at the crack tip.

4. **Patel-Cohen is not in the cited-by literature** for our specific alloy family. We will need to bring this in from outside — from the Patel & Cohen 1953 original or from a TRIP-modeling review. Zhu's mention of stress-induced γ→α′ at the crack tip is qualitative justification for the use of P-C in our toughening submodel, but does not give us the coefficients.

5. **MC carbides (V, Ti, Nb)** are completely absent from Zhu and C64 (no V/Ti/Nb in either alloy). M54 has 0.3 wt% V → MC term. Need separate Mondiere 2018 / Wang 2024 to populate that part of the model.
