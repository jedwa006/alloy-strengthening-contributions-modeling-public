"""Calibration anchors — MicrostructuralState factories matching published M54 data.

Each factory returns a state that exactly mirrors the microstructure measurements
from the source paper, so the model's prediction can be compared against that
paper's reported YS.
"""

from __future__ import annotations

from m54model.alloys import FERRIUM_M54
from m54model.kinetics import m2c_population_af_tempered
from m54model.precipitates import PrecipitatePopulation
from m54model.states import MicrostructuralState


def _matrix_dq() -> dict[str, float]:
    """At-fraction matrix for the DQ state — all alloying still in solid solution."""
    return FERRIUM_M54.at_frac()


def _matrix_tempered(consumed: dict[str, float] | None = None) -> dict[str, float]:
    """At-fraction matrix after carbide precipitation has consumed certain elements.

    Default consumption fractions reflect Wang 2024 / Mondière APT measurements
    of M2C composition: M2C is dominantly Mo (50 at%) with Cr/W/V/Fe/Ni shares.
    Ti is consumed by undissolved MC pinners (most of the 0.013 wt% goes there).
    """
    consumed = consumed or {
        "Mo": 0.80,
        "Cr": 0.80,
        "W": 0.80,
        "V": 0.80,
        "Ti": 0.95,
        "C": 0.99,
    }
    af = FERRIUM_M54.at_frac()
    matrix = {k: v * (1.0 - consumed.get(k, 0.0)) for k, v in af.items()}
    total = sum(matrix.values())
    return {k: v / total for k, v in matrix.items()}


def sun_2022_dq() -> MicrostructuralState:
    """Sun 2022 direct-quench (no temper). Anchor: YS = 1420 MPa."""
    return MicrostructuralState(
        state="direct_quench",
        block_width_um=1.18,
        packet_size_um=13.1,
        pag_width_um=100.0,
        lath_width_nm=135.0,  # midpoint of 70-200 nm range
        dislocation_density_per_m2=2.08e15,
        f_austenite=0.0,
        matrix_at_frac=_matrix_dq(),
        wt_pct_C_in_solution=0.30,  # nominal alloy C, all in supersaturation
        precipitates=[],
        label="Sun 2022 DQ",
    )


def sun_2022_dq_t516_10() -> MicrostructuralState:
    """Sun 2022 direct-quench + 516 °C / 10 h temper (commercial spec).
    Anchor: YS = 1762 MPa, UTS = 2050 MPa.

    Uses Wang 2024's measured M2C population at 520 °C / 8 h (peak hardening,
    closest available datapoint to commercial 516/10 spec). Mondière 2018
    reports M2C at 516/10 as 9.6 nm × 1.2 nm rod but does not give number
    density or volume fraction — Wang's data is more complete.
    """
    m2c = PrecipitatePopulation(
        phase="M2C",
        length_nm=4.0,
        width_nm=0.8,
        number_density_per_m3=6.5e20,
        spacing_nm=12.3,
        coherency="coherent",
        composition_at_frac={
            "Mo": 0.50,
            "Cr": 0.125,
            "W": 0.10,
            "Fe": 0.10,
            "Ni": 0.10,
            "V": 0.025,
        },
    )
    return MicrostructuralState(
        state="dq_tempered",
        block_width_um=1.18,
        packet_size_um=13.1,
        pag_width_um=100.0,
        lath_width_nm=135.0,
        dislocation_density_per_m2=1.12e15,
        f_austenite=0.0,
        matrix_at_frac=_matrix_tempered(),
        wt_pct_C_in_solution=0.003,  # Wang 2024 APT: 99% of C consumed by M2C
        precipitates=[m2c],
        label="Sun 2022 DQ + T516/10",
    )


def sun_2022_af550_45() -> MicrostructuralState:
    """Sun 2022 AF550/45 — ausformed at 550 °C with 45 % reduction, post-cryo.
    Anchor: YS = 1830 MPa.

    No tempering, no carbide precipitation (just the as-ausformed structure).
    """
    return MicrostructuralState(
        state="ausformed",
        block_width_um=0.48,
        packet_size_um=6.7,
        pag_width_um=47.0,
        lath_width_nm=135.0,  # similar to DQ; ausforming refines block more than lath
        dislocation_density_per_m2=7.81e15,
        f_austenite=0.0,
        matrix_at_frac=_matrix_dq(),
        wt_pct_C_in_solution=0.30,  # ausforming doesn't consume C (no temper yet)
        precipitates=[],
        label="Sun 2022 AF550/45",
    )


# Phase 3.7b: empirical CR-dependent refinement-engagement fraction.
# Calibrated to Chapter 4 §"Grain Architecture and Through-Thickness
# Refinement" qualitative description + Phase 3.7a forward-calc
# H_α′ data. Justification per CR:
#   0 %:  no cw → no engagement.
#   20 %: refinement still surface-localized per Ch 4 ("substructural
#         heterogeneity at surface; core remains coarse and lath-dominant").
#         Forward-calc H_α′ at K_sub=150 over-predicted Ch 5 H_α′(20%) by
#         +17 %, consistent with f_engaged ≈ 0 at 20 %.
#   40 %: bimodal architecture — fragmented surface zones + remnant lath
#         core. f_engaged ≈ 0.5-0.7 (partial engagement).
#   60 %: refinement penetrated through cross-section, "uniformly refined
#         microstructure" per Ch 4. f_engaged ≈ 1.0.
DEFAULT_REFINEMENT_ENGAGEMENT_FRACTION_BY_CR = {0: 0.0, 20: 0.0, 40: 0.7, 60: 1.0}
"""Empirical f_engaged(CR) ∈ [0, 1] that scales the K_sub increment to
reflect the through-thickness extent of cw-induced sub-block refinement.

At low CR the refinement is surface-localized and contributes little to
bulk strength; at high CR the refinement is cross-section-wide and
contributes fully. Calibrated against Ch 4 microstructure descriptions
+ Phase 3.7a H_α′ data.

Replaces the Phase 3.6f assumption that K_sub applies uniformly across
all CR. Rationale in FINDINGS Phase 3.7b.
"""


def _subblock_hp_increment_MPa(
    cw_pct: int,
    location: str,
    K_sub_MPa_um_half: float,
    refinement_engagement_fraction: float | None = None,
) -> float:
    """Phase 3.6f / 3.7b: Hall-Petch increment from cw-induced sub-block refinement.

    Δσ<sub>HP,sub</sub> = f<sub>engaged</sub>(CR) · K<sub>sub</sub> ·
                          (d<sub>sub</sub><sup>−½</sup> − d<sub>sub,baseline</sub><sup>−½</sup>)

    Computed RELATIVE to the 0 % CR value at the same location, so the
    baseline σ<sub>HP</sub> (which is empirically calibrated to capture
    the cellular substructure already present in AF + temper) is not
    double-counted. d<sub>sub</sub> = median ASTAR grain size (nm) from
    `USER_M54_GRAIN_SIZE`; falls back to mean-mid when median is None.

    `refinement_engagement_fraction` (Phase 3.7b): if None (default), uses
    `DEFAULT_REFINEMENT_ENGAGEMENT_FRACTION_BY_CR[cw_pct]`. Pass an
    explicit float (e.g. 1.0) to recover the Phase 3.6f uniform-K_sub
    behavior.

    Returns 0 when K<sub>sub</sub> = 0 (the default — sub-block HP
    disabled), at cw_pct=0 by construction, or when f<sub>engaged</sub>=0.
    """
    if K_sub_MPa_um_half == 0.0 or cw_pct == 0:
        return 0.0
    from m54model.calibration.user_microstructure_data import grain_size_for_cr

    f_engaged = (
        refinement_engagement_fraction
        if refinement_engagement_fraction is not None
        else DEFAULT_REFINEMENT_ENGAGEMENT_FRACTION_BY_CR.get(cw_pct, 1.0)
    )
    if f_engaged == 0.0:
        return 0.0

    g0 = grain_size_for_cr(0, location=location)
    gN = grain_size_for_cr(cw_pct, location=location)
    d0_nm = g0.median_grain_area_nm or g0.mean_grain_area_nm_mid
    dN_nm = gN.median_grain_area_nm or gN.mean_grain_area_nm_mid
    d0_um = d0_nm / 1000.0
    dN_um = dN_nm / 1000.0
    if d0_um <= 0 or dN_um <= 0:
        return 0.0
    return f_engaged * K_sub_MPa_um_half * (dN_um ** -0.5 - d0_um ** -0.5)


def _f_A_for_cr(cw_pct: int, source: str) -> float:
    """Phase 3.6h: f_A pickup with three measurement-source choices.

    'astar_surface' (default) — surface-localized ASTAR map (small sample,
    catches the surface cellular network, e.g. 26 % at 40 % CR).
    'astar_core' — through-thickness median ASTAR.
    'xrd_bulk' — Modified Miller V_γ from the Cu-equivalent XRD spectrum
    averaged over the bulk irradiated volume; only available at 0 % CR
    where γ peaks are above noise (4.81 %); fallback to ASTAR core for
    20/40/60 % CR where bulk XRD shows essentially no γ (Phase 3.6b
    XRD-vs-ASTAR divergence).
    """
    from m54model.calibration.user_trip_data import (
        USER_M54_CW_AUSTENITE_CORE,
        USER_M54_CW_AUSTENITE_SURFACE,
    )

    if source == "astar_surface":
        ds = USER_M54_CW_AUSTENITE_SURFACE
    elif source in ("astar_core", "xrd_bulk"):
        # XRD bulk only has signal at 0 % CR; fallback to ASTAR core.
        if source == "xrd_bulk" and cw_pct == 0:
            return 0.0481  # from m54model.xrd analyze_xrd_for_cr(0).V_gamma_pct/100
        ds = USER_M54_CW_AUSTENITE_CORE
    else:
        raise ValueError(
            f"unknown f_A_source {source!r}; "
            "expected 'astar_surface', 'astar_core', or 'xrd_bulk'"
        )
    pt = next((p for p in ds if p.cw_pct == cw_pct), None)
    if pt is None:
        raise KeyError(f"no f_A data at cw_pct={cw_pct}")
    return pt.f_austenite


def m54_af_t516_10_cw(
    cw_pct: float,
    *,
    location: str = "surface",
    ssd_multiplier: float = 1.0,
    subblock_hp_K_MPa_um_half: float = 0.0,
    f_A_source: str | None = None,
    refinement_engagement_fraction: float | None = None,
) -> MicrostructuralState:
    """**Phase 3.6d / 3.6e** — M54 AF + T516/10 + N % cold-rolling state factory.

    Builds on `m54_af550_45_t516_10()` (the cw/cr starting state) and swaps
    in the user's measured cw/cr inputs:

    - **Dislocation density**: ρ<sub>total</sub> = `ssd_multiplier` ×
      ρ<sub>GND</sub> from `USER_M54_GND_DENSITY`. ASTAR-PED measures GND
      only; SSDs are not directly observed. Lit-review finding (Phase
      3.6e): no paper in our refs explicitly partitions ρ<sub>GND</sub>
      from ρ<sub>SSD</sub> in the strengthening equation — most use XRD-WH
      total ρ as the input, with no published k = ρ<sub>total</sub> /
      ρ<sub>GND</sub> consensus for cold-worked martensitic UHSS at
      ε<sub>p</sub> ≈ 1. Default `ssd_multiplier = 1.0` (no SSD
      addition — i.e., trust ASTAR ρ<sub>GND</sub> as ρ<sub>total</sub>);
      use 2.0-3.0 to explore the effect of adding SSDs on top. The
      ground-truth answer for these specific samples would come from a
      modified Williamson-Hall analysis on the user's XRD spectra
      (Phase 3.6e+ deliverable; data already loaded via
      `m54model.xrd.load_xrd_spectrum`).
    - **Reverted austenite fraction**: from `USER_M54_CW_AUSTENITE_SURFACE`
      (or `_CORE` if `location='core'`).
    - **Block width**: held at 0.48 µm (Sun AF baseline) — cold rolling
      fragments at the sub-block scale, not the block scale. The
      sub-block (cell) refinement that ASTAR sees is not captured by
      block-based Hall-Petch; addressed in Phase 3.6f via a separate
      sub-block Hall-Petch term (when implemented).
    - **M2C population**: held at the 516 °C / 10 h post-temper state —
      cold rolling at room temp (T_max ≈ 80 °C) is too cold for further
      M2C precipitation/coarsening on the rolling timescale.
    - **Matrix at-fraction + C in solid solution**: held at tempered values.

    `cw_pct` must be in {0, 20, 40, 60} (the user's ASTAR/GND
    measurement points). Use 0 to recover `m54_af550_45_t516_10()`
    directly with the location-specific f_A.
    """
    if ssd_multiplier < 1.0:
        raise ValueError(
            f"ssd_multiplier must be >= 1.0 (1.0 = GND only); got {ssd_multiplier}"
        )
    if subblock_hp_K_MPa_um_half < 0.0:
        raise ValueError(
            "subblock_hp_K_MPa_um_half must be >= 0 "
            f"(0 = disabled); got {subblock_hp_K_MPa_um_half}"
        )
    from m54model.calibration.user_microstructure_data import gnd_for_cr
    from m54model.calibration.user_trip_data import (
        USER_M54_CW_AUSTENITE_CORE,
        USER_M54_CW_AUSTENITE_SURFACE,
    )

    if location not in ("surface", "core"):
        raise ValueError(f"location must be 'surface' or 'core', got {location!r}")

    cw_int = int(cw_pct)

    # f_A source: explicit f_A_source argument wins; otherwise fall back to
    # `location`-derived ASTAR pickup (preserves Phase 3.6d/e/f behavior).
    if f_A_source is not None:
        f_A_value = _f_A_for_cr(cw_int, f_A_source)
    else:
        austenite_dataset = (
            USER_M54_CW_AUSTENITE_SURFACE if location == "surface"
            else USER_M54_CW_AUSTENITE_CORE
        )
        f_A_pt = next((p for p in austenite_dataset if p.cw_pct == cw_int), None)
        if f_A_pt is None:
            raise KeyError(f"no f_A data at cw_pct={cw_pct}, location={location!r}")
        f_A_value = f_A_pt.f_austenite

    rho_BCC_GND = gnd_for_cr(cw_int, location_phase="BCC_median")
    rho_total = ssd_multiplier * rho_BCC_GND
    delta_sigma_subblock_MPa = _subblock_hp_increment_MPa(
        cw_int,
        location,
        subblock_hp_K_MPa_um_half,
        refinement_engagement_fraction=refinement_engagement_fraction,
    )

    m2c = m2c_population_af_tempered(T_celsius=516.0, t_hours=10.0)
    parts = []
    if ssd_multiplier != 1.0:
        parts.append(f"ρ_SSD ×{ssd_multiplier:.1f}")
    if subblock_hp_K_MPa_um_half != 0.0:
        parts.append(f"K_sub={subblock_hp_K_MPa_um_half:.0f} → +{delta_sigma_subblock_MPa:.0f} MPa")
    suffix = f" ({location}, {'; '.join(parts)})" if parts else f" ({location})"
    state = MicrostructuralState(
        state="af_tempered_cw",
        block_width_um=0.48,
        packet_size_um=6.7,
        pag_width_um=47.0,
        lath_width_nm=135.0,
        dislocation_density_per_m2=rho_total,
        f_austenite=f_A_value,
        f_austenite_kind="reverted",
        matrix_at_frac=_matrix_tempered(),
        wt_pct_C_in_solution=0.003,
        precipitates=[m2c],
        label=f"M54 AF + T516/10 + {cw_int} % CR{suffix}",
    )
    # Stash the sub-block HP increment as a private attribute so
    # `predict_cw_cr_sweep` can pick it up. Frozen-dataclass-safe via
    # object.__setattr__ (bypasses the dataclass-installed __setattr__
    # without mutating the dataclass invariants).
    object.__setattr__(state, "_subblock_HP_increment_MPa", delta_sigma_subblock_MPa)
    return state


def predict_cw_cr_sweep(
    *,
    location: str = "core",
    cw_pcts: tuple[int, ...] = (0, 20, 40, 60),
    apply_strain_rate_correction: bool = True,
    ssd_multiplier: float = 1.0,
    subblock_hp_K_MPa_um_half: float = 0.0,
    f_A_source: str | None = None,
    refinement_engagement_fraction: float | None = None,
) -> list[dict[str, float | str | None]]:
    """Phase 3.6d sweep: predict σ_y at each CR condition and compare to
    measured tensile (where available).

    Returns list of dicts with keys:
        cw_pct, sigma_y_qs_MPa, sigma_y_user_rate_MPa, sigma_y_meas_MPa,
        sigma_y_meas_std_MPa, miss_pct, f_austenite, rho_GND_per_m2.

    `location='core'` is the right default for cross-comparing to a bulk
    tensile bar (the surface f_A measurement is too localized to
    represent bulk material). Use `location='surface'` to see the
    extreme-end prediction at the rolling face.
    """
    from m54model.calibration.strain_rate import (
        EPS_DOT_SUN_2022_S_INV,
        EPS_DOT_USER_TENSILE_S_INV,
        strain_rate_correction,
    )
    from m54model.calibration.user_mechanical_data import tensile_for_cr
    from m54model.strengthening import assemble_yield_strength

    factor = (
        strain_rate_correction(
            EPS_DOT_USER_TENSILE_S_INV, EPS_DOT_SUN_2022_S_INV, m=0.01
        )
        if apply_strain_rate_correction
        else 1.0
    )

    rows: list[dict[str, float | str | None]] = []
    for cw in cw_pcts:
        state = m54_af_t516_10_cw(
            float(cw),
            location=location,
            ssd_multiplier=ssd_multiplier,
            subblock_hp_K_MPa_um_half=subblock_hp_K_MPa_um_half,
            f_A_source=f_A_source,
            refinement_engagement_fraction=refinement_engagement_fraction,
        )
        res = assemble_yield_strength(state)
        # Add the cw-induced sub-block HP increment outside the assembler:
        # it's a model-form extension specific to cw/cr conditions, not a
        # property of MicrostructuralState in general.
        delta_subblock = getattr(state, "_subblock_HP_increment_MPa", 0.0)
        sigma_qs = res.sigma_y_austenite_corrected_MPa + delta_subblock
        sigma_user = sigma_qs * factor
        try:
            m = tensile_for_cr(float(cw))
            meas = m.sigma_y_MPa
            meas_std = m.sigma_y_std_MPa
            miss = (sigma_user - meas) / meas * 100.0
        except KeyError:
            meas = None
            meas_std = None
            miss = None
        rows.append(
            {
                "cw_pct": float(cw),
                "location": location,
                "sigma_y_qs_MPa": round(sigma_qs, 1),
                "sigma_y_user_rate_MPa": round(sigma_user, 1),
                "sigma_y_meas_MPa": meas,
                "sigma_y_meas_std_MPa": meas_std,
                "miss_pct": round(miss, 1) if miss is not None else None,
                "f_austenite": state.f_austenite,
                "rho_GND_per_m2": state.dislocation_density_per_m2,
            }
        )
    return rows


def m54_af550_45_t516_10() -> MicrostructuralState:
    """M54 AF550/45 + commercial 516 °C / 10 h temper — the **user's cw/cr baseline**.

    NOTE: This is NOT a Sun 2022 anchor (Sun used T425/10). It's the actual
    starting state for the user's cold-rolling series.

    **Prior history:** the strip was cross-rolled to achieve the ausformed form
    (or to reach the target geometry post-ausforming) BEFORE the 516 °C / 10 h
    temper. Cross-rolling means multi-axial deformation in two perpendicular
    directions before tempering, not the simple uniaxial AF550/45 of Sun 2022.
    Microstructural impact of the cross-rolling is largely reset by the long
    high-T temper (M2C precipitation, dislocation recovery), so we use Sun's
    AF550/45 block + Wang's tempering-invariant block-size assumption as a
    reasonable proxy. The 0 % CR ASTAR microstructure (Table 3 of user data)
    confirms this is a fine-block-fine-lath structure consistent with AF.

    Microstructural inputs:
    - Block width 0.48 µm: from Sun's AF state; tempering doesn't refine block
      (Wang 2024 confirms block invariant in DQ across 2-10 h tempering).
    - Dislocation density 1.6 × 10¹⁵ m⁻²: directly from the user's ASTAR-PED
      measurement at 0 % CR baseline (Table 4). Slightly higher than Sun's
      AF+T425/10 (1.18 × 10¹⁵), consistent with the longer/hotter 516 °C / 10 h
      temper retaining slightly more dislocation density via M2C-pinning.
    - M2C: predicted via `m2c_population_af_tempered(516, 10)` — past peak,
      LSW-coarsened, V_f at M54-stoichiometry-scaled saturation.
    - Reverted austenite: 0.013 (= 1.3 % surface) per user's ASTAR phase
      fraction at 0 % CR. f_austenite_kind set to 'reverted' since cryo
      removes most retained γ and 516 °C / 10 h is long enough for lath-
      boundary Ni-enriched reversion.
    - C in solid solution: ~0.003 wt% (M2C precipitation depletes matrix C).

    No published YS anchor — anchor will come from the user's measurements
    when available (tensile-tested at 0 % CR baseline). NB: those tests are
    at strain rate 10⁻¹ s⁻¹ vs Sun's 5×10⁻⁴ s⁻¹ (200× faster). For tempered
    M54 with strain-rate sensitivity m ≈ 0.01, expect measured σ_y to be
    ~5 % above Sun-equivalent quasi-static value. The model predicts
    quasi-static; remember to multiply by ~1.05 when comparing to user
    tensile data.
    """
    m2c = m2c_population_af_tempered(T_celsius=516.0, t_hours=10.0)
    return MicrostructuralState(
        state="af_tempered",
        block_width_um=0.48,
        packet_size_um=6.7,
        pag_width_um=47.0,
        lath_width_nm=135.0,
        dislocation_density_per_m2=1.6e15,
        f_austenite=0.013,
        f_austenite_kind="reverted",
        matrix_at_frac=_matrix_tempered(),
        wt_pct_C_in_solution=0.003,
        precipitates=[m2c],
        label="M54 AF550/45 + T516/10 (user's cw/cr baseline)",
    )


def sun_2022_af550_45_t425_10() -> MicrostructuralState:
    """Sun 2022 enhanced commercial route: AF550/45 then 425 °C / 10 h temper.
    Anchor: YS = 1726 MPa.

    Microstructure inputs from Sun 2022 measurements (block, dislocation
    density, lath). M2C population is **predicted** from Cho 2015 → M54
    transferred kinetics via `m2c_population_af_tempered(425, 10)` —
    Sun 2022 did not characterize M2C in this state, so this is the first
    quantitative estimate.
    """
    m2c = m2c_population_af_tempered(T_celsius=425.0, t_hours=10.0)
    return MicrostructuralState(
        state="af_tempered",
        block_width_um=0.48,  # ausforming refines from 1.18 to 0.48 µm
        packet_size_um=6.7,
        pag_width_um=47.0,
        lath_width_nm=135.0,
        dislocation_density_per_m2=1.18e15,  # post-temper recovered to ~DQ+T levels
        f_austenite=0.0,
        matrix_at_frac=_matrix_tempered(),
        wt_pct_C_in_solution=0.003,  # tempered — C consumed by M2C
        precipitates=[m2c],
        label="Sun 2022 AF550/45 + T425/10",
    )
