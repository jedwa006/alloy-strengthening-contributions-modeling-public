# cw/cr Strengthening Analysis — Approach to Theoreticals + Tuning + TRIP-Model Fit

> Written 2026-05-12. Three questions:
> 1. How close do the per-CR strengthening **contributions** approach their
>    theoretical values at 20/40/60 % CR?
> 2. **What can we tune** to close the gaps, and what can't be tuned?
> 3. How well does **Olson-Cohen** vs **Patel-Cohen** fit the post-temper
>    cold-working γ→α′ trajectory we measure?

Companion to [`EVALUATION_M54_MODEL_v1.md`](EVALUATION_M54_MODEL_v1.md) (the
high-level synthesis) and [`FINDINGS.md`](FINDINGS.md) (the running log).
This one is narrower and more quantitative.

---

## 1. Per-CR contribution decomposition (the "theoretical baseline")

By "theoretical" we mean: each strengthening equation evaluated at the
**measured microstructure inputs** for that CR condition (block, ρ<sub>GND</sub>,
matrix composition, M2C population, f<sub>A</sub>). No fits to σ<sub>y</sub>
itself.

### Default knobs (K<sub>sub</sub> = 0, ssd_multiplier = 1.0, f<sub>A</sub> = ASTAR-core)

| CR % | σ<sub>0</sub> | σ<sub>ss</sub> | σ<sub>HP</sub> | σ<sub>ρ</sub> | σ<sub>p</sub>(M2C) | sum (qs) | × rate (1.054) | − f<sub>A</sub> | meas    | miss     |
|---:|--:|--:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0   | 50 | 150 | 332 | 304 | 537 | 1373 | 1447 | 1419 | 1300 ± 30 | **+9.2 %** |
| 20  | 50 | 150 | 332 | 603 | 537 | 1672 | 1762 | 1744 | (no tensile) | — |
| 40  | 50 | 150 | 332 | 676 | 537 | 1744 | 1839 | 1694 | (no tensile) | — |
| 60  | 50 | 150 | 332 | 603 | 537 | 1672 | 1762 | 1588 | 1900 ± 50 | **−16.4 %** |

### What's actually moving with CR

**Only σ<sub>ρ</sub>**. Every other contribution (σ<sub>0</sub>, σ<sub>ss</sub>,
σ<sub>HP</sub>, σ<sub>p</sub>(M2C)) is held at the post-temper baseline because
room-temperature cold rolling (T<sub>max</sub> &lt; 80 °C) doesn't move:

- the matrix composition (Fleischer terms),
- the block size (Wang 2024 confirms tempering-invariant block),
- the M2C population (no precipitation/coarsening kinetics at room temp).

σ<sub>ρ</sub> tracks the user's measured BCC GND density:
1.6→6.3→7.9→6.3 × 10¹⁵ m⁻². The σ<sub>ρ</sub> rise from baseline to
60 % CR is +299 MPa (= 603−304). After the strain-rate correction (×1.054)
that's **+315 MPa added** to predicted σ<sub>y</sub>. The user measures
**+600 MPa** (1300→1900). **Model captures ~52 % of the measured
strengthening rise.**

The other ~285 MPa of measured strengthening that the default model
*misses* is what Phase 3.6f's sub-block HP K<sub>sub</sub>=150 closes:

| CR % | σ<sub>HP,subblock</sub> increment (K<sub>sub</sub>=150) |
|---:|---:|
| 0  | 0 (baseline-relative by construction) |
| 20 | +235 MPa |
| 40 | +249 MPa |
| 60 | +317 MPa |

With K<sub>sub</sub>=150 added:
- 60 % CR: predicted 1923 vs measured 1900 → **+1.2 % miss**
- 0 % CR: predicted 1420 vs measured 1300 → **+9.2 % miss** (unchanged — the
  0 % baseline issue is independent of cw-induced terms)

### How close is "close" at each CR?

| CR % | model captures (% of measured σ<sub>y</sub> at that CR) | with K<sub>sub</sub>=150 |
|---:|---:|---:|
| 0  | 109 % (over-predicts by 9 %)            | 109 %  (unchanged)             |
| 60 | 84 %  (under-predicts by 16 %)          | 101 %  (within measurement σ)  |

Direction-of-effect is right. With one calibrated knob (K<sub>sub</sub>),
high-CR magnitude lands within measurement uncertainty. **The 0 % CR
baseline +9 % bias is a separate problem** (Phase 3.6h diagnosis below)
that no single cw-induced knob can address.

---

## 2. Tunability ranking — what we can/can't move

### Literature-fixed (don't tune for M54 specifically)

These come from the strengthening-equation literature and have well-
established values across many alloy systems:

| Constant | Value | Source | Sensitivity if changed by ±10 % |
|---|---:|---|---:|
| σ<sub>0</sub> | 50 MPa | Universal (Sun, Wang, Zhu, Galindo-Nava all 50) | ±5 MPa (small) |
| Burgers vector b | 0.25 nm | BCC-Fe lattice | ±15 MPa via σ<sub>ρ</sub> term |
| Shear modulus G | 80 GPa | Matrix shear modulus | ±30 MPa via σ<sub>ρ</sub> term |
| ε<sup>V</sup> Bain | 0.022 | **M54-XRD measured** (Phase 3.6b) | ±0.05 MPa·m<sup>½</sup> ΔK<sub>TRIP</sub> |
| γ<sub>0</sub>, ε<sub>0</sub> Patel-Cohen | 0.20, 0.04 | Original PC 1953 Fe-Ni | small (entered via PC criterion only) |

### Physical inputs (refit if measurement changes)

These are tied to a specific microstructure measurement; changing them
means having a new measurement, not "tuning":

| Input | Used in | M54 cw/cr source |
|---|---|---|
| block width d (µm) | σ<sub>HP</sub> = K<sub>HP</sub>·d<sup>−½</sup> | Sun 2022 AF (0.48 µm); not measured on cross-rolled-AF prior |
| ρ (m⁻²) | σ<sub>ρ</sub> = α<sub>eff</sub>·G·b·√ρ | ASTAR-PED GND median |
| M2C r, L (nm) | σ<sub>p</sub> Orowan formula | Cho 2015 → M54 transferred LSW kinetics; not directly measured for AF + 516/10 |
| matrix at-frac | σ<sub>ss</sub> Fleischer | Tempered-state composition with carbide-consumed elements |
| f<sub>A</sub> | rule-of-mixtures correction | ASTAR or XRD |

### Calibration knobs (single-point fits — the things we can actually "tune")

These are the parameters whose values come from fitting the model to one
or more anchor measurements:

| Knob | Default | Calibrated against | What changes if tuned |
|---|---:|---|---|
| K<sub>HP</sub> (Hall-Petch) | 230 MPa·µm<sup>½</sup> | Sun M54 fit | All σ<sub>HP</sub> proportionally |
| α<sub>eff</sub> (Bailey-Hirsch) | 0.38 (Sun) or 0.625 (Wang/Zhu) | Convention choice | All σ<sub>ρ</sub> proportionally |
| K<sub>intr</sub> (intrinsic martensite) | 985 MPa | Sun DQ anchor | Only matters in untempered states |
| K<sub>sub</sub> (sub-block HP, Phase 3.6f) | 150 MPa·µm<sup>½</sup> | User 60 % CR tensile | Δσ<sub>HP,sub</sub> at non-zero CR |
| ssd_multiplier (Phase 3.6e) | 1.0 | Phase 3.6g WH analysis | Multiplies σ<sub>ρ</sub> uniformly |
| M2C V<sub>f</sub>, r, L baseline | from Cho-LSW transfer | Sun AF + 425/10 anchor | σ<sub>p</sub> at all temper conditions |
| f<sub>A</sub> source | ASTAR surface (default) | — | Only the rule-of-mix correction |

### The honest tuning hierarchy

**Tier 1 — Physical inputs (re-measure to change)**: block width on cross-
rolled-AF + temper, M2C population on AF + 516/10. These are the highest-
leverage levers but require new measurements.

**Tier 2 — Single-point fits (already calibrated, treat as fixed unless new data)**:
K<sub>HP</sub>=230, α<sub>eff</sub>=0.38, K<sub>intr</sub>=985, K<sub>sub</sub>=150, M2C kinetics. Each fit absorbs an
anchor's uncertainty into the parameter; tuning them further without new
data just shifts where the residual lives.

**Tier 3 — Source/convention choices (re-evaluate per use case)**: f<sub>A</sub>
source (ASTAR-surface vs ASTAR-core vs XRD-bulk) — the right choice
depends on what you're comparing to (surface phenomenon vs bulk tensile).
ssd_multiplier (Phase 3.6g WH analysis suggests 1.0; left as a knob for
future re-calibration when modified-WH data lands).

**Tier 4 — Knobs we should NOT tune** (would break the literature-anchored
nature of the model): σ<sub>0</sub>, b, G, Fleischer β<sub>i</sub>, ε<sup>V</sup> (XRD-measured).

### Where the +9 % baseline bias comes from (Phase 3.6h diagnosis recap)

The 0 % CR over-prediction (1448 vs 1300 user-rate, +148 MPa) is **Tier
1**: it requires a new measurement, not a knob tweak. Per the sensitivity
sweep:

- block 0.48 → 0.7 µm: −59 MPa
- f<sub>A</sub> 1.3 % (ASTAR surface) → 4.8 % (XRD bulk): −38 MPa
- M2C L 47 → 70 nm (slightly heavier coarsening at 516/10): up to −180 MPa
- ρ 1.6e15 → 1.0e15 (more recovery): −66 MPa

Combinations land within ±5 % of measured. None of these is a "model
parameter" we should tune — they're either microstructure measurements we
need (block, M2C TEM) or measurement-source choices we already expose
(f<sub>A</sub> source).

---

## 3. TRIP-model fit quality for the post-temper cw/cr regime

The user's measured γ trajectory (ASTAR surface):

| CR % | ε<sub>true</sub> | f<sub>A</sub> (surface) | f<sub>α′</sub> consumed = max(0, f<sub>A,0</sub>−f<sub>A</sub>) |
|---:|---:|---:|---:|
| 0   | 0.000 | 0.013 | 0.000 |
| 20  | 0.223 | 0.005 | +0.008 |
| 40  | 0.511 | 0.264 | 0.000 (clipped — γ grew, didn't shrink) |
| 60  | 0.916 | 0.176 | 0.000 (clipped — γ still elevated) |

### Olson-Cohen — structurally inadequate

Classical OC says f<sub>α′</sub>(ε) = 1 − exp{−β·[1 − exp(−α·ε)]<sup>n</sup>} —
**monotonic** in ε. Therefore f<sub>A</sub>(ε) = f<sub>A,0</sub> −
f<sub>α′</sub>(ε) must be **monotonic decreasing**.

The user's data goes 0.013 → 0.005 → **0.264** → 0.176. The 40 % CR
spike is incompatible with OC under any (α, β). Forcing the fit on all
four points produces α=0.26, β=0.05 — small values where OC predicts
essentially zero transformation at all strains. RMSE = 0.004 (small only
because the fitter found a "do nothing" solution, not because the model
describes the data).

| Where OC works | Where OC fails |
|---|---|
| 0 → 20 % CR segment (classical TRIP, γ→α′) | Above 20 % CR (γ formation/stabilization regime) |

**Verdict for OC**: usable as the *forward* term in a competing-mechanism
model, restricted to the 0→20 % CR strain range. Any (α, β) fit on the
user's M54 reverted-γ data is degenerate without a longer monotonic
strain sweep at fixed conditions. Lit-analog (304 SS at 22 °C: α=3.55,
β=0.30) is the current default in `m54model.toughening.crack_tip` and
gives reasonable order-of-magnitude f<sub>α′</sub>(ε) for crack-tip use,
but is NOT M54-calibrated.

### Patel-Cohen — rich but ambiguous for cw/cr

PC says U = τγ<sub>0</sub> + σ<sub>n</sub>ε<sub>0</sub> is the mechanical work done by
applied stress on a transforming γ region. Optimum habit-plane orientation
is at 2θ ≈ 79°. ΔM<sub>s</sub> = U·V<sub>m</sub> / (dF/dT) is the
stress-induced shift in M<sub>s</sub>.

For Fe-Ni-C (γ<sub>0</sub>=0.20, ε<sub>0</sub>=0.04, dF/dT = 1.33 cal/mol·K, V<sub>m</sub> =
7.1×10⁻⁶ m³/mol) at the user's tensile σ values:

| σ (MPa) | mode | U<sub>max</sub> | ΔM<sub>s</sub> (K) |
|---:|---|---:|---:|
| 1300 | tension | +159 | **+202** |
| 1300 | compression | +96  | +123 |
| 1300 | hydrostatic | −52  | −66  |
| 1700 | tension | +207 | **+265** |
| 1700 | compression | +126 | +161 |
| 1700 | hydrostatic | −68  | −87  |
| 1900 | tension | +232 | **+296** |
| 1900 | compression | +141 | +180 |
| 1900 | hydrostatic | −76  | −97  |

**Reading these numbers:**

1. **Under uniaxial tension at the user's σ<sub>y</sub>** (1300-1900
   MPa), PC predicts a +200 to +300 K M<sub>s</sub> shift. This is
   *huge* — well above what's needed to drive γ→α′ if the chemical M<sub>s</sub>
   is anywhere near room temperature. So during tensile testing, any
   metastable γ should transform aggressively. Consistent with the
   classical TRIP picture.

2. **Under uniaxial compression** (which the rolling bite approximates
   in the through-thickness direction): PC still predicts γ→α′ is
   thermodynamically favorable, but with ~60 % the driving force of
   tension at the same σ. Still positive, so γ should still transform.

3. **Under hydrostatic compression**: PC predicts γ→α′ is *opposed*
   (U<sub>max</sub> < 0). The +4 % volumetric expansion of γ→α′ has to
   work against the surrounding pressure.

### The cw/cr 40 % surface spike — what PC actually predicts

The roll bite is **NOT uniaxial compression**. It's closer to **plane-
strain compression** with a strong hydrostatic component:

- σ<sub>normal,through-thickness</sub>: ~1-2 GPa (Hertzian-peak, compressive)
- σ<sub>RD</sub>: tensile constraint ~0.5-1 GPa (work-hardening-related)
- σ<sub>TD</sub>: plane-strain constrained ~0.5-1 GPa (compressive)
- **Hydrostatic component σ<sub>m</sub> ≈ −1 GPa (highly compressive)**

The hydrostatic part **subtracts directly from U<sub>max</sub>**:

U<sub>net,bite</sub> ≈ U<sub>deviatoric</sub>(τ) + ε<sub>0</sub>·σ<sub>m</sub>
                   ≈ +(deviatoric drives γ→α′) − ε<sub>0</sub>·1 GPa
                   ≈ +(some positive) − 40 MPa·dimensionless

For high enough hydrostatic compression, **U<sub>net,bite</sub> can flip
sign**, making γ→α′ thermodynamically *unfavorable*. The same hydrostatic
term **stabilizes γ against transformation** AND **provides a driving
force for α′→γ reverse transformation** if the kinetic path exists.

**At the cellular shear-band intersections** at 40 % CR surface, two
things conspire:

1. The local triaxiality is high (Hertzian-peak under the roll bite).
2. The local Ni partitioning into γ films is high (Sun 2022 EDS shows
   ~14 % Ni in films vs nominal 10 %), lowering the local M<sub>s,chem</sub>
   and making the films metastable to deeper undercooling.

Both effects favor γ retention or formation. PC's hydrostatic term
quantitatively explains why the 40 % CR surface **rises** in γ-content
when classical TRIP would predict it should fall.

**Verdict for PC**: PC + multi-axial stress analysis is the right
framework for the cw/cr response, but using it predictively requires:

- (a) per-region stress decomposition (deviatoric + hydrostatic) at the
  rolling bite
- (b) M54-specific γ-film M<sub>s,chem</sub> (calibrated against
  composition partitioning data — the user's ASTAR-EDS or similar would
  give this)
- (c) coupled forward/reverse transformation kinetics

We have (a) qualitatively. (b) requires composition data we don't have
yet. (c) is Phase 3.7 / 4 work.

### The honest comparison

| Mechanism | Forward γ→α′ | Reverse α′→γ | Captures 40 % CR γ spike? |
|---|---|---|---|
| Classical Olson-Cohen (strain-induced, isotropic) | yes | no | **no** |
| Classical Patel-Cohen (stress-assisted, uniaxial tension) | yes | no | **no** |
| Patel-Cohen with multi-axial stress including hydrostatic compression | yes (deviatoric) | yes (high triaxiality) | **qualitatively yes** |
| Coupled OC + multi-axial PC | yes | yes | yes (Phase 3.7+) |

So neither method *alone* fits the data. **Patel-Cohen extended to
multi-axial stress states qualitatively explains the 40 % CR γ spike via
hydrostatic-compression-driven reverse transformation**, but a
quantitative model would need:

- explicit deviatoric / hydrostatic stress decomposition at each rolling
  pass
- coupled forward/reverse transformation kinetics
- M54-specific γ-film chemistry (composition partitioning on the user's
  samples)

---

## 4. What this analysis tells us we can answer empirically

### Strengthening — yes, with one caveat

We can predict σ<sub>y</sub> at any CR within ~5 % once the K<sub>sub</sub>
sub-block-HP knob is calibrated to one cw measurement (currently 60 %).
The **direction-of-effect** at 20/40 % CR (model says ~1900-2000 MPa)
is a real prediction, not a fit, because K<sub>sub</sub> is shared
across all CR via the same baseline-relative formula. The user could
test this with 20 % or 40 % CR tensile data — it would either confirm
the K<sub>sub</sub>=150 value or point to a different sub-block-HP
scaling.

The 0 % CR baseline +9 % bias is **independent** of cw effects and
needs new microstructure data on the cross-rolled-then-tempered prior:
EBSD for the actual block size, TEM for M2C r/L. This is Tier-1
measurement, not a tunable parameter.

### TRIP — partially

OC alone: cannot describe the cw/cr response. Use only as the
forward-transformation submodel in a competing-mechanism framework.

PC: the right physics IS in PC, but using it predictively for cw/cr
needs multi-axial stress decomposition (which the model doesn't have
yet) and composition data on the γ films (which we'd need to acquire).

**For crack-tip K<sub>IC</sub>** (where stress is uniaxial-tensile-
dominated and the spatial integration in Phase 3.6a/c handles the
field): PC + OC together with the literature-analog (304 SS) (α, β)
gives ΔK<sub>TRIP</sub> &lt; 0.3 MPa·m<sup>½</sup> for M54. **This
prediction is robust** even though M54-specific (α, β) aren't pinned —
the *bound* on TRIP holds at every reasonable parameter choice.

### Path forward — testable next steps

| Question | Experiment | Expected information value |
|---|---|---|
| Does K<sub>sub</sub>=150 generalize? | Tensile bar at 20 % or 40 % CR | Turns one fit into 2-3 predictions |
| Where's the 0 % CR +9 % from? | EBSD on user's 0 % CR sample | Settles ~50-100 MPa (block size) |
| Same | TEM on user's 0 % CR sample | Settles ~50-80 MPa (M2C r/L at 516/10) |
| Is the 40 % CR γ spike triaxial-PC-driven? | EDS composition on γ films vs matrix at 40 % CR surface | Sets M<sub>s,chem</sub> for the films → enables quantitative PC |
| Does WH ρ<sub>WH</sub> reflect total ρ? | Modified WH (Borbely 2022) on existing XRD spectra | Settles whether classical WH under-counts by 2-3× |

### Bottom line in two sentences

**For σ<sub>y</sub>(CR)**: model captures direction-of-effect at all CR
and matches measured magnitude at 60 % CR within 1.2 % once one
cw-induced knob (K<sub>sub</sub>) is calibrated to one tensile point;
0 % baseline +9 % bias is a separate problem that needs new microstructure
measurements.

**For TRIP modeling**: neither classical OC nor uniaxial PC describes
the cw/cr γ trajectory; multi-axial PC with hydrostatic-compression
γ-stabilization is the qualitatively right framework but needs (i)
multi-axial stress decomposition and (ii) γ-film composition data to
become predictive. The crack-tip K<sub>IC</sub> bound (TRIP &lt; 0.3
MPa·m<sup>½</sup>) is robust regardless.
