"""Phase 3.8a — through-thickness mixture model for σ_y(CR).

Replaces the single-location prediction (location='surface' or 'core')
with a per-zone prediction + volume-weighted bulk average. Motivated
by Chapter 4 §"Grain Architecture and Through-Thickness Refinement"
which explicitly defines the "refinement front" — surface deforms first,
propagates inward with CR.

The user's nanoindent data (`USER_M54_NANOINDENTATION`) is *already*
zone-resolved at 5 depth bands: 0-50 / 50-100 / 100-250 / 250-500 µm /
Core. This module ties the model to that experimental design directly:
- Per zone, interpolate microstructure inputs (f_A, sub-block size)
  between the user's measured surface and core values based on the
  zone's depth fraction d/(T/2).
- Predict σ_y per zone via the existing strengthening assembler.
- Volume-weight to bulk σ_y using zone thicknesses + measured plate
  thickness at each CR (3.80 / 3.04 / 2.28 / 1.52 mm per Ch 5 §M&M).

Intentional v1 simplifications (Phase 3.8a):
- ρ_GND is held constant per CR (the user's `USER_M54_GND_DENSITY` is a
  median, not zone-resolved). Future v2 could vary it via 90th-percentile
  vs median per-zone if such data lands.
- Linear interpolation between surface and core for f_A and d_subblock.
  Ch 4 explicitly notes the refinement front is "gradual rather than
  abrupt" at intermediate CR — linear is reasonable. Ground-truth would
  require finer-grained ASTAR scans through the cross-section.
- Zone widths fixed in absolute µm; their volume fractions adapt with
  plate thickness.

Replaces the Phase 3.7b empirical f_engaged(CR) calibration with a
microstructure-derived bulk prediction. If the through-thickness mixture
gives the same answer as f_engaged(CR) tuned to data, that's evidence the
empirical knot points are physically grounded.
"""

from __future__ import annotations

from dataclasses import dataclass

# Zone depth midpoints (µm from rolled surface). Matches the user's
# nanoindent zone definitions in `USER_M54_NANOINDENTATION`.
ZONE_DEPTH_MIDPOINT_UM = {
    "0-50 µm": 25.0,
    "50-100 µm": 75.0,
    "100-250 µm": 175.0,
    "250-500 µm": 375.0,
    "Core": None,  # depth = T/4, depends on plate thickness
}

ZONE_THICKNESS_UM = {
    "0-50 µm": 50.0,
    "50-100 µm": 50.0,
    "100-250 µm": 150.0,
    "250-500 µm": 250.0,
    "Core": None,  # half_plate - 500
}

ZONE_LABELS = ("0-50 µm", "50-100 µm", "100-250 µm", "250-500 µm", "Core")

# Plate thickness at each CR % per Chapter 5 §"Material and Processing":
# 3.80 / 3.04 / 2.28 / 1.52 mm computed from 3.80 mm starting plate.
PLATE_THICKNESS_UM_BY_CR = {0: 3800.0, 20: 3040.0, 40: 2280.0, 60: 1520.0}


@dataclass(frozen=True)
class ZonePrediction:
    """Per-zone σ_y prediction + microstructure inputs used."""

    cw_pct: int
    zone_label: str
    depth_um: float
    """Zone midpoint depth (µm from rolled surface)."""
    depth_normalized: float
    """depth / (T/2); 0 at rolled surface, 1 at mid-plane."""
    volume_fraction: float
    """Fraction of half-plate volume in this zone (= total-plate fraction by
    symmetry — both surfaces contribute identical zone profiles)."""
    f_A: float
    """Interpolated f_austenite at this zone's depth."""
    d_subblock_nm: float
    """Interpolated median grain size (nm) at this zone's depth."""
    sigma_y_user_rate_MPa: float


def zone_volume_fraction(zone_label: str, plate_thickness_um: float) -> float:
    """Fraction of half-plate volume in a given zone.

    For a symmetric plate of thickness T, half-thickness = T/2; both
    surfaces contribute identical zone profiles, so half-plate fractions
    equal full-plate fractions.

    Returns 0 if `Core` is requested but the half-plate is thinner than
    500 µm (the start of the Core zone) — defensive only; for the user's
    actual plates (1.52-3.80 mm) this never triggers.
    """
    half_T = plate_thickness_um / 2.0
    if zone_label == "Core":
        if half_T <= 500.0:
            return 0.0
        return (half_T - 500.0) / half_T
    thickness = ZONE_THICKNESS_UM[zone_label]
    return thickness / half_T


def interpolate_at_depth(
    surface_value: float, core_value: float, depth_normalized: float
) -> float:
    """Linear interpolation between surface (depth=0) and core (depth=1).

    depth_normalized ∈ [0, 1]; clipped if outside.
    """
    d = max(0.0, min(1.0, depth_normalized))
    return surface_value + (core_value - surface_value) * d


def microstructure_at_zone(
    cw_pct: int, zone_label: str, plate_thickness_um: float | None = None
) -> dict[str, float]:
    """Return interpolated f_A and d_subblock at one zone for one CR.

    Surface values from `USER_M54_CW_AUSTENITE_SURFACE` and surface
    `USER_M54_GRAIN_SIZE`; core analogues. Linear in
    depth_normalized = zone_depth / (T/2).
    """
    from m54model.calibration.user_microstructure_data import grain_size_for_cr
    from m54model.calibration.user_trip_data import (
        USER_M54_CW_AUSTENITE_CORE,
        USER_M54_CW_AUSTENITE_SURFACE,
    )

    if plate_thickness_um is None:
        plate_thickness_um = PLATE_THICKNESS_UM_BY_CR.get(cw_pct)
        if plate_thickness_um is None:
            raise KeyError(f"no default plate thickness for cw_pct={cw_pct}")
    half_T = plate_thickness_um / 2.0

    if zone_label == "Core":
        depth_um = (half_T + 500.0) / 2.0  # midpoint of Core zone
    else:
        depth_um = ZONE_DEPTH_MIDPOINT_UM[zone_label]
    depth_norm = depth_um / half_T

    fA_surf = next(p for p in USER_M54_CW_AUSTENITE_SURFACE if p.cw_pct == cw_pct).f_austenite
    fA_core = next(p for p in USER_M54_CW_AUSTENITE_CORE if p.cw_pct == cw_pct).f_austenite
    f_A = interpolate_at_depth(fA_surf, fA_core, depth_norm)

    g_surf = grain_size_for_cr(cw_pct, location="surface")
    g_core = grain_size_for_cr(cw_pct, location="core")
    d_surf_nm = g_surf.median_grain_area_nm or g_surf.mean_grain_area_nm_mid
    d_core_nm = g_core.median_grain_area_nm or g_core.mean_grain_area_nm_mid
    d_sub_nm = interpolate_at_depth(d_surf_nm, d_core_nm, depth_norm)

    return {
        "f_A": f_A,
        "d_subblock_nm": d_sub_nm,
        "depth_um": depth_um,
        "depth_normalized": depth_norm,
        "volume_fraction": zone_volume_fraction(zone_label, plate_thickness_um),
    }


def predict_zone_sigma_y(
    cw_pct: int,
    zone_label: str,
    *,
    subblock_hp_K_MPa_um_half: float = 150.0,
    apply_strain_rate_correction: bool = True,
    plate_thickness_um: float | None = None,
) -> ZonePrediction:
    """Predict σ_y at one (CR, zone) using zone-interpolated f_A +
    sub-block-HP increment built from zone-interpolated d_subblock.

    Uses the existing strengthening assembler with zone-appropriate
    f_austenite. Sub-block HP increment is computed against the SAME
    location's 0 % CR baseline d_subblock at the zone's depth — i.e.
    the increment captures only cw-induced refinement at this depth,
    not the as-tempered baseline structure.

    Note: ρ_GND is held at the per-CR `USER_M54_GND_DENSITY` median —
    we don't have zone-resolved GND. This means the predicted σ_y(zone)
    captures *only* the f_A and sub-block-HP variation between zones,
    not GND gradients.
    """
    from m54model.calibration import strain_rate_correction
    from m54model.calibration.strain_rate import (
        EPS_DOT_SUN_2022_S_INV,
        EPS_DOT_USER_TENSILE_S_INV,
    )
    from m54model.calibration.anchors import _matrix_tempered
    from m54model.calibration.user_microstructure_data import gnd_for_cr
    from m54model.kinetics import m2c_population_af_tempered
    from m54model.states import MicrostructuralState
    from m54model.strengthening import assemble_yield_strength

    micro = microstructure_at_zone(cw_pct, zone_label, plate_thickness_um)
    rho_GND = gnd_for_cr(cw_pct, location_phase="BCC_median")
    m2c = m2c_population_af_tempered(T_celsius=516.0, t_hours=10.0)

    state = MicrostructuralState(
        state="af_tempered_cw_zone",
        block_width_um=0.48,
        packet_size_um=6.7,
        pag_width_um=47.0,
        lath_width_nm=135.0,
        dislocation_density_per_m2=rho_GND,
        f_austenite=micro["f_A"],
        f_austenite_kind="reverted",
        matrix_at_frac=_matrix_tempered(),
        wt_pct_C_in_solution=0.003,
        precipitates=[m2c],
        label=f"M54 AF + T516/10 + {cw_pct} % CR (zone={zone_label})",
    )

    # Sub-block HP increment via the zone-interpolated d_subblock vs the
    # SAME zone's 0 % CR baseline d_subblock. (Built directly here rather
    # than reusing _subblock_hp_increment_MPa, since that helper takes
    # location='surface'|'core', not depth-interpolated values.)
    delta_subblock = 0.0
    if subblock_hp_K_MPa_um_half > 0 and cw_pct != 0:
        baseline_micro = microstructure_at_zone(0, zone_label, PLATE_THICKNESS_UM_BY_CR[0])
        d0_um = baseline_micro["d_subblock_nm"] / 1000.0
        dN_um = micro["d_subblock_nm"] / 1000.0
        if d0_um > 0 and dN_um > 0:
            delta_subblock = subblock_hp_K_MPa_um_half * (
                dN_um ** -0.5 - d0_um ** -0.5
            )

    res = assemble_yield_strength(state)
    sigma_qs = res.sigma_y_austenite_corrected_MPa + delta_subblock
    factor = (
        strain_rate_correction(
            EPS_DOT_USER_TENSILE_S_INV, EPS_DOT_SUN_2022_S_INV, m=0.01
        )
        if apply_strain_rate_correction
        else 1.0
    )
    sigma_user = sigma_qs * factor

    return ZonePrediction(
        cw_pct=cw_pct,
        zone_label=zone_label,
        depth_um=micro["depth_um"],
        depth_normalized=micro["depth_normalized"],
        volume_fraction=micro["volume_fraction"],
        f_A=micro["f_A"],
        d_subblock_nm=micro["d_subblock_nm"],
        sigma_y_user_rate_MPa=sigma_user,
    )


def predict_bulk_sigma_y_through_thickness(
    cw_pct: int,
    *,
    subblock_hp_K_MPa_um_half: float = 150.0,
    apply_strain_rate_correction: bool = True,
) -> dict[str, float | list[ZonePrediction]]:
    """Volume-weighted average of per-zone σ_y predictions to bulk.

    Returns {bulk_sigma_y_MPa, zones: [ZonePrediction, ...]}.
    """
    zone_preds = [
        predict_zone_sigma_y(
            cw_pct,
            zone,
            subblock_hp_K_MPa_um_half=subblock_hp_K_MPa_um_half,
            apply_strain_rate_correction=apply_strain_rate_correction,
        )
        for zone in ZONE_LABELS
    ]
    sum_vf = sum(z.volume_fraction for z in zone_preds)
    bulk = sum(z.volume_fraction * z.sigma_y_user_rate_MPa for z in zone_preds) / sum_vf
    return {"bulk_sigma_y_MPa": round(bulk, 1), "zones": zone_preds}


def derive_zone_sigma_y_from_nanoindent(
    cw_pct: int,
    zone_label: str,
    *,
    H_gamma_GPa: float = 4.0,
    tabor_C_uts: float = 3.24,
    work_hardening_ratio: float | None = None,
    apply_strain_rate_correction: bool = True,
) -> dict[str, float]:
    """Phase 3.8b — invert measured per-zone H_composite to derive an
    equivalent measured σ_y at that zone.

    Pipeline:
      1. Measured H_composite from `USER_M54_NANOINDENTATION` for this
         (CR, zone).
      2. Interpolated f_A at this zone (same scheme as Phase 3.8a).
      3. Eq. 1 (Ch 5) inverted: H_α′ = (H_composite − f_A · H_γ) / (1 − f_A).
      4. Tabor: σ_UTS_α′ = H_α′ · 1000 / tabor_C_uts.
      5. σ_y_α′ = σ_UTS_α′ / work_hardening_ratio.
      6. Optionally rate-correct via the standard +5.4 % bump.

    Returns a dict with the inputs + intermediate + derived σ_y so each
    step is auditable. This is "what σ_y would the H + f_A + Tabor +
    WH-ratio chain say at this zone if we trust the measurements?"

    Together with `predict_zone_sigma_y` (which predicts σ_y from
    microstructure inputs ALONE), this gives a per-zone measurement-
    derived anchor — turning the user's 5-zone × 4-CR nanoindent grid
    into 20 σ_y comparison points instead of just 4 bulk tensile points.
    """
    from m54model.calibration import nanoindent_for_cr
    from m54model.calibration.strain_rate import (
        EPS_DOT_SUN_2022_S_INV,
        EPS_DOT_USER_TENSILE_S_INV,
        strain_rate_correction,
    )
    from m54model.strengthening.derived_properties import (
        EMPIRICAL_WORK_HARDENING_RATIO_BY_CR,
        phase_corrected_alpha_prime_hardness_GPa,
    )

    if work_hardening_ratio is None:
        work_hardening_ratio = EMPIRICAL_WORK_HARDENING_RATIO_BY_CR.get(cw_pct, 1.5)

    zones = nanoindent_for_cr(cw_pct)
    zone = next(z for z in zones if z.zone_label == zone_label)
    H_composite_GPa = zone.H_GPa

    micro = microstructure_at_zone(cw_pct, zone_label)
    f_A = micro["f_A"]

    H_alpha_prime = phase_corrected_alpha_prime_hardness_GPa(
        H_composite_GPa, f_A, H_gamma_GPa=H_gamma_GPa
    )
    if H_alpha_prime <= 0:
        # Eq. 1 numerically degenerate at very high f_A (Phase 3.7a guard);
        # signal to consumers that this point is unusable.
        return {
            "cw_pct": float(cw_pct),
            "zone_label": zone_label,
            "H_composite_GPa": H_composite_GPa,
            "f_A_interpolated": f_A,
            "H_alpha_prime_derived_GPa": 0.0,
            "sigma_uts_alpha_prime_derived_MPa": 0.0,
            "sigma_y_alpha_prime_derived_MPa": 0.0,
            "sigma_y_user_rate_derived_MPa": 0.0,
            "work_hardening_ratio_assumed": work_hardening_ratio,
            "valid": False,
        }

    sigma_uts_alpha = H_alpha_prime * 1000.0 / tabor_C_uts
    sigma_y_alpha = sigma_uts_alpha / work_hardening_ratio
    factor = (
        strain_rate_correction(
            EPS_DOT_USER_TENSILE_S_INV, EPS_DOT_SUN_2022_S_INV, m=0.01
        )
        if apply_strain_rate_correction
        else 1.0
    )
    return {
        "cw_pct": float(cw_pct),
        "zone_label": zone_label,
        "H_composite_GPa": H_composite_GPa,
        "f_A_interpolated": f_A,
        "H_alpha_prime_derived_GPa": H_alpha_prime,
        "sigma_uts_alpha_prime_derived_MPa": sigma_uts_alpha,
        "sigma_y_alpha_prime_derived_MPa": sigma_y_alpha,
        "sigma_y_user_rate_derived_MPa": sigma_y_alpha * factor,
        "work_hardening_ratio_assumed": work_hardening_ratio,
        "valid": True,
    }


def per_zone_predicted_vs_derived_sweep(
    cw_pcts: tuple[int, ...] = (0, 20, 40, 60),
    *,
    subblock_hp_K_MPa_um_half: float = 150.0,
    H_gamma_GPa: float = 4.0,
) -> list[dict[str, float | str | None]]:
    """20-row table (5 zones × 4 CR) comparing per-zone *predicted* σ_y
    (from microstructure inputs alone, Phase 3.8a) against per-zone
    *derived* σ_y (from H_composite + f_A + Tabor + WH ratio, Phase 3.8b).

    Per-zone agreement validates the linear-interpolation + Tabor
    framework; per-zone disagreement highlights where the microstructure-
    only prediction misses a real per-zone effect (e.g., surface matrix
    work-hardening that f_A interpolation can't capture)."""
    rows: list[dict[str, float | str | None]] = []
    for cw in cw_pcts:
        for zone in ZONE_LABELS:
            pred = predict_zone_sigma_y(
                cw, zone, subblock_hp_K_MPa_um_half=subblock_hp_K_MPa_um_half
            )
            derived = derive_zone_sigma_y_from_nanoindent(
                cw, zone, H_gamma_GPa=H_gamma_GPa
            )
            sigma_pred = pred.sigma_y_user_rate_MPa
            sigma_derived = derived["sigma_y_user_rate_derived_MPa"]
            if not derived["valid"] or sigma_derived <= 0:
                miss = None
            else:
                miss = (sigma_pred - sigma_derived) / sigma_derived * 100
            rows.append(
                {
                    "cw_pct": cw,
                    "zone_label": zone,
                    "depth_um": pred.depth_um,
                    "f_A_interpolated": pred.f_A,
                    "H_composite_meas_GPa": derived["H_composite_GPa"],
                    "H_alpha_prime_derived_GPa": (
                        round(derived["H_alpha_prime_derived_GPa"], 2)
                        if derived["valid"] else None
                    ),
                    "sigma_y_predicted_MPa": round(sigma_pred, 1),
                    "sigma_y_derived_MPa": (
                        round(sigma_derived, 1) if derived["valid"] else None
                    ),
                    "miss_pct": round(miss, 1) if miss is not None else None,
                }
            )
    return rows


def through_thickness_sweep(
    cw_pcts: tuple[int, ...] = (0, 20, 40, 60),
    *,
    subblock_hp_K_MPa_um_half: float = 150.0,
) -> list[dict[str, float | str | None]]:
    """Sweep across CR conditions, return bulk through-thickness σ_y vs measured."""
    from m54model.calibration import tensile_for_cr

    rows: list[dict[str, float | str | None]] = []
    for cw in cw_pcts:
        result = predict_bulk_sigma_y_through_thickness(
            cw, subblock_hp_K_MPa_um_half=subblock_hp_K_MPa_um_half
        )
        try:
            m = tensile_for_cr(float(cw))
            meas = m.sigma_y_MPa
            std = m.sigma_y_std_MPa
            miss = (result["bulk_sigma_y_MPa"] - meas) / meas * 100
        except KeyError:
            meas = None
            std = None
            miss = None
        rows.append(
            {
                "cw_pct": cw,
                "bulk_sigma_y_user_rate_MPa": result["bulk_sigma_y_MPa"],
                "sigma_y_meas_MPa": meas,
                "sigma_y_meas_std_MPa": std,
                "miss_pct": round(miss, 1) if miss is not None else None,
                "zones": result["zones"],
            }
        )
    return rows
