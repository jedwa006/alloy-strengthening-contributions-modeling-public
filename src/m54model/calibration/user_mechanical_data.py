"""User's measured tensile, nanoindentation, and toughness data — Phase 3.6d.

Two parallel datasets per CR condition:

1. **Bulk tensile** (Table 3 of user's draft + 0/47/53/60 % SPR slide). YS,
   UTS, total elongation; tested at ε̇ ≈ 1e-1 s⁻¹ — apply
   `m54model.calibration.strain_rate.strain_rate_correction` before
   comparing to the model's quasi-static predictions.
2. **Nanoindentation depth profiles** (Fig 2 of user's draft). H and reduced
   modulus E_r at five through-thickness zones (0-50, 50-100, 100-250,
   250-500 µm, Core). Mean ± 1σ within each zone.
3. **Toughness** (slide). K_IC (or equivalent — units shown as "MPa/m²"
   on user's slide are believed to be a typo for MPa·m^½, since the M54
   numbers around 200-450 are consistent with K_IC SENB/CT and inconsistent
   with energy-per-area units).

Units throughout: σ in MPa (NOT GPa, despite the slides showing GPa);
hardness H in GPa; reduced modulus Er in GPa; toughness K_IC in MPa·m^½;
elongation in %; CR % is engineering thickness reduction.

Source workbooks (private):
- `data/nanoindentation/experimental/AllSamples M54_HvsErvsThicknessToCrossSection.xlsx`
- `data/tensile/experimental/`  (CSVs to land here when user shares them)

NOTE on the 47/53 % CR samples: Per the SPR slide, these are intermediate
cumulative-reduction conditions BETWEEN the 40 % and 60 % cw/cr ASTAR
points. They were tensile-tested but do NOT have ASTAR maps — so they
extend the strain–strength curve without a matching f_A measurement.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TensilePoint:
    """One tensile-test condition (mean of N replicates ± 1σ)."""

    cw_pct: float
    """Cumulative cold-rolling reduction (%)."""

    label: str

    sigma_y_MPa: float
    sigma_y_std_MPa: float
    UTS_MPa: float
    UTS_std_MPa: float
    elongation_pct: float
    elongation_std_pct: float

    n_replicates: int = 0  # 0 = not reported

    notes: str = ""

    @property
    def work_hardening_ratio(self) -> float:
        """UTS / σ_y — proxy for residual hardening capacity."""
        return self.UTS_MPa / self.sigma_y_MPa


# Table 3 (user's draft) + tensile slide. All at ε̇ ≈ 1e-1 s⁻¹.
USER_M54_TENSILE: list[TensilePoint] = [
    TensilePoint(
        cw_pct=0.0,
        label="AF + T516/10 (0% CR baseline)",
        sigma_y_MPa=1300.0,
        sigma_y_std_MPa=30.0,
        UTS_MPa=2100.0,
        UTS_std_MPa=10.0,
        elongation_pct=11.0,
        elongation_std_pct=1.0,
        notes="Cross-rolled-into-AF + 516/10 temper baseline (the user's cw/cr starting state).",
    ),
    TensilePoint(
        cw_pct=47.0,
        label="AF + T516/10 + 47% CR",
        sigma_y_MPa=1800.0,
        sigma_y_std_MPa=30.0,
        UTS_MPa=2600.0,
        UTS_std_MPa=30.0,
        elongation_pct=15.0,
        elongation_std_pct=0.0,
        notes="Intermediate CR; no matching ASTAR map. Strain-rate sensitivity unknown.",
    ),
    TensilePoint(
        cw_pct=53.0,
        label="AF + T516/10 + 53% CR",
        sigma_y_MPa=1700.0,
        sigma_y_std_MPa=80.0,
        UTS_MPa=2500.0,
        UTS_std_MPa=20.0,
        elongation_pct=13.0,
        elongation_std_pct=1.0,
    ),
    TensilePoint(
        cw_pct=60.0,
        label="AF + T516/10 + 60% CR",
        sigma_y_MPa=1900.0,
        sigma_y_std_MPa=50.0,
        UTS_MPa=2700.0,
        UTS_std_MPa=20.0,
        elongation_pct=20.0,
        elongation_std_pct=3.0,
        notes="Highest σ_y AND highest ductility — opposite of typical CW behavior.",
    ),
]


# 20 % and 40 % CR tensile not yet reported (user has cw/cr ASTAR for these
# but tensile bars haven't been broken). When they land, append to the list.


@dataclass(frozen=True)
class ToughnessPoint:
    """One tensile-toughness measurement.

    **Definition (per user, 2026-05-12)**: area under the engineering
    stress-strain curve from instrumented tensile to fracture. Units
    are MJ/m³ (energy density). NOT to be confused with K<sub>IC</sub>
    fracture toughness (MPa·m^½), which is a separate plane-strain
    quantity — see Mondière 2018's K<sub>IC</sub> = 110 MPa·m^½ literature
    anchor in the toughening module.

    The user's slide originally labeled units as "MPa/m²" — that label
    was a notation typo. Numerically MJ/m³ ≡ MPa (energy/vol = stress
    × strain), so the values are correct, only the unit string was wrong.

    The Chapter 5 draft §"Toughness" text reports DIFFERENT values
    (242-270 / 127-136 / 101-180 MJ/m³ for 0/47/60 % CR) with a
    DECREASING trend — claims it tracks "uniform elongation collapse",
    but Table 3 in the same paper shows TOTAL elongation 11→15→13→20 %
    rising, so the §Text values appear to be measuring area-to-uniform
    rather than area-to-fracture. The values stored here are the
    instrumented-tensile-to-fracture metric (matching slide + Fig 3b).
    """

    cw_pct: float
    label: str
    tensile_toughness_MJ_per_m3: float
    tensile_toughness_std_MJ_per_m3: float
    method: str = "instrumented tensile, area to fracture"
    notes: str = ""


# Toughness chart (user's "Mechanical Properties" slide; Chapter 5 Fig 3b
# shows the same trend in the green-bar overlay).
USER_M54_TOUGHNESS: list[ToughnessPoint] = [
    ToughnessPoint(
        0.0,
        "AF + T516/10 baseline",
        219.0,
        13.0,
        notes=(
            "Tensile toughness — NOT K_IC. Mondière 2018's K_IC = 110 MPa·m^½ "
            "is a separate fracture-toughness anchor, kept in the toughening module."
        ),
    ),
    ToughnessPoint(47.0, "AF + T516/10 + 47% CR", 322.0, 9.0),
    ToughnessPoint(53.0, "AF + T516/10 + 53% CR", 280.0, 12.0),
    ToughnessPoint(
        60.0,
        "AF + T516/10 + 60% CR",
        434.0,
        23.0,
        notes=(
            "Tensile toughness DOUBLES from 0 % to 60 % CR — the unusual "
            "triple-positive (σ_y↑ + UTS↑ + EL↑(total) + tensile-toughness↑) "
            "with cold work in the AF+T M54 system."
        ),
    ),
]


@dataclass(frozen=True)
class NanoindentationZone:
    """Mean H + Er within one through-thickness zone for one CR condition."""

    cw_pct: float
    zone_label: str  # '0-50 µm', '50-100 µm', '100-250 µm', '250-500 µm', 'Core'
    zone_depth_um_low: float
    zone_depth_um_high: float | None  # None for 'Core' (mid-thickness)
    H_GPa: float
    H_std_GPa: float
    Er_GPa: float
    Er_std_GPa: float

    @property
    def sigma_y_tabor_MPa(self) -> float:
        """Tabor-relation estimate: σ_y ≈ H / 3 (MPa).
        Quick orientation only — for true σ_y use the tensile data; the
        Tabor coefficient is alloy- and microstructure-dependent (2.8 to
        3.5 typical for tempered martensite). Here we report H/3 as a
        first-order proxy."""
        return self.H_GPa * 1000.0 / 3.0


# Visible values from Fig 2 (user's draft) — eyeballed to ~0.05 GPa precision.
# Refine from the source workbook (`data/nanoindentation/experimental/`) when
# we wire up the loader; until then these are good enough for cross-checks.
USER_M54_NANOINDENTATION: list[NanoindentationZone] = [
    # 0 % CR — baseline
    NanoindentationZone(0,  "0-50 µm",     0.0,  50.0, 6.71, 0.21, 248.5, 7.0),
    NanoindentationZone(0,  "50-100 µm",  50.0, 100.0, 6.65, 0.23, 247.5, 5.5),
    NanoindentationZone(0,  "100-250 µm", 100.0, 250.0, 6.84, 0.34, 254.0, 17.0),
    NanoindentationZone(0,  "250-500 µm", 250.0, 500.0, 6.95, 0.37, 258.0, 19.5),
    NanoindentationZone(0,  "Core",       500.0, None, 6.86, 0.15, 247.5, 9.0),
    # 20 % CR — flat-ish, 1 GPa above baseline
    NanoindentationZone(20, "0-50 µm",     0.0,  50.0, 8.00, 0.20, 224.0, 5.0),
    NanoindentationZone(20, "50-100 µm",  50.0, 100.0, 7.73, 0.25, 224.0, 5.0),
    NanoindentationZone(20, "100-250 µm", 100.0, 250.0, 7.86, 0.30, 225.0, 5.5),
    NanoindentationZone(20, "250-500 µm", 250.0, 500.0, 7.74, 0.30, 223.0, 4.5),
    NanoindentationZone(20, "Core",       500.0, None, 7.78, 0.30, 222.5, 5.0),
    # 40 % CR — peak hardness; lowest E_r (austenite-spike linkage)
    NanoindentationZone(40, "0-50 µm",     0.0,  50.0, 7.78, 0.24, 204.0, 4.5),
    NanoindentationZone(40, "50-100 µm",  50.0, 100.0, 7.93, 0.30, 207.0, 3.5),
    NanoindentationZone(40, "100-250 µm", 100.0, 250.0, 8.02, 0.30, 208.0, 4.0),
    NanoindentationZone(40, "250-500 µm", 250.0, 500.0, 7.90, 0.30, 207.0, 3.5),
    NanoindentationZone(40, "Core",       500.0, None, 7.78, 0.30, 209.5, 3.5),
    # 60 % CR — surface-localized hardness; E_r rebounds high
    NanoindentationZone(60, "0-50 µm",     0.0,  50.0, 8.06, 0.20, 265.5, 5.0),
    NanoindentationZone(60, "50-100 µm",  50.0, 100.0, 7.87, 0.20, 263.0, 4.5),
    NanoindentationZone(60, "100-250 µm", 100.0, 250.0, 7.85, 0.25, 261.0, 5.5),
    NanoindentationZone(60, "250-500 µm", 250.0, 500.0, 7.41, 0.27, 258.0, 5.0),
    NanoindentationZone(60, "Core",       500.0, None, 7.24, 0.27, 259.0, 4.5),
]


# ---------- Lookups ---------------------------------------------------------


def tensile_for_cr(cw_pct: float) -> TensilePoint:
    for p in USER_M54_TENSILE:
        if p.cw_pct == cw_pct:
            return p
    raise KeyError(
        f"no tensile data for cw_pct={cw_pct}; available: "
        f"{[p.cw_pct for p in USER_M54_TENSILE]}"
    )


def toughness_for_cr(cw_pct: float) -> ToughnessPoint:
    for p in USER_M54_TOUGHNESS:
        if p.cw_pct == cw_pct:
            return p
    raise KeyError(
        f"no toughness data for cw_pct={cw_pct}; available: "
        f"{[p.cw_pct for p in USER_M54_TOUGHNESS]}"
    )


def nanoindent_for_cr(cw_pct: float) -> list[NanoindentationZone]:
    """Return the 5-zone depth profile for one CR condition."""
    rows = [p for p in USER_M54_NANOINDENTATION if p.cw_pct == cw_pct]
    if not rows:
        raise KeyError(f"no nanoindentation data for cw_pct={cw_pct}")
    return rows
