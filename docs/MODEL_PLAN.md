# M54 Strengthening-Contribution Model — Plan v1

> Working plan for the Ferrium M54 strengthening + toughening model. This document is the planning artifact that precedes any code. Living doc — revise as we learn.

## 0. Project goal in one paragraph

Build a quantitative, calibratable model of yield strength (and second-tier toughness) for **Ferrium M54** across four microstructural states — **mill-anneal (MA)**, **direct-quench (DQ)**, **direct-quench + temper (DQ+T)**, and **ausformed + temper (AF+T)** — that decomposes the result into named physical contributions (lattice friction, solid solution, Hall-Petch, dislocation, M2C-Orowan, MC-Orowan, retained-austenite mixing, TRIP-toughening). Calibrate against the user's own Sun 2022 data + the Mondière 2018 / B. Wang 2024 commercial-temper anchors. Make it interactively explorable so the user can sweep heat-treatment parameters and see contributions move.

## 1. The four microstructural states

We anchor everything to these four states. Notation matches Sun 2022.

| State | Shorthand | Processing | Why we care |
|-------|-----------|------------|-------------|
| **Mill-anneal** | MA | Equilibrium ferrite + carbides as supplied (slow-cooled from sub-critical anneal). | Starting point for fabrication; needs hardness/machinability prediction; rare to see in service. |
| **Direct-quench** | DQ | 1060 °C / 1 h austenitize → oil quench → −76 °C / 2 h cryo (per QuesTek QPI-M54). | Fully martensitic baseline. Pre-temper. Sun 2022 has direct measurements. |
| **DQ + temper** | DQ+T | Above + temper. Commercial recipe: **516 °C / 10 h**. Mondière + B. Wang study near this point. | The standard commercial state. Most published M54 data sits here. |
| **Ausformed + temper** | AF+T | Solutionize → cool to ausforming-T (550 °C in Sun 2022) → roll (45 % reduction in Sun 2022) → oil quench → cryo → temper. Sun 2022 uses **AF550/45 + T425/10**. | The user's own enhanced-processing route. Faster kinetics, refined microstructure. |

Two sub-states inside DQ+T and AF+T worth noting:
- **Q-C** (quenched + cryo, no temper): the immediate post-cryo state, the precursor to all tempering.
- **Over-tempered** (e.g. 520 °C / 100 h+ in Wang 2024, or 516 °C / 500 h in Mondière for XRD): a useful end-of-life regime for embrittlement studies.

## 2. The strengthening equation (canonical form)

Adopt the form Sun 2022 uses (which is the form **the user co-authored**), with named-options where conventions diverge:

$$ \sigma_y \;=\; \sigma_0 \;+\; \sigma_{ss} \;+\; \sigma_{H\text{-}P} \;+\; \sigma_\rho \;+\; \sigma_p $$

with:

$$
\sigma_p \;=\; \sqrt{\sigma_{M_2C}^{\,2} \;+\; \sigma_{MC}^{\,2}}
\quad\text{(Pythagorean per Xiong 2021 review and Wang 2024)}
$$

For tempered states with non-trivial reversed-austenite fraction:

$$ \sigma_y^{\,\text{eff}} \;=\; (1 - f_A)\,\sigma_y \;+\; f_A\,\sigma_A $$

The decomposition is opinionated (linear top-level sum, Pythagorean within precipitation). Wang 2024 uses Pythagorean on (σ_Mart² + σ_p²) at the top level too — we'll support both as a configurable strategy.

## 3. Knowledge inventory by state

Per state: **what we know from lit (✓), what we have as constants (★), what we need from experiment (?), and what we ballpark/derive (≈)**. References in `[brackets]` use our citekeys.

### 3.1 State: MA — mill-anneal

| Item | Status | Source / value |
|------|--------|----------------|
| Composition | ✓ | `[zhu07_Mondiere_2018]`, `[sun_main]`: Fe-0.30C-1Cr-10Ni-7Co-2Mo-1.3W-0.1V-0.013Ti |
| Equilibrium phase fractions at MA T | ≈ | Thermo-Calc TCFE → ferrite + M23C6 + MC. We don't have anyone's Thermo-Calc M54 output yet — would need to run or re-extract. |
| Microstructure (ferrite grain size) | ? | No literature on MA M54. Need user data or estimate from typical mill-anneal practice. |
| YS / hardness | ? | No published. Estimate from rule-of-mixtures on equilibrium phases. |
| Use in model | mostly a starting-point for processing path; MA isn't a "model output" condition we'd normally predict. |

### 3.2 State: DQ — direct quench (post-cryo, no temper)

| Item | Status | Source / value |
|------|--------|----------------|
| YS, UTS, EL | ✓ | `[sun_main]`: **YS 1420 / UTS 1916 / EL 14.9 %** |
| Hardness (HV0.5) | ✓ | `[sun_main]`: ~560 HV |
| Block width d_block | ✓ | `[sun_main]`: **1.18 µm** (DQ is the un-refined baseline) |
| PAG width | ✓ | `[sun_main]`: 100 µm |
| Packet size | ✓ | `[sun_main]`: 13.1 µm |
| Lath width | ✓ | `[sun_main]`: 70–200 nm (TEM, range) |
| Dislocation density ρ | ✓ | `[sun_main]`: **2.08 × 10¹⁵ m⁻²** (Williamson–Hall, post-cryo) |
| Solid-solution composition (matrix) | ≈ | C is mostly trapped in solution at DQ (no M2C precipitation yet); other substitutionals at nominal levels. Fleischer with Zhu Table 3 β coefs. |
| MC carbide population (undissolved Ti-MC pinners) | ✓ | `[zhu07_Mondiere_2018]`: ~70 nm mean (50–120 nm range), f_v ≈ 6 × 10⁻⁴, N ≈ 3 × 10¹⁹ m⁻³, comp (Ti₀.₄₄Mo₀.₂₇W₀.₁₃V₀.₁₆)C |
| M2C carbide population | ✓ | None — no precipitation in DQ state |
| Retained austenite | ≈ | Likely <1 vol % after −76 °C cryo (per `[sun_main]`'s "no obvious RA"). |
| Calibration anchor | ✓ | YS 1420 → strong test of σ_0+σ_ss+σ_HP(d=1.18)+σ_ρ(2.08e15)+σ_MC(undissolved) sum |

**Predicted YS for DQ (sanity check):**
- σ_0 = 50, σ_ss(Fleischer) ≈ 220 (rough — needs computation), σ_HP = 300/√1.18 = **276 MPa**, σ_ρ = 0.25·2.5·80×10³·0.25e-9·√(2.08e15) = **571 MPa**, σ_MC ≈ small (~25 MPa for Orowan on r=35 nm, f_v=6e-4)
- Sum ≈ 1142 MPa vs measured 1420 → 280 MPa under-predict. Need to revisit Fleischer (probably larger than 220 at DQ when C is in solution — Wang 2024's σ_ss = 195 is for tempered states where C has dropped to ~0.003 wt%).
- The carbon-in-solution contribution is huge at DQ. Fleischer β_C is typically ~1700–2000 MPa·(at-frac)^(1/2). At 0.30 wt% ≈ 1.4 at%, this gives σ_C ≈ 1700·√0.014 ≈ 200 MPa — that closes most of the gap.
- **Open question**: how does Fleischer Co contribute? Galindo-Nava omits Co from their β table; Zhu has β_Co = 200 MPa.

### 3.3 State: DQ + T (commercial peak: T516/10)

| Item | Status | Source / value |
|------|--------|----------------|
| YS, UTS, EL @ T516/10 | ✓ | `[sun_main]`: **YS 1762 / UTS 2050 / EL 14.9 %** |
| Hardness | ✓ | `[sun_main]`: 618 HV ≈ 54 HRC |
| KIC | ✓ | `[zhu07_Mondiere_2018]`: 110 MPa·m^(1/2); commercial spec ≈ 126 |
| Block width | ✓ | `[sun_main]`: ~1.18 µm (block size doesn't change in tempering — Wang 2024 confirms) |
| Dislocation density (post-temper) | ✓ | `[sun_main]`: 1.12 × 10¹⁵ m⁻² (drops from 2.08 due to recovery) |
| M2C size (commercial peak) | ✓ | `[zhu07_Mondiere_2018]`: 9.6 nm × 1.2 nm rod, aspect ratio 10 |
| M2C composition | ✓ | `[zhu07_Mondiere_2018]` (APT): (Mo₀.₅₀Cr₀.₁₂₅W₀.₁₀Fe₀.₁₀Ni₀.₁₀V₀.₀₂₅)₂C |
| M2C number density / volume fraction | **GAP** | **Mondière doesn't report N or f_v at 516/10**. Wang 2024 at 520/8: N = 650 µm⁻², spacing 12.3 nm. Use Wang's data with small JMA extrapolation 520→516 °C. |
| MC strip-segregation | ≈ | Likely starts past peak (Wang 2024 at 520/10 shows it). At 516/10 may be marginal. |
| Cementite | ✓ | "Very few" per Mondière. W stabilizes M2C and consumes C without leaving Fe3C. |
| Reversed austenite | **GAP** | Wang 2024 detected weak (111)γ XRD peak but did not quantify. Cross-reference Zhang 2022 (cryo paper) and/or measure independently. |
| Strengthening decomposition | ✓ | Wang 2024 at 520/8 (close enough): σ_f=50, σ_ss=195, σ_Mart=390, σ_p(M2C)=980, predicted σ_y ≈ 1620, measured 1747 → 127 MPa gap = MC contribution + model error |
| Calibration anchor | ✓ | YS 1762 (Sun 2022 measured DQ+T516/10) |

**This is the best-characterized state.** Wang 2024's strengthening decomposition is essentially a turn-key import for our model.

### 3.4 State: AF + T (Sun 2022 enhanced route: AF550/45 + T425/10)

| Item | Status | Source / value |
|------|--------|----------------|
| YS, UTS, EL | ✓ | `[sun_main]`: **YS 1726 / UTS 2222 / EL 15.5 %** |
| Hardness | ✓ | `[sun_main]`: 629 HV at peak (T425/10 of AF550/45) |
| Block width (post-AF) | ✓ | `[sun_main]`: **0.48 µm** at AF550/45 — refined ~2.5× vs DQ |
| PAG (post-AF) | ✓ | `[sun_main]`: 47 µm (vs 100 µm DQ — elongated by deformation) |
| Dislocation density (post-AF, pre-temper) | ✓ | `[sun_main]`: **7.81 × 10¹⁵ m⁻²** (3.75× DQ — the ausforming density) |
| Dislocation density (after T425/10) | ✓ | `[sun_main]`: **1.18 × 10¹⁵ m⁻²** (recovered, converged with DQ+T) |
| Hardness drop on tempering (AF) | ✓ | 660 → 629 HV at 425 °C / 10 h (5 % drop, vs DQ which gains 60 HV from precipitation) |
| M2C kinetics in AF state | ≈ | **Cho 2015** for 13Co-8Ni: E_eff(nucleation, severely-rolled) = 137 kJ/mol, peak time ~1 h vs 10 h undeformed (10× faster). For M54 AF550/45, ballpark interpolation: E_eff ≈ 150–200 kJ/mol, peak time ~5–10× faster than DQ. |
| M2C population at peak (AF) | ≈ | Cho's H600 at peak: r ≈ 1.52 nm, N = 14.65 × 10²² m⁻³, V_f = 0.0040 (roughly 3× higher N, 30 % smaller r vs Ho) |
| MC at AF | ≈ | Likely refined and increased number density (similar logic to M2C). No direct M54-AF data. |
| Reversed austenite (AF + T) | **GAP** | Sun 2022 did not characterize. Likely present but quantification needed. |
| Strengthening decomposition (AF+T) | **GAP** | Sun 2022 only did dislocation+block-size partition (314 + 120 MPa = 434 vs 410 measured). σ_p was NOT quantified. **The biggest gap our model fills.** |
| Calibration anchor | ✓ | YS 1726 (Sun 2022 AF550/45 + T425/10) |

**The model fills Sun 2022's open σ_p gap** by combining Cho-2015 kinetics (transferred to M54 chemistry) with Wang-2024-style Orowan computation. This is the paper our work continues from.

### 3.5 Universal constants (used everywhere)

> Convention conflicts noted. Default = Sun 2022 (user's own paper) unless physically wrong.

| Constant | Sun 2022 | Wang 2024 / Zhu 2025 | Galindo-Nava 2015 | Default in model |
|----------|---------:|---------------------:|------------------:|-----------------:|
| σ_0 (lattice friction)         | 50 MPa   | 50 MPa  | 50 MPa  | **50 MPa** |
| M (Taylor factor)              | 2.5      | 2.5     | 3.0     | **2.5** (Sun) |
| G (matrix shear modulus)       | 80 GPa   | 80 GPa  | 80 GPa  | **80 GPa** |
| G_NiAl (if applicable)         | —        | 88 GPa  | —       | 88 GPa (M54 has no Al, so unused) |
| b (Burgers vector)             | 0.25 nm  | 0.25 nm | 0.286 nm† | **0.25 nm** (Sun) |
| α (Bailey-Hirsch)              | **0.38** | 0.25    | 0.25    | **0.38** (Sun, user's paper) — flag option for 0.25 |
| K_HP (Hall-Petch coef)         | **230 MPa·µm^½** | 300 MPa·µm^½ | 300 MPa·µm^½ | **230** (Sun) — flag option for 300 |
| d (Hall-Petch length)          | block size | block size | block size (per Morito 2006) | **block size** |
| σ_A (austenite YS)             | — | 360 MPa (Li 2026 C64) | — | **360 MPa** (only used if f_A > 0) |
| r_c (NiAl shearing → Orowan)   | — | 3.8 nm | — | unused for M54 (no Al) |
| σ_ss (in tempered state)       | — | 195 MPa (Zhang 2022) | — | **195 MPa** as fast option; Fleischer for full sweep |

† Galindo-Nava's b = 0.286 nm appears to be a₀ of α-Fe, not Burgers vector; |b| = a₀√3/2 ≈ 0.248 nm. Likely a typo or model choice on their part — flag.

**Fleischer β coefficients** (Zhu 2025 Table 3, MPa per √(at-frac)):

| Element | Co | Ni | Cr | Mo | Al |
|---------|---:|---:|---:|---:|---:|
| β_i     | 200.0 | 405.8 | 174.0 | 953.5 | 196 |

Missing for M54: **β_W and β_V**. Galindo-Nava's Eq. (Appendix A) lets us compute them from atomic radius and shear modulus mismatch. β_C also missing — for DQ where C is in solid solution (~0.014 at frac), this is non-trivial; need from Krauss 1999 (`[sun20_Krauss_1999]`) or similar.

## 4. Architecture proposal

### 4.1 Code language and framework

**Python 3.11+**. Reasoning:
- The user has materials-science-Python literacy implied (Thermo-Calc Python API, MATLAB → Python migration is common in the field).
- Excellent Jupyter / scientific stack (NumPy, SciPy, pandas, matplotlib).
- Cleanly callable from notebooks AND from CLI scripts AND from a future web UI.
- `pydantic` for the typed data model (alloy composition, microstructural state, model constants).
- `pint` for units (we'll have nm, µm, m⁻², MPa, GPa, kJ/mol, K — easy to slip up).
- Optional Streamlit later for a quick interactive UI (low effort, no JS).

Other languages considered and rejected:
- Julia: faster, nicer syntax for math, but smaller ecosystem and the user is more likely Python-fluent.
- Rust + WASM: massive overkill for a calculation that runs in milliseconds.
- MATLAB: locks the user to a license, harder to share.

### 4.2 Module layout

```
m54model/
├── alloys/
│   ├── __init__.py
│   ├── ferrium_m54.py     # composition + nominal property dataclass
│   └── compositions.py    # generic Composition dataclass with at%/wt% conversion
├── states/
│   ├── __init__.py
│   ├── base.py            # MicrostructuralState dataclass: block, packet, PAG, lath, ρ, retained_aust, etc.
│   ├── mill_anneal.py     # MA-state factory
│   ├── direct_quench.py   # DQ-state factory (calibrated to Sun 2022 DQ data)
│   ├── tempered.py        # DQ+T or AF+T state factory + temper kinetics evolution
│   └── transitions.py     # how to evolve from one state to another (e.g., apply tempering to DQ)
├── precipitates/
│   ├── __init__.py
│   ├── base.py            # PrecipitatePopulation dataclass: N, V_f, r, l/d aspect, composition, structure
│   ├── m2c.py             # M2C-specific kinetics (JMA per Wang 2024 or Cho 2015)
│   ├── mc.py              # MC carbide model
│   └── mondiere_anchors.py # the Mondière 2018 measured population at 516°C/10h
├── strengthening/
│   ├── __init__.py
│   ├── friction.py        # σ_0
│   ├── solid_solution.py  # Fleischer with extensible β table
│   ├── hall_petch.py      # σ_HP (configurable d)
│   ├── dislocation.py     # σ_ρ Bailey-Hirsch (configurable α, M)
│   ├── orowan.py          # σ_p Ashby-Orowan for M2C, MC
│   ├── mixing.py          # rule-of-mixtures with retained austenite
│   └── total.py           # σ_y assembly with strategy choice (linear / Pythagorean)
├── toughening/
│   ├── __init__.py
│   ├── patel_cohen.py     # stress-assisted γ → α′ criterion
│   ├── olson_cohen.py     # strain-induced kinetics (sigmoidal master eq)
│   └── crack_tip.py       # combine for K_IC contribution at crack tip
├── kinetics/
│   ├── __init__.py
│   ├── jma.py             # JMA / Avrami formalism
│   ├── lsw.py             # LSW coarsening
│   └── transferred.py     # Cho 2015 → M54 kinetics transfer with documented assumptions
├── thermo/
│   ├── __init__.py
│   └── thermocalc_proxy.py # placeholder for Thermo-Calc API; for now, hard-coded equilibrium tables from Mondière + Wang
├── constants.py            # the universal constants table (Section 3.5 above)
├── model.py                # high-level Model class: feed alloy + processing path → state → strength + toughness
├── calibration/
│   ├── __init__.py
│   ├── anchors.py         # Sun 2022, Wang 2024, Mondière 2018 calibration data
│   └── fit.py             # parameter-fitting utilities (e.g., fitting K_HP to a calibration set)
└── plotting/
    ├── contributions.py    # stacked-bar of σ_y decomposition (Wang 2024 Fig. 15 style)
    ├── tempering.py        # YS/UTS/HV vs tempering time at given T (Wang 2024 Fig. 11 style)
    └── pareto.py           # YS vs Akv2 (Zhu Fig. 2c style)

tests/
├── ...                    # one test per module; each must reproduce a published number to within stated tolerance

scripts/
├── reproduce_sun_2022.py   # smoke test: model the AF and DQ + T conditions, compare to published values
├── reproduce_wang_2024.py  # smoke test: 520 °C tempering time series
├── sweep_temper.py         # CLI: sweep T,t around 516 °C / 10 h
└── interactive_ui.py       # Streamlit app (Phase 3)

notebooks/
├── 01_introduction.ipynb           # walkthrough of the model API
├── 02_DQ_baseline.ipynb            # reproduce Sun 2022 DQ result
├── 03_DQT_commercial.ipynb         # reproduce DQ+T516/10 with Mondière + Wang anchors
├── 04_AF_route.ipynb               # reproduce AF550/45+T425/10 with Cho-transferred kinetics
├── 05_TRIP_toughening.ipynb        # Patel-Cohen + Olson-Cohen at the crack tip
└── 06_temper_optimization.ipynb    # find the optimal temper for a given strength/toughness target
```

### 4.3 Data flow

```
Alloy (composition) ─┐
                     ├──► State factory ──► MicrostructuralState ──► σ_y, K_IC, contributions dict
Processing path ─────┘                          (block, ρ, precipitates, f_A)
```

Three layers, each independently testable:
1. **Processing → state**: how heat treatment yields microstructure (largely driven by JMA kinetics, Sun 2022 measurements, Cho 2015 transferred ausforming acceleration).
2. **State → contributions**: pure equation evaluation, no kinetics.
3. **Contributions → totals**: choice of summation strategy (linear vs Pythagorean).

The user can swap any layer — provide their own measured state (skip layer 1), provide their own constants (override layer 2 defaults), or extract per-contribution numbers without summation (skip layer 3).

### 4.4 Key API sketch

```python
from m54model import M54, ProcessingPath, Model
from m54model.processing import austenitize, oil_quench, cryo, ausform, temper

# Define the heat treatment path declaratively
path = ProcessingPath([
    austenitize(T=1060, t=1.0),       # °C, h
    oil_quench(),
    cryo(T=-76, t=2.0),
    ausform(T=550, reduction=0.45),    # optional — skip for DQ route
    temper(T=425, t=10),
])

model = Model(alloy=M54, path=path)
state = model.evolve()                 # → MicrostructuralState
result = model.predict()                # → ResultBundle (sigma_y, K_IC, contributions)

print(result.contributions)
# {'sigma_0': 50, 'sigma_ss': 195, 'sigma_HP': 433, 'sigma_rho': 280,
#  'sigma_M2C': 980, 'sigma_MC': 65, 'sigma_p': 982, 'sigma_y_total': 1740}

result.plot_contributions()             # stacked-bar Wang 2024 Fig. 15 style
result.plot_vs_anchor("Sun2022_AF550_T425_10")  # overlay measured
```

## 5. TRIP toughening submodel

Anchors at `[trip_PatelCohen_1953]` (mechanical driving force) and `[trip_OlsonCohen_1975]` (strain-induced kinetics).

Operationally:

1. **At the crack tip**, compute the local stress + strain field via HRR or a calibrated effective-stress proxy.
2. For each austenite-film element in the plastic zone:
   - Compute U = τγ₀ + σε₀ (Patel-Cohen).
   - If U + ΔG_chem(T) ≥ ΔG_crit → instantaneous γ → α′ (stress-assisted).
   - Else if local plastic strain > 0 → apply Olson-Cohen f_α′ = 1 − exp{−β[1 − exp(−αε)]^n} with α(T), β(T) calibrated to M54 reversed-austenite films (TRIP-steel parameter transfer is a documented assumption).
3. Sum the volume fraction of newly transformed α′ in the plastic zone.
4. Crack-tip shielding from the +4 % volume expansion → ΔK_IC contribution.

**Transformation strains** for M54 reversed austenite are not directly measured in our literature. Default: γ₀ ≈ 0.20, ε₀ ≈ 0.04 (Fe-Ni values from Patel-Cohen). M54 carbon and Co contents may shift these — ballpark with Bain distortion calc.

**ΔG_chem(T)** for M54 reversed austenite chemistry: needs Thermo-Calc TCFE database run, OR transfer from `[zhu39_Ghosh_Olson_1999]` paraequilibrium analysis. Until then, document as an estimated parameter.

This submodel can be developed and validated independently of the strength model; its output ΔK_IC is layered onto the matrix K_IC contribution at the end.

## 6. Calibration & validation strategy

Three calibration anchors (the "must reproduce these") and several validation cross-checks (the "should match these too").

### Calibration set — the model MUST reproduce these to ±5 %

| Anchor | Source | Predicted YS | Tol | Notes |
|--------|--------|--------------|-----|-------|
| **DQ baseline** | `[sun_main]` | 1420 MPa | ±5 % | Sets σ_0 + σ_ss(DQ) + σ_HP(d=1.18) + σ_ρ(2.08e15) sum; biggest constraint on Fleischer β_C |
| **DQ + T516/10** | `[sun_main]` | 1762 MPa | ±5 % | Sets M2C Orowan calibration (with population from Wang 2024 + Mondière) |
| **AF550/45 + T425/10** | `[sun_main]` | 1726 MPa | ±5 % | Sets transferred Cho-kinetics calibration; the model's most-novel claim |

If any of these miss by >5 %, we revisit the constants table or the kinetics-transfer assumption.

### Validation cross-checks — should match within stated tolerance

| Check | Source | Predicted | Tol |
|-------|--------|-----------|-----|
| AF550/45 (no temper) | `[sun_main]`: YS 1830 | 1830 | ±10 % (no precipitation, just dislocations + block) |
| Wang 520 °C / 8 h | `[zhu41_Wang_2024]`: YS 1747 | 1747 | ±10 % (transfer from 516/10) |
| Mondière 516 °C / 10 h UTS | `[zhu07_Mondiere_2018]`: 1965 MPa | UTS prediction (= 1.15× YS rule of thumb) | ±10 % |
| Mondière K_IC | `[zhu07_Mondiere_2018]`: 110 MPa·m^½ | TRIP-augmented K_IC | ±20 % (toughness has more variance) |

### What we don't try to reproduce (out of scope v1)

- High-strain-rate Hopkinson-bar response (Sun ref [2] X.Y. Li 2022 has Johnson-Cook for M54)
- Fatigue, creep, oxidation
- Hydrogen embrittlement
- Mill-anneal hardness (parking until needed)

## 7. User interaction model

How does the user (you) actually use this thing? Three modes:

### 7.1 Notebook mode — primary for exploration

Jupyter notebooks for: parameter sweeps, sensitivity analysis, fitting a custom-temper recipe, reproducing a published figure. Each notebook in `notebooks/` is self-contained and importable.

**When to use**: experimenting with the model, comparing strategies, developing a new submodel.

### 7.2 Script mode — for batch / CI / reproducibility

`scripts/` contains pinned-input scripts that produce the canonical published-result reproductions. These run in CI to catch regressions when constants change.

**When to use**: "reproduce Sun 2022 Fig. X", "regenerate calibration table", "run after a model change".

### 7.3 Streamlit mini-UI — for interactive parameter sweep

Phase 3 deliverable. Single-page UI with:
- Sliders for processing path (austenitize T/t, ausforming T/reduction, temper T/t)
- Live update of σ_y, contributions stacked bar, distance from anchor
- Export of result as JSON + plot

**When to use**: showing the model to a collaborator, quick what-if exploration without a notebook.

### 7.4 Claude-assisted workflow

The user will work with Claude for: extending the model, adding new states/submodels, integrating new literature, debugging mismatches. The pattern is **scoped tasks on topic branches** as we've established.

## 8. Literature-refresh agent / skill design

The reference library is now extensive (73 papers). Re-indexing every paper for every question wastes context. Proposed workflow:

### 8.1 Triggered lit lookup

When implementing a model component, **spawn a focused research agent** to extract specific data from a specific paper, rather than reading the whole paper into context. Pattern:

```
"In [zhu07_Mondiere_2018], find the M2C composition reported by APT vs the Thermo-Calc-predicted composition. Report only those two numbers and their context."
```

This was used in this planning round (4 parallel agents on Mondière, B. Wang, Cho, Galindo-Nava) and worked well — keeps main-thread context lean while enabling deep dives.

### 8.2 Lit refresh signals

When to re-check the literature for a given topic:
- **New paper added to `references/references.bib`** → spawn an indexing agent for it on a `research/index-<paper>` branch.
- **Model prediction misses anchor by >10 %** → spawn an agent on the closest 2-3 papers to look for missed assumptions or data.
- **User asks a "why does this happen?" question** → spawn an agent on the relevant lit cluster (e.g., for cementite questions: `[zhu39_Ghosh_Olson_1999]`, `[sun_main]`, `[zhu41_Wang_2024_M54]`).
- **Quarterly cadence**: a "lit-watch" cron that searches Crossref + Google Scholar for new M54 / Co-Ni secondary-hardening papers and flags them in `references/lit-watch.md`.

### 8.3 Possible Claude skill: `lit-lookup`

A formal skill we could create: takes a citekey + question, spawns a sub-agent on that PDF, returns a focused answer. Reduces friction. Worth implementing if we find ourselves doing manual lookups frequently. Defer until we hit ~10 manual lookups.

### 8.4 Indexing as we go

Pattern established: when a paper proves load-bearing for a model decision, write an `index/<paper>-index.md` so future sessions don't have to re-derive. We've done this for Zhu 2025 main, Sun 2022, the 5 cited-by, Patel-Cohen, Olson-Cohen. As we go through model implementation, expect to add indexes for Wang 2024, Mondière 2018, Cho 2015, Galindo-Nava 2015, Krauss 1999, and probably Ghosh-Olson 1999.

## 9. Phased implementation roadmap

### Phase 0 — finish lit foundation (this week)

- [x] Index Patel-Cohen + Olson-Cohen (done)
- [x] Get all 73 PDFs locally (done — pull1 + pull2 + Wen + Wang)
- [x] Verify all DOIs (done — Crossref check)
- [ ] Index Wang 2024 + Mondière 2018 + Cho 2015 + Galindo-Nava 2015 (research agents already extracted; convert to permanent `index/<paper>-index.md` files)

### Phase 1 — strengthening core (Weeks 1–2)

- [x] Scaffold the Python package (uv project, ruff, mypy, pytest)
- [x] Implement: `alloys`, `states`, `constants`, `strengthening/{friction, solid_solution, hall_petch, dislocation, orowan}`
- [x] Calibration anchors as state factories in `calibration/anchors.py`
- [x] Calibration script + sweep utilities (`scripts/calibrate.py`, `calibration/sweep.py`)
- [x] Calibrate against Sun 2022 DQ + T516/10 (anchor 2): **PASS at -4.9 %** ✓
- [ ] ~~Calibrate against Sun 2022 DQ (anchor 1)~~ — deferred to Phase 2: under-predicts by ~38 %, see "Phase 1.5 finding" below
- [x] **Gate (relaxed)**: DQ+T anchor passes; DQ (untempered) deferred until intrinsic-martensite term added.

### Phase 1.5 finding — DQ vs DQ+T behavior

After fixing a double-counted Taylor factor in `sigma_dislocation` (was including
`α × M` when Sun's published formula has M absorbed into α), the picture clarifies:

- **DQ + T516/10** anchor passes cleanly at **-4.9 %** under linear sum + Sun convention. The framework correctly composes σ_friction + σ_ss(post-precipitation matrix) + σ_HP(block) + σ_ρ(post-temper density) + σ_M2C(Wang 520/8 anchor). This is the Phase 1 success.
- **DQ (untempered)** anchor under-predicts by **~38 %** even with extreme β_C. The simple Hall-Petch (block) + Bailey-Hirsch + Fleischer decomposition is missing what Krauss 1999 and Galindo-Nava 2015 call the **as-quenched intrinsic martensite strength** — sources include lath-boundary strengthening (block size badly under-counts boundary area in untempered laths), tetragonality of C-supersaturated martensite, and quench-induced internal stresses. After tempering this contribution disappears (C drops from 0.30 wt% to ~0.003 wt%, laths coarsen).
- **AF550/45 (untempered)** anchor under-predicts by ~28 % for the same reason.

**Phase 2 must address this** before AF + T calibration is meaningful. Three approaches under consideration:
1. Add an explicit `sigma_intrinsic_martensite` term that's only present in untempered states, calibrated to lath-spacing × C-supersaturation per Krauss 1999.
2. Use lath-spacing-based Hall-Petch for untempered states (lath ~135 nm vs block 1180 nm); switch back to block-based for tempered.
3. Adopt the full Galindo-Nava 2015 model which combines block + lath effects in a hierarchical Hall-Petch.

Option 3 is the most principled but the most work. Option 1 is the fastest. Defer the choice to Phase 2 kickoff.

### Phase 2 — ausforming + tempering (Weeks 3–4)

- [ ] **Add intrinsic-martensite term per Phase 1.5 finding** (gates the AF anchors)
- [ ] Implement `kinetics/{jma, transferred}` with Cho 2015 → M54 transfer
- [ ] Implement `precipitates/{m2c, mc}` with full kinetics integration
- [ ] Add `ausform()` to processing path
- [ ] Calibrate against Sun 2022 DQ (revisit with intrinsic term)
- [ ] Calibrate against Sun 2022 AF550/45 (untempered)
- [ ] Calibrate against Sun 2022 AF550/45 + T425/10 (anchor 3)
- [ ] **Gate**: all 3 calibration anchors + DQ + AF anchors within ±5 %

### Phase 3 — TRIP toughening (Weeks 5–6)

- [ ] Implement `toughening/{patel_cohen, olson_cohen, crack_tip}`
- [ ] Add `f_A` reverted-austenite term to strengthening rule-of-mixtures
- [ ] Validate K_IC against Mondière 110 MPa·m^(1/2) anchor

### Phase 4 — interactive layer (Weeks 7–8)

- [ ] Streamlit UI for processing-path sliders + live contributions bar
- [ ] Notebook tutorials (01–06)
- [ ] User-facing README in `m54model/`

### Phase 5 — extensions (open-ended)

- [ ] Mill-anneal state (if/when needed)
- [ ] Thermo-Calc TCFE integration (replace hard-coded equilibrium tables)
- [ ] Full toughness model (not just K_IC; include J-integral)
- [ ] Fit-to-experiment utility (user provides their own (T, t, YS, ρ, …) → suggested constants)

## 10. Open questions for the user (please answer before Phase 1)

1. **Strengthening sum convention**: Default to **Sun 2022 linear top-level + Pythagorean within precipitation**. Fine? Or want Wang 2024's full Pythagorean as default?

2. **Fleischer β coefficients for W and V**: Compute from Galindo-Nava Eq. (Appendix A) using atomic-radius-and-shear-modulus mismatch, or do you have empirical M54-relevant numbers from other lit?

3. **Block size as Hall-Petch d**: Default. Or override with **lath spacing** (some authors do; the answer changes σ_HP by 5–10×)?

4. **Reverted austenite in DQ + T516/10 and AF + T425/10**: Do you have measured volume fractions for either condition? If not, ballpark from Zhang 2022 (cryo paper) and Wang 2024 (XRD-detected but unquantified)?

5. **Streamlit UI worthwhile in Phase 4?** Or is a well-organized notebook collection enough for your workflow?

6. **Codebase home**: this repo, or split the model into a separate Python package repo and depend on this one for refs? Recommend keeping in this repo for now (`m54model/` subdirectory), can spin out later if it grows.

7. **CI / tests**: do you want GitHub Actions running on push? (Implies setting up a remote — we currently have local-only git.)

8. **Thermo-Calc**: do you have Thermo-Calc + TCFE access? If yes, the model can call it for equilibrium phase calcs (instead of hard-coding Mondière/Wang values). If no, we proceed with hard-coded tables.

## 11. Risks / known unknowns

- **Cho 2015 → M54 kinetics transfer is the biggest assumption**. Cho's Cr-rich M2C in 13Co alloy may not behave like M54's Mo-W-rich M2C in 7Co alloy. If anchor 3 (AF + T) misses, this is suspect #1.
- **MC-Orowan contribution is unquantified everywhere**. Wang 2024 explicitly under-predicts σ_y by 30–90 MPa attributed to missing MC. Our model needs to either compute MC properly or accept a ~5 % miss.
- **Reverted austenite quantification gap** for M54. Both Wang 2024 and Sun 2022 acknowledge it but don't quantify. If TRIP toughening submodel is to work, we need real f_A and chemistry data — possibly user's own future measurement.
- **Carbon-in-solution contribution at DQ** is large and Fleischer coefficient β_C is poorly constrained. Calibration will likely require fitting β_C against the DQ anchor.
- **Sun 2022 vs Wang 2024 constant divergence**: α = 0.38 vs 0.25, K_HP = 230 vs 300 MPa·µm^½. The model exposes both but defaults to user's own paper. Worth a sensitivity analysis.

---

## Quick-reference: what's locked in vs proposed

| Locked in | Proposed (need user OK) |
|-----------|-------------------------|
| The 4 microstructural states | Module layout (Section 4.2) |
| The strengthening equation form (Section 2) | API sketch (Section 4.4) |
| Calibration anchors (Section 6) | Streamlit UI in Phase 4 |
| Universal constants (Section 3.5) — defaults | Lit-lookup as a formal Claude skill (Section 8.3) |
| Knowledge inventory by state (Section 3) | Phased timeline (Section 9) |
| TRIP submodel architecture (Section 5) | Open questions in Section 10 |

When you're ready, hit me with answers (or partial answers) to Section 10 and I'll start scaffolding Phase 1. If anything in this plan looks wrong or backwards, the time to push back is now.
