# TRIP Foundations — Patel-Cohen 1953 & Olson-Cohen 1975

> The two seminal papers underlying the toughening submodel for our M54 work. Together they give the full stress-assisted-plus-strain-induced martensitic transformation framework. Olson-Cohen ties directly to QuesTek lineage — G.B. Olson founded QuesTek (the alloy designer for Ferrium M54).

---

## Why these two papers, and how they fit together

The toughening contribution from the **film-like reversed austenite** at lath boundaries (which Zhu 2025 measures at 15.8 nm at 32 h temper, growing to 36.4 nm at 100 h) operates through stress-induced or strain-induced γ → α′ martensitic transformation at the crack tip. There are two regimes:

| Regime | When it dominates | Governing paper | Math |
|--------|-------------------|-----------------|------|
| **Stress-assisted** | Crack-tip stress is high but plastic strain in austenite is small. Nucleation occurs on the SAME sites as spontaneous (cooling) transformation, but applied stress shifts the M_s | **Patel-Cohen 1953** | Mechanical work `U = τγ₀ + σε₀` adds to chemical free energy → M_s^σ |
| **Strain-induced** | Plastic deformation in austenite creates NEW nucleation sites (shear-band intersections). Operates above M_s^σ but below M_d | **Olson-Cohen 1975** | Sigmoidal `f_α′ = 1 − exp{−β[1 − exp(−αε)]^n}` |

For Ferrium M54 with film-like reversed austenite, both are likely active in different parts of the crack-tip field. The complete toughening submodel will need to combine them, with a transition criterion at the σ_y of the austenite (the boundary between "stress shifts M_s but doesn't yield γ" and "γ yields and creates new nucleation sites").

---

## Patel & Cohen 1953 — "Criterion for the Action of Applied Stress in the Martensitic Transformation"

### Bibliographic header
- **Authors:** J.R. Patel, M. Cohen — Department of Metallurgy, MIT
- **Journal:** Acta Metallurgica, Vol. 1, Sept. 1953, pp. 531-538
- **DOI:** [10.1016/0001-6160(53)90083-2](https://doi.org/10.1016/0001-6160(53)90083-2)
- **Funding:** US Office of Naval Research
- **Pages:** 8

### Core thesis (one paragraph)
Earlier work (Scheil 1932) had assumed only shear stress matters for martensitic transformation. Kulin et al. 1952 disproved this by showing that elastic bending of an austenitic bar produces martensite **only on the tensile side** (not on the compressive side, even though shear is the same). Patel and Cohen formalize this: the applied-stress contribution to the transformation thermodynamic driving force has a **shear** term AND a **normal** term, weighted by the corresponding components of the transformation strain.

### Key equations

**Eq. (1) — Patel-Cohen mechanical driving force (THE central equation):**

$$ U = \tau\,\gamma_0 + \sigma\,\varepsilon_0 $$

where:
- U = mechanical work per unit transformed volume (positive aids transformation; positive σ_normal is tensile)
- τ = shear stress resolved on the habit plane (always positive — habit-plane permutations)
- γ₀ = transformation shear strain (Fe-30Ni measured by Machlin 1951: **γ₀ = 0.20**)
- σ = normal stress resolved perpendicular to the habit plane (signed: + tension, − compression)
- ε₀ = transformation dilatational (volume) strain normal to habit (Fe-30Ni: **ε₀ = 0.04**, corresponding to ~+4 % volume expansion)

**Eq. (2)–(3) — Mohr's circle resolution for uniaxial loading:**
$$ \tau = \tfrac{1}{2}\,\sigma_1\,\sin 2\theta \quad ; \quad \sigma = \pm\tfrac{1}{2}\,\sigma_1(1 + \cos 2\theta) $$
- σ₁ = magnitude of the applied uniaxial stress
- θ = angle between specimen axis and habit-plane normal

**Eq. (4) — U as a function of θ:**
$$ U = \tfrac{1}{2}\gamma_0\sigma_1\sin 2\theta \pm \tfrac{1}{2}\varepsilon_0\sigma_1(1+\cos 2\theta) $$

**Eq. (6) — Optimal habit-plane orientation that maximizes U:**
$$ \tan 2\theta = \pm\,\gamma_0/\varepsilon_0 $$
- For Fe-30Ni: γ₀/ε₀ = 0.20/0.04 = 5 → 2θ ≈ 79°

**Eq. (7) — The criterion (modified M_s):**
$$ \big(F^M - F^A\big)\big|_{M_s^\sigma} = \big(F^M - F^A\big)\big|_{M_s} + U_{max} $$
- M_s^σ = the stress-shifted martensite-start temperature
- "(F^M − F^A) at M_s" is the constant chemical driving force criterion (~−200 cal/mol Fe-Ni; ~−370 cal/mol Fe-Ni-C)
- U_max gets added algebraically: positive (tension/shear) raises M_s; negative (hydrostatic compression) lowers it

**Eq. (12) — Hydrostatic-pressure special case** (no shear; only the dilatational coupling):
$$ U = -\varepsilon_0\,\sigma_1 \quad\text{(opposes transformation)} $$

### Quantitative validation (Table I of paper)

| Stress system | Material | dM_s/dσ calc | dM_s/dσ exp |
|---------------|----------|-------------:|------------:|
| Uniaxial tension     | 0.5 C – 20 Ni Fe | **+1.07 °C/ksi** | +1.0 °C/ksi |
| Uniaxial compression | 0.5 C – 20 Ni Fe | +0.72 °C/ksi    | +0.65 °C/ksi |
| Hydrostatic pressure | 70 Fe – 30 Ni    | −0.38 °C/ksi    | −0.57 °C/ksi |

Tension > compression because in tension both shear AND normal terms aid the transformation; in compression the shear aids but the (negative) normal term opposes. Hydrostatic pressure has only the dilatational coupling (no shear) and that coupling is negative (compression of volume-expanding transformation).

### Required thermodynamic input data (Appendix I)

For Fe-Ni binaries (Jones & Pumphrey 1949 thermodynamics):
$$ F^M - F^A = N_{Ni}\,\Delta H_{Ni} + 1.25\,N_{Fe}\,\Delta F_{Fe} $$
- ΔH_Ni = 2500 cal/mol (heat of solution difference, ferrite vs austenite)
- ΔF_Fe = γ→α free energy of pure iron (Zener 1946 from Austin 1932 specific-heat data)
- 1.25 = empirical correction factor for Fe-Ni equilibrium

For Fe-Ni-C (Fisher 1949 method):
$$ F^M - F^A = N_{Ni}\Delta H_{Ni} + 1.25 N_{Fe}\Delta F_{Fe} + N_C(10500 − 3425\,T) + \Delta F_* $$
- ΔF_* = free energy due to C atom ordering in tetragonal martensite

**Slopes used:** d(F^M − F^A)/dT ≈ 1.33 cal/(mol·K) for the 0.5C-20Ni-bal-Fe alloy; 1.23 cal/(mol·K) for the 70Fe-30Ni alloy.

### What this gives our M54 model

- **A direct coefficient for "how much does crack-tip stress shift the local M_s of the reversed-austenite films."** For a Fe-Co-Ni-Mo-Cr reversed austenite at the lath boundary in M54, we'll need to plug in measured γ₀, ε₀ (M54 transformation strains) and an Fe-Co-Ni-Mo-Cr-C thermodynamic database to compute U_max. Sun 2022 has the bulk M_s ≈ M_f from prior work (M54 has Ms ≈ 90-150 °C per QuesTek datasheet, so reversed austenite stable down to RT but metastable under stress).
- **The orientation-optimization (Eq. 6)** is something our model can implement directly: find the habit-plane orientation in the lath film that maximizes U for the local stress state at the crack tip.
- **The stress-vs-pressure asymmetry** (Eq. 12) means our model should explicitly carry both deviatoric and hydrostatic stress components — they couple to different transformation strains.

### References worth following up

- [9] **Jones & Pumphrey 1949** — J. Iron Steel Inst. 163 — the Fe-Ni thermodynamics underlying Eq. (A1). May be on JISI archive.
- [7] **Zener 1946** — Trans. AIME 167, 513 — pure iron γ-α free energy.
- [8] **Cohen, Machlin, Paranjpe** — Thermodynamics in Physical Metallurgy (ASM 1950), p. 242 — Fe-C constant driving force at M_s.
- [11] **Fisher, Hollomon, Turnbull 1949** — Trans. AIME 185, 691 — nucleation theory background.

---

## Olson & Cohen 1975 — "Kinetics of Strain-Induced Martensitic Nucleation"

### Bibliographic header
- **Authors:** **G.B. Olson** (AMAX Foundation Fellow, MIT) and M. Cohen (Ford Professor, MIT)
- **Journal:** Metallurgical Transactions A, Vol. 6A, April 1975, pp. 791-795
- **DOI:** [10.1007/BF02672301](https://doi.org/10.1007/BF02672301)
- **Funding:** NSF GH-40452X + ONR N00014-67-A-0204-0027
- **Pages:** 5
- **Lineage note:** **G.B. Olson** went on to found **QuesTek Innovations LLC** — the same company that designed Ferrium M54 (per the Jou US 9,051,635 patent we have in `pdf-archive/`). This 1975 paper is the foundational TRIP-kinetics equation in QuesTek's design lineage.

### Core thesis (one paragraph)
Patel-Cohen handles stress-assisted nucleation (same sites as spontaneous, just shifted M_s). But above M_s^σ, plastic deformation in the austenite **creates new nucleation sites** — specifically, the intersections of shear bands (ε′-hcp martensite plates, mechanical twins, or stacking-fault bundles). Olson-Cohen build a probabilistic model of (i) shear-band formation kinetics, (ii) intersection geometry, and (iii) probability that an intersection produces an α′ embryo, integrated to give the full f_α′(ε) curve. Output: a **sigmoidal volume fraction with saturation < 1**, controlled by two temperature-dependent parameters.

### Key equations

**Eq. (1)–(2) — Shear-band formation rate:**
$$ \frac{df_{sb}}{1 - f_{sb}} = \alpha\,d\varepsilon \quad\Rightarrow\quad f_{sb} = 1 - \exp(-\alpha\,\varepsilon) $$
- f_sb = volume fraction of shear bands in austenite
- α = strain-independent rate parameter; depends on **stacking-fault energy** (lower SFE → higher α) and **strain rate** (higher ε̇ → higher α)

**Eq. (3) — Number density:** N_v^sb = f_sb / v_sb  (v_sb = avg volume per shear band)

**Eq. (4) — Intersection density:**
$$ N_v^I = K\,(N_v^{sb})^n $$
- K = geometric constant (random-orientation thin plates → K = π²d³/16 with n = 2; non-random → use higher n empirically)

**Eq. (5)–(6) — Embryo formation and growth:**
$$ dN_v^{\alpha'} = p\,dN_v^I \quad ; \quad \frac{df^{\alpha'}}{1 - f^{\alpha'}} = \bar{v}^{\alpha'}\,dN_v^{\alpha'} $$
- p = probability that an intersection generates an α′ embryo (Gaussian distribution of intersection potencies vs chemical driving force, equivalently vs T)

**Eq. (7) — THE MASTER EQUATION (Olson-Cohen sigmoidal model):**

$$ \boxed{f^{\alpha'} = 1 - \exp\!\Big\{-\beta\big[1 - \exp(-\alpha\,\varepsilon)\big]^n\Big\}} $$

where:
- f^α′ = volume fraction of strain-induced α′ martensite
- ε = plastic strain in the austenite
- α = shear-band-formation rate (strongly temperature-dependent through SFE)
- β = (v_α′ K / (v_sb)^n)·p — proportional to embryo-formation probability; saturates at low T (p → 1)
- n = empirical exponent; **n = 4.5 fits Angel's 304 SS data**

### Fitted parameters from Angel's 1954 304 SS data

| T (°C) | α (rate of shear-band formation) | β (saturation level driver) |
|--------|---------------------------------:|----------------------------:|
| −188   | 12.9 | ~2.0 |
| −70    | ~7   | ~2.0 |
| −30    | ~5   | ~1.7 |
| 0      | ~4   | ~1.0 |
| 22     | 3.55 | ~0.3 |
| 50     | ~2   | ~0   |

- α monotonically decreases with T (because SFE rises with T → less shear-banding)
- β has a **Gaussian-shaped** drop centered at +12 °C, with σ ≈ 34 °C ≈ 142 J/mol (assuming ΔS^(γ→α′) ≈ 1 cal/mol·K = 4.2 J/mol·K)

### How to interpret the parameters physically

- **α** captures the **shear-banding propensity** of the austenite. Reduce SFE → more shear bands per strain increment → faster transformation.
- **β** captures the **potency of intersections** for embryo nucleation. Set by the chemical driving force ΔG^(γ→α′) at temperature T. At low T, ΔG is large enough that almost every intersection works (p → 1, β saturates). At high T (above ~M_d), ΔG is too small and β → 0 (no transformation).

### Strategic takeaway from the paper (relevant for QuesTek alloy design)

The temperature sensitivity of TRIP — too narrow a useful T window because of adiabatic heating — can be flattened by:
1. **Reducing ΔS^(γ→α′)** through alloying — broadens the β-vs-T transition
2. **Reducing ΔS^(γ→ε′)** through alloying — flattens the α-vs-T curve

Olson notes that **substituting Cr and Mn for Ni accomplishes both** — and indicates such modifications are "currently being investigated" (1975). This thinking line eventually flowed into QuesTek's TRIP and PH steel design philosophy.

### What this gives our M54 model

- **The toughening submodel can use Eq. 7 directly** to compute strain-induced f_α′ in the reversed austenite films at the M54 crack tip, given the local plastic strain ε in the austenite and α(T), β(T) for our composition.
- **For M54 we need two parameters fitted to in-situ TEM or XRD measurements of f_α′ vs strain** (which Sun 2022 does NOT report — gap to fill, possibly via a separate experiment or by transferring α/β from a 13Co-8Ni TRIP study like Cho 2015 in Sun's ref [11]).
- **The volume change from γ → α′ (~4 % expansion)** at the crack tip → compressive residual stress in the surrounding plastic zone → **crack-tip shielding**. Magnitude scales with f_α′ × ΔV_transformation. This is the toughening mechanism Zhu 2025 invokes qualitatively.
- **Distinguishing stress-assisted vs strain-induced** (the paper's opening) tells us where Patel-Cohen ends and Olson-Cohen begins. Below σ_y of the austenite, only Patel-Cohen applies; above, both are active and Olson-Cohen typically dominates.

### References worth following up

- [3] **Angel 1954** — J. Iron Steel Inst. 177, 165 — the 304 SS dataset Olson-Cohen fit. Pre-DOI.
- [6] **Lecroisey & Pineau 1972** — Met. Trans. 3, 387 — SFE temperature dependence in Fe-Ni-Cr.
- [11] **Olson & Cohen 1972** — J. Less-Common Metals 28, 107 — earlier paper on shear-band intersection mechanism details.
- [4] **Gerberich et al. 1970** — Asilomar conf. proceedings — earlier parabolic TRIP model.

---

## Combined model for M54 toughening submodel

Putting it together, the toughening contribution from reversed-austenite TRIP at the M54 crack tip is:

1. **Compute local stress field** at crack tip (HRR or comparable elastic-plastic field)
2. **For each material point in the austenite films:**
   - Compute U via Patel-Cohen Eq. (1) with M54 transformation strains (γ₀, ε₀) and the local stress tensor
   - If U + ΔG_chem(T) ≥ ΔG_crit → **stress-assisted transformation** triggered, austenite → α′
   - Else if local plastic strain ε > 0 in austenite → **strain-induced transformation** via Olson-Cohen Eq. (7) with α(T), β(T) for M54
3. **Sum the volume fraction of newly transformed α′** in the plastic zone
4. **Compute volume-expansion-induced stress shielding** at the crack tip → toughness increment ΔK_IC

Required data (model inputs):
- M54 transformation strains γ₀, ε₀ (probably similar to other Fe-Ni alloys: γ₀ ≈ 0.20, ε₀ ≈ 0.04, but should verify for our composition)
- ΔG_chem(T) for γ → α′ in the M54 reversed-austenite chemistry (Thermo-Calc TCFE database)
- α(T), β(T) for strain-induced kinetics (calibrate from 13Co-8Ni TRIP literature or M54-specific experiment)
- f_RA(T_temper, t_temper) — volume fraction of reversed austenite as f(temper history) — from Sun 2022 or Mondière

These are tractable inputs, and define a clean three-tier model: yield (linear sum) + precipitation strengthening (Pythagorean) + TRIP toughening (Patel-Cohen + Olson-Cohen). Each tier has independent literature support.
