# M54 Strengthening + Toughening Model — Step-Back Evaluation v1

> Written 2026-05-12, after Phase 3.6h. Purpose: take stock of what the model
> says, what it's grounded in, where the residuals are honest signal vs noise,
> and what we'd most usefully do next. Intended for self-orientation and as a
> prompt for advisor discussion.

This is a synthesis essay, not a phase log. For incremental work history see
[`FINDINGS.md`](FINDINGS.md); for the canonical architecture see
[`MODEL_PLAN.md`](MODEL_PLAN.md).

---

## 1. Where we stand quantitatively

### Sun 2022 calibration anchors — all four pass within ±5 %

| Anchor                               | Predicted | Measured | Miss     | Status |
|--------------------------------------|----------:|---------:|---------:|--------|
| DQ (post-cryo, no temper)            | 1419      | 1420     | −0.1 %   | ✓ PASS |
| DQ + T516/10 (commercial)            | 1675      | 1762     | −4.9 %   | ✓ PASS |
| AF550/45 (post-cryo, no temper)      | 1864      | 1830     | +1.9 %   | ✓ PASS |
| AF550/45 + T425/10 (enhanced)        | 1748      | 1726     | +1.3 %   | ✓ PASS |

These are the **non-trivial** test of the model: the same constants
(α<sub>BH</sub> = 0.38, K<sub>HP</sub> = 230, K<sub>intr</sub> = 985, the
Cho 2015 → M54 stoichiometry-scaled M2C kinetics) reproduce four states
spanning DQ vs AF processing AND two tempering temperatures.

### User cw/cr σ<sub>y</sub> sweep — direction right, magnitude under by
~300 MPa at high CR with default knobs

| CR % | f<sub>A</sub> core | ρ<sub>GND</sub> (m⁻²) | σ<sub>y</sub> model (default) | σ<sub>y</sub> measured | miss   |
|---:|---:|---:|---:|---:|---:|
| 0   | 0.026 | 1.6×10¹⁵ | 1420 | **1300 ± 30** | **+9.2 %** |
| 20  | 0.013 | 6.3×10¹⁵ | 1745 | (no tensile)  | —          |
| 40  | 0.099 | 7.9×10¹⁵ | 1695 | (no tensile)  | —          |
| 60  | 0.126 | 6.3×10¹⁵ | 1589 | **1900 ± 50** | **−16.4 %** |

With the **recommended `K_sub = 150` sub-block-HP knob** (Phase 3.6f), the
60 % gap closes to **+1.2 %** without disturbing the 0 % baseline:

| CR % | σ<sub>y</sub> model (K<sub>sub</sub>=150) | σ<sub>y</sub> measured | miss |
|---:|---:|---:|---:|
| 0   | 1420 | 1300 ± 30 | +9.2 % |
| 20  | 1993 | —         | —      |
| 40  | 1957 | —         | —      |
| 60  | 1923 | 1900 ± 50 | **+1.2 %** |

### K<sub>IC</sub> at M54 baseline — TRIP is negligible, matrix dominates

For M54 with f<sub>A</sub> = 1.3 % and K<sub>matrix</sub> = 100 MPa·m<sup>½</sup>:

| Field model | M<sub>s</sub> offset (K) | ΔK<sub>TRIP</sub> (MPa·m<sup>½</sup>) |
|---|---:|---:|
| Williams-K (Phase 3.6a) | 0   | 0.32 |
| Williams-K              | 50  | 0.26 |
| Williams-K              | 100 | 0.14 |
| HRR (Phase 3.6c)        | 0   | 0.32 |
| HRR                     | 50  | 0.17 |
| HRR                     | 100 | 0.09 |

Mondière's measured K<sub>IC</sub> = 110 MPa·m<sup>½</sup> for commercial
M54 is **essentially all matrix** — TRIP contributes well under 1 % of the
total even on the most-optimistic assumptions.

### XRD-derived facts (Phase 3.6b/g)

- **Bain volumetric strain ε<sup>V</sup> = +0.022** (M54-specific from a<sub>α′</sub>
  = 2.870 Å, a<sub>γ</sub> = 3.589 Å) — half the textbook +0.04 we'd been using.
- **Bulk V<sub>γ</sub> = 4.81 % at 0 % CR**, drops to ~0 % at 20-60 % CR (vs ASTAR
  surface 1.3 % → 26.4 % spike → 17.6 %). **XRD and ASTAR sample
  different volumes; both are correct for their scope.**
- **k = ρ<sub>WH</sub>/ρ<sub>GND</sub> = 0.06-0.13** across all CR — i.e.
  ρ<sub>GND</sub> from ASTAR-PED is ~10× the bulk WH ρ<sub>total</sub>. The
  *opposite* of a hidden SSD reservoir.

---

## 2. Anatomy of the predictions — what the contributions actually are

A typical M54 prediction (AF + T516/10 baseline, decomposition):

| Term       | Value (MPa) | What it represents | Source / equation |
|------------|------------:|--------------------|-------------------|
| σ<sub>0</sub>     |  50  | Lattice friction          | Universal (Sun, Wang, Zhu, Galindo-Nava all use 50) |
| σ<sub>ss</sub>    | 150  | Fleischer solid-solution  | √(Σ β<sub>i</sub>² · x<sub>i</sub>); β from Niu 2019 / Zhu Table 3 |
| σ<sub>HP</sub>    | 332  | Hall-Petch (block)        | K<sub>HP</sub>·d<sup>−½</sup>; K=230 (Sun M54 fit), d=0.48 µm (Sun AF) |
| σ<sub>ρ</sub>     | 304  | Bailey-Hirsch dislocation | α<sub>eff</sub>·G·b·√ρ; α<sub>eff</sub>=0.38 (Sun), ρ from user GND |
| σ<sub>intr</sub>  |   0  | As-quenched intrinsic     | K·√(wt%C); ≈0 in tempered states (C consumed) |
| σ<sub>p</sub>     | 537  | Orowan M2C                | M·0.4Gb/[π√(1−ν)]·(1/L)·ln(2r<sub>s</sub>/b); L from Cho-transferred LSW |
| **TOTAL (qs)**    | **1373** | linear sum (Sun + Zhu top-level convention) | |
| × strain-rate factor (200×, m=0.01) | **1448** | user-rate equivalent | (200)<sup>0.01</sup> = 1.054 |
| − austenite correction (f<sub>A</sub>=0.013) | **1434** | rule-of-mixtures with σ<sub>A</sub>=360 | |

**The two biggest contributors are σ<sub>p</sub>(M2C) (39 %) and σ<sub>HP</sub>
(24 %).** Together they're 63 % of the predicted yield.

---

## 3. Empirical vs first-principles audit

For each constant in the model, where does it come from? This is the lens
through which we should read every residual.

### Calibrated (fit to one or more anchors; circular if used to predict the same anchor)

- **K<sub>HP</sub> = 230 MPa·µm<sup>½</sup>** — Sun 2022 M54-specific Hall-Petch fit on
  block-width data. Anchored to Sun's DQ + AF anchors; not independent of them.
- **α<sub>BH</sub> = 0.38** — Bhadeshia-Honeycombe convention with M absorbed,
  used by Sun. Compatible-with-anchor calibration.
- **K<sub>intr</sub> = 985** — fit on Sun's DQ anchor explicitly. Tunes the σ<sub>y</sub>
  prediction to match measured σ<sub>y</sub> at the DQ state. Pure calibration.
- **Cho-transferred LSW kinetics for M2C in AF state** — fit indirectly so
  that AF + T425/10 prediction matches Sun's 1726 MPa anchor. Not independent.

### First-principles (with measured / literature inputs but not fit to our anchors)

- **σ<sub>0</sub> = 50 MPa** — universal field convention.
- **Fleischer β<sub>i</sub>** for Cr/Ni/Mo/Co/Al — from Niu 2019 (independent of M54
  anchors). β for W, V, C, Ti are placeholders (flagged in code).
- **σ<sub>p</sub> functional form** — Wang 2024 Eq. 9 / Zhu Eq. 13 (literature consensus).
- **σ<sub>ρ</sub> functional form** — Bailey-Hirsch (textbook).
- **σ<sub>A</sub> = 360 MPa** — Li 2026 C64 (different alloy but same regime).
- **Patel-Cohen γ<sub>0</sub>=0.20, ε<sub>0</sub>=0.04** — original PC 1953 Fe-Ni values.

### Measured directly on the user's samples

- **ρ<sub>GND</sub>(CR)** from ASTAR-PED — independent of every model assumption.
- **f<sub>A</sub>(CR, location)** from ASTAR — independent.
- **Bulk V<sub>γ</sub> + a<sub>α′</sub>** from XRD (Phase 3.6b) — independent.
- **σ<sub>y</sub>(CR)** from tensile (0/47/53/60 % CR) — the comparison anchors.
- **K<sub>IC</sub>(CR)** (Phase 3.6d-prep) — comparison only.
- **Bain ε<sup>V</sup> = 0.022** (Phase 3.6b) — measured, NOT calibrated.

### Sub-block HP K<sub>sub</sub> = 150 MPa·µm<sup>½</sup> (Phase 3.6f)

This is **calibrated to close the user's 60 % CR tensile measurement** —
it's the only M54-cw/cr-specific anchor we have. Single-point calibration
on a single tensile measurement; uncertainty band is wide. **Not
independent of the 60 % CR data point.**

---

## 4. Honest read of the residuals

### Sun anchor passes are not as impressive as they look

All four Sun anchors pass at ±5 %. But:

- **DQ pass at −0.1 % is essentially trivial** because K<sub>intr</sub> = 985 was
  fit explicitly to that anchor. The real tests are DQ+T, AF, AF+T.
- **AF (untempered) at +1.9 %** is also calibration-related: σ<sub>HP</sub> uses
  Sun's measured AF block (0.48 µm) and there's no independent f<sub>A</sub> or
  precipitate term to compete with σ<sub>ρ</sub>. So this anchor is a
  consistency check but not a strong test.
- **DQ + T at −4.9 %** is the most-stressed pass — three terms (σ<sub>HP</sub>,
  σ<sub>ρ</sub>, σ<sub>p</sub>) all carry ~equal weight, and the M2C kinetics is
  Cho-transferred (not directly fit). This is the closest thing to a
  predictive success.
- **AF + T at +1.3 %** is similar: M2C kinetics calibrated through AF-state
  parameters fit to match Sun's 1726 MPa.

The model is **self-consistent across DQ vs AF processing and across two
tempering temperatures**, but only DQ + T is a strict prediction.

### The user's cw/cr data is a real test

The cw/cr series gives us **two genuine prediction targets the model has
not been calibrated against**: σ<sub>y</sub>(0 %) = 1300 MPa and σ<sub>y</sub>(60 %) = 1900 MPa.

- **+9.2 % at 0 % CR**: model over-predicts by 120 MPa. The diagnosis sweep
  (Phase 3.6h) attributes this to a 3-way contribution: cross-rolled prior
  block coarsening (~50-100 MPa), ASTAR-surface vs bulk f<sub>A</sub>
  source (~30-50 MPa), M2C coarsening at 516/10 not captured by Cho-LSW
  transfer (~50-80 MPa). All three are plausible at parameter-uncertainty
  scale; none alone is the answer.
- **−16.4 % at 60 % CR (default knobs)**: the cw-induced sub-block
  refinement isn't captured by block-based σ<sub>HP</sub>. Phase 3.6f's
  K<sub>sub</sub>=150 closes this to +1.2 %, but K<sub>sub</sub> is a
  single-point fit to this data — it doesn't *predict* the 60 % CR point,
  it *fits* it.

### What we cannot do well right now

1. **Predict σ<sub>y</sub> at intermediate cw/cr conditions** without
   recalibration. The 47 %/53 % tensile points (1800/1700 MPa) are not
   reproduced by interpolating any sweep we have — the sub-block HP
   K<sub>sub</sub> is calibrated only to the 60 % point, and the 0 %
   over-prediction muddies the absolute calibration.
2. **Quantify K<sub>IC</sub>(CR)** beyond saying TRIP is negligible. The
   user's measured K<sub>IC</sub> trend (219 → 322 → 280 → 434 from
   0/47/53/60 %) is not captured by ΔK<sub>TRIP</sub> alone (which
   predicts <0.5 MPa·m<sup>½</sup>). The big rise in measured K<sub>IC</sub>
   has to come from matrix mechanisms (refined block, dislocation-
   accommodated tearing, sub-block boundaries deflecting cracks). That
   physics is not in the model.
3. **Disentangle cross-rolled-AF + temper from simple-AF + temper**. Our
   `m54_af550_45_t516_10()` uses Sun's simple-AF block. The user's actual
   cross-rolled prior may give a different effective block. EBSD on the
   user's 0 % CR sample would resolve this in one measurement.

### The TRIP ≪ matrix conclusion is robust

Across **every** field-model variation we've tried:

- bulk-averaged Williams-K (Phase 3.5) → ΔK<sub>TRIP</sub> ≈ 0.6 MPa·m<sup>½</sup>
- spatial Williams-K (Phase 3.6a) → ≈ 0.6 MPa·m<sup>½</sup>
- spatial K with M<sub>s</sub> offset = 50-100 K → 0.14-0.26 MPa·m<sup>½</sup>
- spatial HRR (Phase 3.6c) → 0.09-0.32 MPa·m<sup>½</sup>
- with M54-specific Bain ε<sup>V</sup> = 0.022 (Phase 3.6b, half textbook) → all of the above × 0.55

**Conclusion**: at M54's f<sub>A</sub> = 1-3 %, transformation toughening
contributes well under 1 MPa·m<sup>½</sup>. Mondière's measured 110
MPa·m<sup>½</sup> is essentially all matrix. Our cross-mechanism
verification is consistent — different field models, different ε<sup>V</sup>
choices, all give the same qualitative answer. **This is the strongest
prediction the model makes.**

---

## 5. Subjective evaluation: what we trust, what we don't

### High confidence

- The **strengthening framework** (decomposition, equation forms) is
  literature-consensus and reproduces four independent anchors.
- The **direction-of-effect** for cw-induced strengthening (σ<sub>y</sub>
  rises with CR) is right.
- The **TRIP ≪ matrix** finding for M54 K<sub>IC</sub>.
- The **strain-rate correction** algebra (200× × m=0.01 → 5.4 %) is
  empirical but pinned to a literature value with documented uncertainty.
- The **XRD-derived Bain ε<sup>V</sup> = 0.022** is direct measurement, not fit.
- The **qualitative cw/cr austenite story** (non-monotonic, surface-localized
  spike at 40 %) is consistent across ASTAR + XRD + nanoindent E<sub>r</sub>.

### Medium confidence

- The **Cho 2015 → M54 transferred M2C kinetics** at 516 °C / 10 h. Calibrated
  against Sun's 425/10 anchor, extrapolated to 516/10 via the LSW model.
  Sensitivity sweep in Phase 3.6h showed M2C L is the most-leveraged
  parameter for the baseline miss; we don't have a direct M2C measurement
  on the user's 516/10 sample.
- The **f<sub>A</sub> source choice for tensile-bar comparison**.
  ASTAR-surface, ASTAR-core, XRD-bulk all give different numbers and
  different model predictions. We don't have a "ground truth" bulk γ
  measurement that integrates over the tensile bar's gauge volume.

### Low confidence

- The **sub-block HP K<sub>sub</sub> = 150 MPa·µm<sup>½</sup>** value. It's
  fit to one tensile point (60 % CR). We don't have a literature anchor
  for this, and 47 %/53 % CR data doesn't have ASTAR sub-block to test
  against.
- The **Phase 3.6e `ssd_multiplier` knob**. Phase 3.6g's WH analysis
  suggests k=1.0 is correct as a default, but the WH ρ<sub>WH</sub> being
  10× *smaller* than ρ<sub>GND</sub> hints there's something else going
  on — either ASTAR-PED over-counts (the agent's hypothesis), or
  classical WH under-counts in textured BCC by more than the 2-3× we
  expect. We don't have the data to distinguish.
- The **Mondière K<sub>IC</sub> = 110 anchor for predicted K<sub>matrix</sub>**.
  Only one published M54 K<sub>IC</sub> measurement; no error bar reported.
  Our K_matrix-for-target solver returns ~110 MPa·m<sup>½</sup> as
  consistency, but that's not really a test since TRIP is negligible —
  we're solving for K<sub>matrix</sub> ≈ K<sub>IC</sub>.

### Wide-open

- The **K<sub>IC</sub>(CR) trend** measured by the user (219 → 434 doubling).
  No model in the codebase predicts this. Matrix-toughness mechanisms
  (refined block / sub-block deflecting cracks; ductile-tearing energy
  in the sub-block-network plastic zone) are not implemented.
- The **non-monotonic cw/cr austenite at 40 % CR surface** mechanism.
  We have the data. We have a hypothesis (cellular shear-band network +
  surface-localized γ stabilization or formation). We don't have a
  predictive model.
- The **competing-mechanism austenite kinetics** for fitting Olson-Cohen
  M54-specific (α, β). Blocked by the non-monotonicity above.

---

## 6. What the model is good for *right now*

1. **Cross-paper / cross-state consistency**: takes a microstructure spec
   and decomposes σ<sub>y</sub> into named contributions following the
   literature consensus. Useful for thinking about *which lever moves the
   answer* in a specific way.
2. **Sensitivity studies**: run a sweep across one parameter, see how σ<sub>y</sub>
   or K<sub>IC</sub> responds. Knobs are well-instrumented and mostly
   physically meaningful (not all — e.g. the SSD multiplier needs WH-style
   anchoring).
3. **Bound the TRIP contribution**: the framework definitively rules out
   transformation toughening as a primary K<sub>IC</sub> mechanism at M54
   austenite levels. Useful for framing the user's K<sub>IC</sub>-doubling
   data: it can't be TRIP, so what else?
4. **Anchor management**: when new measurements arrive (TEM, EBSD, full
   stress-strain CSV, Charpy raw curves), the framework absorbs them into
   one of three roles — calibration anchor, prediction target, or
   direct-measured input. This makes "what's a real prediction vs what's
   a fit" easy to inspect.

## 7. What it's NOT good for *right now*

1. **Absolute σ<sub>y</sub> prediction at the user's specific cw/cr
   states without 1-knob recalibration**. The +9 % baseline + −16 % cw
   gaps both need investigation; until they're closed the absolute
   numbers are best read as "model + offset = measurement."
2. **K<sub>IC</sub> trend prediction**. We can rule out TRIP; we can't
   yet predict the 219→434 rise. That mechanism is matrix-side and not
   in the codebase.
3. **TRIP at conditions outside M54's regime**. Olson-Cohen is using a
   304 SS literature analog (α=3.55, β=0.30); M54-specific (α, β) is
   blocked by the non-monotonic cw/cr response.

---

## 8. Suggested investigation priorities

Ranked by leverage-per-effort.

### Highest leverage

1. **EBSD on the user's 0 % CR sample to measure the actual block size**
   for the cross-rolled-AF + 516/10-temper state. One scan, settles
   ~50-100 MPa of the +9 % baseline bias. Possibly already done; the
   user's data trove may have it.
2. **TEM on the same 0 % CR sample** for M2C r, L, V<sub>f</sub>. Rules
   out (or pins) the second 50-80 MPa contributor to the baseline bias.
3. **Tensile data for 20 % and 40 % CR** if breakable bars are available.
   Would test whether the Phase 3.6f K<sub>sub</sub>=150 single-point
   calibration generalizes — turns one fit into three predictions.

### Medium leverage

4. **Modified Williamson-Hall** (Borbely 2022) on the user's existing
   XRD spectra. Phase 3.6g's classical WH gave k = 0.06-0.13 vs ASTAR;
   modified WH would shift this by ~2-3× and let us decide which
   measurement to trust.
5. **K<sub>IC</sub> raw curves** to separate K<sub>initiation</sub> from
   K<sub>steady</sub>. Makes the K<sub>IC</sub>(CR) doubling much more
   interpretable mechanistically.
6. **Matrix-toughness model** — implement a sub-block-deflection /
   ductile-tearing K<sub>matrix</sub> increment that depends on cw-induced
   substructure. Would let us actually predict the K<sub>IC</sub>(CR)
   trend instead of just bounding the TRIP ceiling.

### Lower leverage / Phase 4 territory

7. **Competing-mechanism austenite model** for the cw/cr non-monotonicity.
   Big lift for a feature that helps interpret data but doesn't change
   the core σ<sub>y</sub> or K<sub>IC</sub> story much.
8. **HRR-J full angular field** instead of the lite radial-rescale-only
   we have. The Phase 3.6c "lite" version captured the main effect
   (TRIP < 0.3 vs <0.5 MPa·m<sup>½</sup>); full HRR would refine within
   factors of 1.5×.

---

## 9. So where do we land?

### What we've actually learned about M54 from this work

- **TRIP is not a primary toughening mechanism in commercial M54.** The
  ~1-3 % reverted austenite at lath boundaries contributes well under
  1 MPa·m<sup>½</sup> to K<sub>IC</sub> across every model variation we
  tried. Mondière's 110 is matrix-driven.
- **The user's cw/cr microstructure has a non-monotonic surface
  austenite behavior** (1.3 % → 0.5 % → 26.4 % → 17.6 %) that is real
  (XRD bulk, ASTAR surface, nanoindentation E<sub>r</sub> all
  cross-validate the surface phenomenon at 40 % CR), but is decoupled
  from the bulk phase fractions and therefore from the bulk tensile
  response.
- **M54 cold-rolling produces the unusual combination of σ<sub>y</sub>↑
  AND ductility↑** (1300 MPa @ 11 % EL → 1900 MPa @ 20 % EL across
  0 → 60 % CR) AND **K<sub>IC</sub>↑** (219 → 434 MPa·m<sup>½</sup>).
  This is a *real* and unusual finding — classical CW reduces ductility.
  The model rules out TRIP as the explanation; the most likely mechanism
  is the surface-localized cellular shear-band network producing a
  reservoir of strain-hardening sites.
- **The Bain volumetric strain for M54 is +0.022, not the textbook
  +0.04**. This corrects a casual literature value that was compounding
  toughening-prediction overstatements.

### What we've actually built

A literature-consensus strengthening framework that closes four Sun 2022
anchors at ±5 %, captures direction-of-effect on the user's cw/cr σ<sub>y</sub>
sweep, and gives a falsifiable bound on TRIP toughening. The model is
**diagnostic** — it tells us where the assumptions are unconstrained
faster than it tells us the right answer. That's a useful role.

### What I'd say to a stranger about whether they should trust this model

Use it for:
- mechanism reasoning ("which contribution dominates here?")
- bounding TRIP and substructure contributions
- comparing different processing routes at the same temper
- absorbing new measurements into a coherent picture

Don't use it for:
- predicting absolute σ<sub>y</sub> at conditions far from the Sun
  anchors without measurement-anchored recalibration
- predicting K<sub>IC</sub> trends with cold work (matrix mechanisms not
  modeled)
- M54 cw/cr K<sub>IC</sub> doubling has *no* model explanation yet — that
  remains an open scientific question, not just a parameter-tuning issue
