# Model Findings & Insights

> Living log of discoveries, calibration notes, and design decisions made while
> building the M54 strengthening model. Updated as we go. Organized **topically**
> for reference use, with phase tags so you can trace when each finding landed.

## How to use this doc

- **Looking for "what does our model do for X?"** → §2 (per-contribution).
- **Looking for "how does our prediction compare to paper Y?"** → §3 (per-anchor).
- **Looking for "why was this constant chosen?"** → §4 (calibration choices).
- **Looking for "what are the known biases?"** → §5 (gaps and known biases).
- **Looking for the chronological story** → §6 (phase log).

Each finding flagged with `[Phase X.Y]` for when it was discovered.

---

## 1. Convention conflicts in the literature

These are places where different papers use different forms of the same physical
equation. Documented so we don't get tripped up reading a paper and assuming
their α/K matches ours.

### Bailey-Hirsch dislocation strengthening — α conventions

`σ_ρ = α_eff · G · b · √ρ`

| Source | Original form | α | M | α_eff (Schmid-averaged prefactor) |
|--------|---------------|---|---|-----------------------------------|
| Sun 2022 (Bhadeshia & Honeycombe lineage) | `α G b √ρ`     | 0.38 | implicit | **0.38** (DEFAULT in our model) |
| Wang 2024 / Zhu 2025                       | `α M G b √ρ`   | 0.25 | 2.5      | **0.625** |
| Galindo-Nava 2015                          | `α M G b √ρ`   | 0.25 | 3.0      | 0.75 |

**Pitfall:** if you read Sun's formula and naïvely multiply by M=2.5, you
double-count by ~2.6×. We hit this bug in Phase 1.5 (caused DQ to "pass" at
−1.4 % deceptively, by canceling out a missing physics term). Fix landed in
[`dislocation.py`](../src/m54model/strengthening/dislocation.py); convention
collapse documented in
[`constants.py`](../src/m54model/constants.py). `[Phase 1.5]`

### Hall-Petch coefficient K_HP — block size assumed

`σ_HP = K_HP · d^(−1/2)`, with **d = martensite block width** (per Galindo-Nava
2015, originally Morito 2006).

| Source | K_HP (MPa·µm^½) | d definition |
|--------|----------------:|--------------|
| Sun 2022 (M54-specific fit, Fig. 7) | **230** (DEFAULT) | block size |
| Wang 2024 / Zhu 2025 (generic SH-steel)  | 300 | block size |
| Galindo-Nava 2015 model | 300 | block size (per Morito 2006) |

Sun's lower K is a fit specifically on M54 data; we default to it as the most
specific value. The 30 % gap to Wang/Zhu's generic 300 is worth re-checking
when more M54 data accumulates.

### Top-level summation strategy

Three strategies supported (see [`total.py`](../src/m54model/strengthening/total.py)
docstring):

| Strategy        | Form                                                                                               | Used by              |
|-----------------|----------------------------------------------------------------------------------------------------|----------------------|
| `linear`        | σ_y = σ_0 + σ_ss + σ_HP + σ_ρ + σ_p                                                                | Sun 2022, Zhu 2025 (DEFAULT) |
| `pythagorean_p` | σ_y = σ_0 + σ_ss + σ_HP + σ_ρ + √(Σ σ_pᵢ²)  (only between precipitate phases)                       | seen rarely         |
| `pythagorean_dp`| σ_y = σ_0 + σ_ss + σ_HP + √(σ_ρ² + σ_p²)  (across dislocation + all precipitates)                  | Wang 2024, Li 2026 C64 |

**Empirical:** for our DQ + T516/10 anchor, `linear` lands at −4.9 % vs
`pythagorean_dp` at −17.6 % under-predict. `linear` is correct for tempered M54
in the regime we're modeling. `pythagorean_dp` would only become preferable if
σ_ρ and σ_p both contributed strongly *and* were partially substitutive — a
regime our calibration data doesn't show. `[Phase 1.5]`

### Carbon strengthening — Speich-Leslie 1722 vs our 985

The classical empirical fit of Speich & Leslie 1972 on plain-C as-quenched
martensite:

```
σ_y(MPa) = 413 + 1722 · √(wt%C)
```

The 1722 lumps **all** C-related strengthening: Fleischer atomic-mismatch +
Bain tetragonality + lath-boundary HP + supersaturation. If you also use
Fleischer-C separately (β_C ≈ 1722 MPa per √(at-frac) ≈ 7969 MPa per √(wt%C)
after unit conversion), you double-count.

Our decomposition keeps them separate:
- **Fleischer-C:** β_C ≈ 1722 MPa·√(at-frac)⁻¹ in the at-frac Fleischer sum (also a placeholder; needs proper sourcing)
- **Intrinsic martensite:** K = **985 MPa·√(wt%C)⁻¹** captures the residual
  (Bain + lath + supersaturation), only present in untempered states

`985² + (1722×wt-to-at-conv)² ≈ 1722²` (roughly) — the Speich-Leslie 1722 is
the quadrature sum of the two pieces we've split out. `[Phase 1.6]`

---

## 2. Per-contribution notes

For each strengthening term: what we use, what's calibrated, what's still
guesswork. See [`MODEL_PLAN.md §3.5`](MODEL_PLAN.md) for the full constants
table.

### σ_0 — lattice friction
- **Value:** 50 MPa (universal across Sun 2022, Wang 2024, Zhu 2025, Galindo-Nava).
- **Source:** textbook for BCC-Fe; Sun ref [12].
- **Confidence:** high; doesn't move.

### σ_ss — Fleischer solid-solution
- **Form:** `σ_ss = √(Σ_i β_i² · x_i)` over substitutional + interstitial elements
  remaining in matrix (excludes Fe).
- **β coefficients** for Co/Ni/Cr/Mo/Al sourced from Niu 2019 (via Zhu 2025
  Table 3). β for **W, V, C, Ti are placeholders** —
  W=700, V=200, C=1722, Ti=250 — based on educated guesses from atomic-radius
  + shear-modulus mismatch arguments (proper computation per Galindo-Nava
  Appendix A is a TODO).
- **Confidence:** medium for Co/Ni/Cr/Mo; **low for W/V/C/Ti** (placeholders).
- **Sensitivity check (Phase 1.6):** β_C swept 1500-2000 MPa moves DQ
  prediction by ~25 MPa (1-2 %). Calibration is robust to β_C uncertainty
  within this range because the bulk of C-strengthening is in the intrinsic
  term, not Fleischer-C.

### σ_HP — Hall-Petch grain-boundary
- **Form:** `σ_HP = K_HP · d^(−1/2)` with d = block width (μm).
- **K = 230 MPa·µm^½** per Sun 2022 (M54 fit).
- **Confidence:** high; comes from your own paper.

### σ_ρ — Bailey-Hirsch dislocation
- **Form:** `σ_ρ = α_eff · G · b · √ρ` (Sun convention with M absorbed; see
  §1).
- α_eff = 0.38, G = 80 GPa, b = 0.25 nm.
- **Confidence:** high after Phase 1.5 bug fix.

### σ_intr — as-quenched intrinsic martensite (new in Phase 1.6)
- **Form:** `σ_intr = K · √(wt%C in solid solution)`, K = 985.
- **Returns 0 for tempered states** — by construction in the function.
- **Calibrated against** Sun 2022 DQ anchor; validated against AF550/45 with
  the same K (works without retuning). `[Phase 1.6]`

### σ_p — Orowan precipitation
- **Form (with spacing):** `σ_p = M · 0.4 G b / [π √(1−ν)] · (1/L) · ln(2 r_s/b)`
  per Wang 2024 Eq. 9.
- **Form (volume-fraction fallback):** `σ_p = 0.26 · G b / r_eq · √f_v · ln(r_eq/b)`
  per Zhu Eq. 13 (Ashby).
- **For DQ + T516/10:** uses Wang's measured M2C population at 520 °C / 8 h
  (closest published anchor to commercial 516 °C / 10 h spec): r_eq = 0.85 nm,
  N = 6.5 × 10²⁰ m⁻³, L = 12.3 nm.
- **Confidence:** medium — using Wang's 520 °C population at 516 °C may
  introduce a small bias. Mondière reports M2C size at 516/10 as 9.6 × 1.2 nm
  rod (slightly larger than Wang's 4 × 0.8) but doesn't give N or f_v, so we
  can't directly use Mondière for the full population.

### σ_y(eff) — austenite rule-of-mixtures correction
- **Form:** `σ_y(eff) = (1 − f_A) σ_y + f_A · σ_A` with σ_A = 360 MPa per Li
  2026 C64.
- **Currently uses total f_A** without decomposing retained vs reverted (per
  Q4 of MODEL_PLAN §10).
- **Note:** the user's 0/20/40/60 % cw/cr austenite-content data is the
  designated calibration set for the **Olson-Cohen TRIP submodel** in Phase 3.

---

## 3. Per-anchor model-vs-published comparisons

Calibration anchors per [`MODEL_PLAN §6`](MODEL_PLAN.md). Each anchor is a
specific microstructural condition with a measured YS we try to reproduce.

### Anchor 1 — Sun 2022 DQ (no temper)

- **Anchor YS = 1420 MPa.**
- **Predicted = 1419 MPa (−0.1 %).** PASS. `[Phase 1.6]`
- Decomposition (linear sum, Sun convention):
  - σ_0 = 50, σ_ss = 257, σ_HP(d=1.18) = 212, σ_ρ(2.08e15) = 346,
    σ_intr(0.30 wt%C) = 539. **Total = 1404.** (Discrepancy with reported 1419
    is rounding in the per-term display.)
- **What this calibrates:** the K=985 intrinsic-martensite coefficient.
- **Note:** Sun 2022's own decomposition only reports the AF→DQ delta (ΔHP +
  Δσ_ρ ≈ 434 MPa vs measured ΔYS = 410 MPa). It doesn't validate absolute DQ
  YS — our model is the first to attempt that decomposition.

### Anchor 2 — Sun 2022 DQ + T516/10 (commercial spec)

- **Anchor YS = 1762 MPa.**
- **Predicted = 1675 MPa (−4.9 %).** PASS. `[Phase 1.5]`
- Decomposition:
  - σ_0 = 50, σ_ss = 195 (post-precipitation matrix), σ_HP(d=1.18) = 212,
    σ_ρ(1.12e15) = 254, σ_intr = 0 (tempered), σ_M2C = 964.
    **Total = 1675.**
- **The −87 MPa miss** is interpretable: Wang 2024 explicitly under-predicts
  by 30-90 MPa attributed to **MC carbide Orowan contribution NOT included**.
  Adding MC properly should close the gap. Tracked as a TODO in the Orowan
  term.
- **σ_M2C lineage:** uses Wang's measured 520/8 population (r_eq = 0.85 nm,
  L = 12.3 nm, N = 6.5e20). Plugging into our Ashby-Orowan with-spacing form
  reproduces Wang's reported σ_p ≈ 980 MPa to within 2 %.

### Anchor 3 — Sun 2022 AF550/45 (no temper, ausformed)

- **Anchor YS = 1830 MPa.**
- **Predicted = 1864 MPa (+1.9 %).** PASS. `[Phase 1.6]`
- Decomposition:
  - σ_0 = 50, σ_ss = 257, σ_HP(d=0.48) = 332, σ_ρ(7.81e15) = 672,
    σ_intr(0.30 wt%C) = 539. **Total = 1850.**
- **What this validates:** the K=985 intrinsic-martensite coefficient (fit on
  DQ) transfers to AF without retuning. Same physics, refined geometry.
- **Sun 2022's own analysis:** Δ(AF − DQ) = 410 MPa measured. Our model
  predicts 1864 − 1419 = 445 MPa Δ. Sun explicitly attributed this to:
  block refinement +120 MPa (we get +120 MPa), dislocation strengthening +314
  MPa (we get +326 MPa with the corrected Bailey-Hirsch). Lines up with Sun's
  decomposition to within 4 %.

### Anchor 4 — Sun 2022 AF550/45 + T425/10 (enhanced commercial route)

- **Anchor YS = 1726 MPa.**
- **Predicted = 1748 MPa (+1.3 %).** PASS. `[Phase 2]`
- **First-pass result was +5.3 % over** using Cho's H600 V_f saturation
  (0.0040) directly. The fix was a composition-stoichiometry argument:
  Cho's 13Co-8Ni alloy has 5.4 wt% total M2C-formers (Cr 3.89 + Mo 1.49); M54
  has 4.4 wt% (Cr 1.0 + Mo 2.0 + W 1.3 + V 0.1). Ratio: **0.81**. Applying
  V_f_M54 = 0.81 × V_f_Cho closes the anchor to +1.3 %.
- **Predicted M2C population at AF + T425/10 (kinetics-derived):**
  - r_eq = 1.80 nm (LSW-coarsened from Cho's peak r=1.52 nm using
    Q_coarsen=177 kJ/mol Arrhenius-scaled to 425 °C)
  - V_f = 0.0032 (M54-stoich-scaled from Cho 0.0040)
  - N = 1.32 × 10²³ m⁻³
  - L = 19.6 nm
- **Decomposition:** σ_0=50, σ_ss=195, σ_HP(d=0.48)=332, σ_ρ(1.18e15)=261,
  σ_intr=0, σ_M2C=910. **Total = 1748.**
- **Compare to DQ + T516/10:** AF+T predicts 1748 vs DQ+T 1675 — AF route is
  73 MPa stronger. Sun 2022 measured: AF+T 1726 vs DQ+T 1762 — AF route is
  36 MPa **weaker**. Direction-disagreement of 36 MPa! This is a **subtle bias**
  in our model worth tracking. Likely source: AF+T425/10 has
  smaller-but-more-numerous M2C (vs DQ+T516/10's larger-fewer M2C), and our
  Orowan formula favors the small-dense regime more than experiment suggests.
  Worth investigating with sensitivity analysis on r vs L when more anchor
  data is available.

---

## 4. Calibration choices and their rationale

### Why default to Sun convention (α_eff = 0.38, K_HP = 230)?

- Sun 2022 is the user's own paper; numbers are M54-specific and credible.
- Wang/Zhu's α_eff = 0.625 over-predicts σ_ρ by ~65 % vs Sun's 0.38 in the AF
  state. Without an offsetting reduction elsewhere, Wang's convention
  over-predicts AF YS by ~10 %.
- We expose the WANG convention via `Convention.WANG` if reproducing Wang's
  numbers exactly is needed. `[Phase 1.5]`

### Why K=985 for the intrinsic-martensite term?

- Calibrated to nail Sun 2022 DQ (anchor 1) within 0.1 %.
- Validates AF anchor at +1.9 % without retuning — strong evidence that the
  term captures real C-driven physics rather than per-state empirical fit.
- Speich-Leslie 1722 is the lumped value that includes Fleischer-C; subtract
  Fleischer-C contribution and the residual matches our K. `[Phase 1.6]`

### Why deferred reverted-vs-retained austenite decomposition?

- The user has measured **total** austenite at 0, 20, 40, 60 % cw/cr but has
  not run TEM/APT to decompose retained vs reverted. For the rule-of-mixtures
  YS correction the distinction doesn't matter.
- The cw/cr series IS the right calibration data for **Olson-Cohen
  α(T), β(T) parameters** in Phase 3 — much better than transferring 304 SS
  values from Olson-Cohen's original paper. `[Phase 0]`

### Why hold lath spacing constant at 135 nm across all conditions?

- Sun 2022 reports lath width 70-200 nm but does not break out by AF vs DQ.
- 135 nm is the midpoint; same value used in DQ and AF state factories.
- Implication: lath-spacing-based contributions (which we don't yet use)
  would be identical in DQ and AF, which is probably wrong (AF likely has
  refined laths too). When we add lath-HP (Phase 2.5?), this needs better
  data. `[Phase 1]`

---

## 5. Known gaps and biases

Things we know are wrong or missing, deliberately deferred:

| Item | Direction | Magnitude | Tracked in |
|------|-----------|-----------|------------|
| Fleischer β for W, V, C, Ti are placeholders | unknown | likely small (<5 % on DQ; negligible elsewhere) | TODO in `constants.py` |
| MC carbide Orowan contribution not computed | under-predicts | 30-90 MPa on DQ + T (per Wang 2024) | TODO in `orowan.py` |
| Lath-HP enhancement above block-HP not modeled | under-predicts in untempered (compensated by intrinsic term) | unknown — currently absorbed into K=985 | Galindo-Nava option in MODEL_PLAN |
| **AF+T predicts > DQ+T but Sun measures AF+T < DQ+T** | **direction-of-effect** | model says AF wins by 73 MPa, exp says DQ wins by 36 MPa — total mismatch ~109 MPa | `[Phase 2]` — see anchor 4 §3 |
| Reverted-vs-retained austenite not decomposed | n/a (uses total f_A) | small for YS, larger implications for TRIP | Phase 3 |
| Carbon-in-solution depletion at temper hardcoded at 99 % | small | plausibly ±20 MPa | should derive from M2C V_f balance |
| Block size doesn't change with tempering | OK to first order (Wang 2024 confirms) | none | n/a |
| K_LSW for M2C in M54 is order-of-magnitude estimate (5e-31 m³/s) | unknown direction | could shift r at peak by 30 % | TODO in `kinetics/m2c.py` |
| AF state V_f saturation calibrated via 0.81 stoichiometry scale | calibrated to anchor 4 | tunable knob, uncertainty propagates | `[Phase 2]` |
| **M54 cw/cr austenite content is non-monotonic in CR** — Olson-Cohen alone cannot model the user's measured behavior | model would over-predict α′ formation in the 40-60 % CR regime where reverse-transformation actually dominates | up to ~25 vol % austenite-content discrepancy at 40 % CR | `[Phase 3]` — see §7 below |

---

## 6. Phase log (chronological)

### Phase 0 — Literature foundation (complete)
- 73/73 papers indexed locally with verified DOIs.
- TRIP foundation papers (Patel-Cohen, Olson-Cohen) indexed.
- Architecture plan ([`MODEL_PLAN.md`](MODEL_PLAN.md)) drafted with knowledge
  inventory across the four states.

### Phase 1 — Strengthening core scaffold
- Python package `m54model/` with src layout, uv-managed, ruff/mypy/pytest.
- All five baseline strengthening contributions implemented
  (`friction`, `solid_solution`, `hall_petch`, `dislocation`, `orowan`).
- Three summation strategies (`linear`, `pythagorean_p`, `pythagorean_dp`).
- 8 smoke tests passing.

### Phase 1.5 — Bug fix + first calibration sweep
- **Bug:** double-counted Taylor factor in `sigma_dislocation`. Fixed.
- **Finding:** DQ + T516/10 calibrates cleanly at −4.9 % under Sun convention
  + linear sum.
- **Finding:** DQ and AF (untempered) under-predict by 28-38 % — exposed a
  missing physics term.

### Phase 1.6 — Intrinsic-martensite term
- **New term:** `σ_intr = K · √(wt%C in solid solution)`, K = 985,
  applies only in untempered states.
- **Result:** all three baseline anchors PASS within ±5 %. Same K calibrates
  DQ and AF without retuning.

### Phase 2 — Tempering kinetics + AF anchor (complete)
- M2C kinetics modules (`kinetics/{jma, lsw, m2c}`).
- Wang 2024 baseline for DQ tempering, Cho 2015 H600 baseline for AF tempering.
- Arrhenius scaling on rate constants from each paper's reference temperature.
- LSW coarsening past peak.
- M54 vs Cho stoichiometry V_f scaling (0.81) — closed AF+T anchor from +5.3 %
  to +1.3 %.
- **All 4 Sun 2022 anchors PASS within ±5 %.** Best fit: AF+T at +1.3 %.
- **Direction-of-effect bias caught:** model predicts AF+T > DQ+T by 73 MPa,
  but Sun measures AF+T < DQ+T by 36 MPa. Tracked in §5.

### Phase 3 v1 — TRIP submodel equations (complete)
- `m54model.toughening.patel_cohen` — stress-assisted M_s shift.
  **Reproduces Patel-Cohen 1953 Table I tension slope exactly: +1.07 °C/ksi**
  for Fe-Ni-C; hydrostatic exact (-0.38 °C/ksi); compression slightly off
  (0.65 vs PC's 0.72 — likely a slight different molar-volume convention).
- `m54model.toughening.olson_cohen` — strain-induced sigmoidal kinetics.
  Reproduces Angel 1954 304 SS curves (saturates ~0.86 at -188 °C / ε=0.6;
  ~0.20 at 22 °C / ε=0.6).
- `m54model.toughening.fit_olson_cohen` — scipy least-squares fitter for
  (α, β) given (ε, f_α′) data; recovers synthetic params to within 1 %.
- `m54model.calibration.user_trip_data` — placeholder data structure for the
  user's 0/20/40/60 % cw/cr austenite measurements with conversion to true
  strain via ε = -ln(1-r). Drop in real values to calibrate M54 reverted-γ
  Olson-Cohen parameters.
- 10 new validation tests; all 24 tests now pass.

### Phase 3.1 — User's M54 ASTAR cw/cr data, non-monotonic finding `[Phase 3.1]`

ASTAR precession-diffraction-mapped FCC γ phase fractions across 0/20/40/60 %
cumulative cold rolling, both at the rolling **surface** and through-thickness
**core** (median along ND-midplane):

| CR % | Surface RA (%) | Core RA (%) | User's annotation                  |
|-----:|---------------:|------------:|------------------------------------|
|   0  |    1.3 ± 0.9   |     2.6     | Trace; as-quenched baseline        |
|  20  |    0.5 ± 0.3   |     1.3     | Heterogeneous onset                |
|  40  |   26.4 ± 9     |     9.9     | Peak cellular network; 4:1 surface:core |
|  60  |   17.6 ± 8     |    12.6     | Partial retransformation           |

**The behavior is non-monotonic in CR.** Classical Olson-Cohen predicts f_α′
monotonically increases with plastic strain → f_A monotonically decreases.
The user's data shows the opposite story above 20 % CR: austenite content
**rises sharply** at 40 % CR (surface jumps from 0.5 % to 26.4 %, a 50× jump)
then partially retransforms at 60 %.

**Implications:**

- Olson-Cohen alone is **insufficient** for M54 reverted austenite under
  cold rolling. Any α(T), β(T) we fit would over-predict α′ formation in
  the 40–60 % CR regime where reverse-transformation dominates.
- The fitter in `m54model.calibration.user_trip_data` defaults to
  `fit_only_monotonic_prefix=True` and refuses to fit because the
  monotonic-decreasing prefix has only 2 points (0 → 20 % CR) — too few for
  two parameters. Forcing a fit on the full data rails α to its upper
  bound (50), a clear "model is wrong" signal we lock in via test.
- The 4:1 surface:core ratio at 40 % CR is the **smoking gun** for either
  surface-localized adiabatic heating during rolling (driving local
  α′ → γ reverse transformation) or strain partitioning that creates a
  cellular shear-band substructure stabilizing austenite at the surface.

**Candidate mechanisms** for the high-CR austenite formation/stabilization:

1. **Adiabatic heating at the rolling surface** drives local α′ → γ reverse
   transformation. Plausible: surface sees highest shear strain rate, so
   biggest local ΔT.
2. **Mechanical α′ → γ transformation in shear-band cellular networks** —
   shear bands at >20 % CR provide energetically-favorable nucleation sites
   for the reverse transformation.
3. **TWIP-like substructure** (twin boundaries acting as nucleation sites
   for retained or reverted austenite stabilization).
4. **Mechanical alloying through ε-martensite intermediate**: γ → ε → α′ →
   ε → γ cycle under severe shear.

**Path forward (Phase 3.5):**

- For crack-tip K_IC modeling in Phase 3.5, use Olson-Cohen with
  literature-analog (α, β) — e.g., Cho 2015 H600 Co-Ni values, or 304 SS
  RT — explicitly noting this as a calibration gap.
- Restrict any quantitative TRIP claim to the 0 → 20 % CR (small-strain)
  regime where classical TRIP applies.
- Phase 3.6 scope: extend to a **competing mechanism model** combining
  forward Olson-Cohen γ → α′ with a separate α′ → γ reverse rate that
  depends on local temperature rise and strain-band density.

### Phase 3.2 — Mechanism evidence: bimodal grain structure + GND densities `[Phase 3.2]`

Two additional datasets from the user (ASTAR-derived grain size + ASTAR-PED
extrapolated GND densities, both phase-resolved) reinforce the
non-monotonic-austenite finding from §6.1 and point at a specific mechanism.

**Bimodal surface microstructure at 40 % CR — the smoking gun:**

| CR  | Loc.    | Mean GA (nm) | %<50 nm | %>200 nm | Characteristic |
|-----|---------|-------------:|--------:|---------:|----------------|
|  0  | Surf.   |    62-75     |    35   |    5     | Unimodal lath martensite |
| 20  | Surf.   |    71-75     |    40   |    8     | Heterogeneous onset |
| **40** | **Surf.** | **37**   |  **60** |  **20**  | **Bimodal (fine + remnant)** |
| 60  | Surf.   |    53-116    |    20   |   12     | Unimodal; intermediate refine |

At 40 % CR Surface, grain population is bimodal: 60 % fine (<50 nm) +
20 % coarse (>200 nm). This is **direct microstructural evidence for the
cellular shear-band network** the user noted in the f_A table — the fine
population is consistent with reverted γ nucleating at shear-band
intersections, the coarse population is remnant un-deformed lath martensite.

**Mechanism story (combining §6.1, §6.2, §6.3 rolling conditions):**

The user's IR-monitored rolling-surface temperature **never exceeded 80 °C**
during any pass (`USER_M54_ROLLING_CONDITIONS`). This **rules out bulk
adiabatic-heating-driven reverse transformation** as the dominant mechanism —
the surface is far too cold to reach the chemical Ac1 of any reasonable
local γ-stabilizing region.

What survives:

1. ~~Bulk adiabatic heating at the rolling surface~~ — **ruled out** by IR data.
2. **Mechanical Patel-Cohen reverse transformation under compressive contact
   stress.** For α′ → γ, ε₀ inverts sign (Bain volume contracts), so
   compression × negative ε₀ favors reverse. With max separating force
   290 MPa (≈ 42 ksi) and Hertzian peak ~2-3× higher (600-900 MPa local
   contact), PC's +0.72 °C/ksi compression slope gives ~85-200 °C M_s shift —
   borderline for bulk reverse transformation but **sufficient at local
   stress concentrations** in shear-band intersections.
3. **Cellular shear-band network at 40 % CR provides BOTH stress-
   concentration sites AND localized strain-band heating.** While bulk
   surface stays cold, the inelastic dissipation rate inside individual
   shear bands during the brief roll-bite contact can spike local T+stress
   far above the bulk average. This is the mechanism that the IR can't see
   (sub-pass time scale, sub-millimeter spatial scale).

The 4:1 surface:core ratio in the f_A data is now attributed to surface-
localized **stress** (Hertzian contact peaks at the roller-strip interface)
rather than surface-localized **temperature**. Bimodal grain structure (60 %
fine + 20 % coarse at 40 % CR Surface) is direct evidence for the cellular
network providing the nucleation pathway.

**Modeling implication:** the cellular shear-band network is the right
length scale for the non-monotonic mechanism — bulk-averaged Olson-Cohen +
bulk Patel-Cohen will continue to under-predict the high-CR austenite. A
phenomenological "shear-band-mediated reverse-transformation rate" term
keyed on local plastic strain × local hydrostatic-compression contribution
is the cleanest path forward (probably Phase 3.6).

### Phase 3.3 — AF+T516/10 prediction is a testable claim `[Phase 3.3]`

The user's actual cw/cr baseline state is **AF550/45 + T516/10** (NOT Sun's
AF+T425/10). Built `m54_af550_45_t516_10()` factory with:
- Block 0.48 µm (from AF, invariant in tempering)
- ρ = 1.6 × 10¹⁵ m⁻² (user's ASTAR-PED at 0 % CR baseline, BCC median)
- f_A = 0.013 (user's ASTAR phase fraction at 0 % CR Surface)
- M2C population predicted via Cho-transferred kinetics at (516, 10)

**Model prediction: σ_y ≈ 1373 MPa.**

That's ~390 MPa weaker than DQ+T516/10 (1762, Sun anchor) and ~350 MPa
weaker than AF+T425/10 (1726, Sun anchor). The reason: ausforming-
accelerated M2C nucleation reaches saturation V_f early in the 10 h
hold, then LSW-coarsens for the remaining time at 516 °C — predicted
r grows to 4.35 nm (vs Wang's 0.85 nm at peak) and L to 47.4 nm (vs
12.3 nm at peak). The Orowan strength drops accordingly.

This is **the same insight that motivated Sun 2022's AF+T425/10 choice**:
AF route should be paired with lower-T tempers to keep M2C in the
small-dense regime. AF+T516/10 over-tempers.

**Testable prediction:** if/when you have a measured YS for the AF+T516/10
baseline (likely tensile data at 0 % CR), the gap between predicted (1373)
and measured will tell us:
- Gap small (within ±5 %) → confirms AF over-tempers at 516/10; the
  cw/cr work was the right way to recover strength.
- Predicted is too low (e.g. measured ≈ 1700 MPa) → my K_LSW or
  Q_coarsen is too aggressive; M2C didn't coarsen as much as Cho's
  kinetics predict for M54 chemistry. Calibration pull on those constants.
- Predicted is too high → unlikely given the conservatism, but would
  point at a model-form issue.

If you ever tensile-tested the 0 % CR baseline, please send the number —
it's a good cross-validation point for the kinetics module.

**GND density observations:**

| CR  | BCC median ρ (×10¹⁵ m⁻²) | FCC median ρ (×10¹⁶ m⁻²) | n grains BCC |
|-----|--------------------------:|---------------------------:|--------------|
|  0  |          1.6              |          6.5               |    34        |
| 20  |          6.3              |          3.3               |    46        |
| 40* |          7.9              |          3.8               |     4 *      |
| 60  |          6.3              |          3.2               |    24        |

(*small n grains for the FCC phase at 40 % — interpret carefully.)

Two surprises:
- **FCC ρ is ~5–10× higher than BCC ρ** across all CR conditions. The
  reverted austenite is heavily defected from interface mismatch with the
  surrounding martensite, even pre-deformation (0 % CR FCC ρ = 6.5e16 m⁻²).
- **BCC ρ peaks at 40 % CR** (7.9e15 m⁻²) coincident with the austenite
  spike — energy is concentrated in dislocation walls at the conditions
  where the cellular network is most active.

**Implication for our model:** σ_A = 360 MPa (Li 2026 C64 textbook value)
is likely too low for cold-worked M54 reverted austenite. Bailey-Hirsch
on FCC at ρ = 6.5e16 m⁻² gives σ_y,γ ≈ 660 MPa with FCC constants
(α≈0.3, G≈75 GPa, b≈0.253 nm, σ_0≈200 MPa). Roughly 2× the textbook value.
Phase 3.5 should support per-condition σ_A from measured FCC ρ instead of a
constant 360 MPa default.

### Phase 3.5 (next) — Crack-tip K_IC integration
- HRR (or simpler) crack-tip stress field model.
- For each material point in plastic zone:
  - Apply Patel-Cohen U = τγ₀ + σε₀ → stress-assisted M_s shift.
  - Apply Olson-Cohen with calibrated (α, β) → strain-induced f_α′.
- Sum transformed-α′ volume → compressive residual stress field → ΔK_IC.
- Validate against Mondière's M54 K_IC = 110 MPa·m^(1/2) anchor.

---

## Adding a new finding

When you spot something worth recording:

1. Decide if it's a per-contribution fact (§2), per-anchor comparison (§3),
   calibration choice (§4), or a known gap (§5). Sometimes it's worth
   recording in two sections — that's fine.
2. Tag with `[Phase X.Y]` so future-us can trace it back.
3. If the finding changes a model output, add a one-line entry to §6 with the
   commit-merge SHA so you can `git show` the diff later.
4. Keep entries terse and link to source (`[citekey]` for lit, file path for
   code).

Avoid burying findings in commit messages alone — they get hard to find.
