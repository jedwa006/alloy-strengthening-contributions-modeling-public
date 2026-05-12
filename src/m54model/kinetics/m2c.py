"""M2C carbide population predictors for tempered states.

Two factory functions:
- `m2c_population_dq_tempered(T, t)`: M2C in DQ + temper, baselined to Wang 2024
- `m2c_population_af_tempered(T, t)`: M2C in AF + temper, baselined to Cho 2015

Both return a `PrecipitatePopulation` with composition fixed to the M54 APT
measurements from Wang 2024 / Mondière 2018.

Open assumptions documented in code; expect calibration against AF + T425/10
anchor (Sun 2022 anchor 4) to refine these.
"""

from __future__ import annotations

import math

from m54model.kinetics.jma import arrhenius_rate_scale, jma_volume_fraction
from m54model.kinetics.lsw import lsw_radius
from m54model.precipitates import PrecipitatePopulation

# ---------------------------------------------------------------------------
# Composition shared across M54 conditions (APT-measured by both Wang and Mondière)
# ---------------------------------------------------------------------------
M54_M2C_COMPOSITION = {
    "Mo": 0.50,
    "Cr": 0.125,
    "W": 0.10,
    "Fe": 0.10,
    "Ni": 0.10,
    "V": 0.025,
}

# ---------------------------------------------------------------------------
# DQ + tempering kinetics (baselined to Wang 2024 at 520 °C / 8 h)
# ---------------------------------------------------------------------------
# Wang 2024 fit: f(t) = 1 - exp(-8.9e-7 * t^1.26), t in seconds, T = 520 °C.
WANG_K_REF = 8.9e-7
WANG_N = 1.26
WANG_T_REF = 520.0  # Celsius
# Apparent activation energy for M2C precipitation in DQ secondary-hardening
# steel (Cho 2015 Ho-state, 13Co-8Ni — closest available analog to M54 DQ).
Q_M2C_DQ_kJ_per_mol = 407.0  # Cho 2015 Stage 1 (nucleation) for Ho

# Wang 2024 measured M2C population at 520 °C / 8 h (peak):
WANG_PEAK_R_NM = 0.85
WANG_PEAK_L_NM = 12.3
WANG_PEAK_N_PER_M3 = 6.5e20

# LSW coarsening rate constant for M2C in M54 — order-of-magnitude estimate.
# True K_LSW for Cr-Mo-W-V M2C in BCC-Fe is poorly constrained; literature
# spread is 1e-32 to 1e-29 m^3/s. Default to 5e-31 as a midpoint; will calibrate
# against anchor 4 if AF + T predictions are off.
K_LSW_M2C_M3_PER_S = 5e-31


# ---------------------------------------------------------------------------
# AF + tempering kinetics (baselined to Cho 2015 H600 at 475 °C / 1 h)
# ---------------------------------------------------------------------------
# Cho 2015 H600 (severely-rolled at 600 °C) at peak hardening, 475 °C / 1 h:
#   r = 1.52 nm, N = 1.465e23 m^-3, V_f = 0.0040
CHO_H600_PEAK_R_NM = 1.52
CHO_H600_PEAK_N_PER_M3 = 1.465e23
CHO_H600_PEAK_VOLFRAC = 0.0040
CHO_H600_PEAK_TIME_SEC = 3600.0  # 1 h
CHO_H600_T_REF = 475.0  # Celsius
# Cho's H600 effective activation energies:
Q_M2C_AF_NUCLEATION_kJ_per_mol = 137.0  # Stage 1
Q_M2C_AF_COARSENING_kJ_per_mol = 177.0  # Stage 3 (LSW)

# M54 → Cho-13Co-8Ni V_f-saturation scaling.
# Cho's 13Co-8Ni alloy has Cr 3.89 + Mo 1.49 = 5.4 wt% total M2C-formers.
# M54 has Cr 1.0 + Mo 2.0 + W 1.3 + V 0.1 = 4.4 wt%. By stoichiometry, M54's
# max M2C V_f should be roughly 4.4/5.4 = 0.81 of Cho's. Calibration against
# Sun 2022 anchor 4 (AF+T425/10) closes to within ~3.6 % at 0.81 — see
# docs/FINDINGS.md §3 anchor 4.
M54_VS_CHO_VOLFRAC_SCALE = 0.81


def m2c_population_dq_tempered(T_celsius: float, t_hours: float) -> PrecipitatePopulation:
    """Predict M2C population for DQ M54 + isothermal temper at (T, t).

    Pre-peak: Wang 2024 JMA with Arrhenius scaling for T-dependence.
    Post-peak: LSW coarsening on the radius, V_f stays at saturation.

    Returns a PrecipitatePopulation with r_eq, N, L, and V_f estimates.
    """
    t_seconds = t_hours * 3600.0
    # Scale Wang's k from T_ref=520 °C to target T using Arrhenius.
    k_T = WANG_K_REF * arrhenius_rate_scale(Q_M2C_DQ_kJ_per_mol, T_celsius, WANG_T_REF)
    f_v = jma_volume_fraction(k_T, WANG_N, t_seconds)
    # Wang's saturation V_f at 520 °C/peak is ~0.003. Cap accordingly.
    f_v_saturated = min(f_v, 0.003)

    # Radius: starts at Wang's peak r=0.85 nm at peak time (8 h at 520 °C).
    # Pre-peak: scale r ~ (f_v / f_v_peak)^(1/3).
    if f_v >= 0.003:
        # Past peak — coarsen via LSW from the peak time to current t.
        # Estimate peak time at this T using inverse JMA (when f reaches 0.5 of saturation).
        # For simplicity: start LSW at the time when f_v hits 0.003.
        try:
            t_peak = (math.log(1.0 / (1.0 - 0.003)) / k_T) ** (1.0 / WANG_N)
        except (ValueError, ZeroDivisionError):
            t_peak = t_seconds
        t_post_peak = max(0.0, t_seconds - t_peak)
        r_nm = lsw_radius(WANG_PEAK_R_NM, K_LSW_M2C_M3_PER_S, t_post_peak)
    else:
        # Pre-peak: scale r as (f/f_peak)^(1/3) of the Wang peak radius.
        r_nm = WANG_PEAK_R_NM * (f_v_saturated / 0.003) ** (1.0 / 3.0) if f_v_saturated > 0 else 0.0

    # N from f_v and r (treat as equivalent spheres).
    if r_nm > 0 and f_v_saturated > 0:
        r_m = r_nm * 1e-9
        N = 3.0 * f_v_saturated / (4.0 * math.pi * r_m**3)
        # Mean spacing L from N: L ~ N^(-1/3).
        L_nm = (1.0 / N) ** (1.0 / 3.0) * 1e9
    else:
        N = 0.0
        L_nm = 0.0

    return PrecipitatePopulation(
        phase="M2C",
        radius_nm=r_nm,
        number_density_per_m3=N,
        volume_fraction=f_v_saturated,
        spacing_nm=L_nm if L_nm > 0 else None,
        coherency="coherent",
        composition_at_frac=dict(M54_M2C_COMPOSITION),
    )


def m2c_population_af_tempered(T_celsius: float, t_hours: float) -> PrecipitatePopulation:
    """Predict M2C population for ausformed M54 + isothermal temper at (T, t).

    Cho 2015 H600 baseline (severely-rolled, AF analog): peak r=1.52 nm,
    N=1.465e23, V_f=0.0040 at 475 °C / 1 h. We assume V_f saturates at the
    Cho peak value 0.0040 and that r grows via LSW past peak (with a faster
    Q than the DQ case per Cho's data).

    Returns a PrecipitatePopulation. If T or t is well below the AF peak
    conditions, V_f is JMA-scaled down and r is correspondingly smaller.
    """
    t_seconds = t_hours * 3600.0
    # JMA-scale Cho's k from 475 °C to target T using AF nucleation Q.
    k_T = (1.0 / CHO_H600_PEAK_TIME_SEC) * arrhenius_rate_scale(
        Q_M2C_AF_NUCLEATION_kJ_per_mol, T_celsius, CHO_H600_T_REF
    )
    f_v_raw = jma_volume_fraction(k_T, WANG_N, t_seconds)  # use n=1.26 (Wang); Cho doesn't fit n
    # Apply M54 ↔ Cho composition scaling on the saturation V_f.
    vf_sat_M54 = CHO_H600_PEAK_VOLFRAC * M54_VS_CHO_VOLFRAC_SCALE
    f_v_saturated = min(f_v_raw, vf_sat_M54)

    # Compute peak time at current T (using M54-scaled V_f saturation).
    try:
        t_peak_s = (math.log(1.0 / (1.0 - vf_sat_M54)) / k_T) ** (1.0 / WANG_N)
    except (ValueError, ZeroDivisionError):
        t_peak_s = t_seconds

    if t_seconds > t_peak_s:
        # Past peak — LSW coarsening from peak time. Use AF coarsening Q to
        # scale K_LSW from 475 °C to target T (faster at higher T).
        K_LSW_at_T = K_LSW_M2C_M3_PER_S * arrhenius_rate_scale(
            Q_M2C_AF_COARSENING_kJ_per_mol, T_celsius, CHO_H600_T_REF
        )
        r_nm = lsw_radius(CHO_H600_PEAK_R_NM, K_LSW_at_T, t_seconds - t_peak_s)
    else:
        # Pre-peak: scale radius as (f_v/f_v_peak)^(1/3) of Cho's peak.
        if f_v_saturated > 0:
            r_nm = CHO_H600_PEAK_R_NM * (f_v_saturated / vf_sat_M54) ** (1.0 / 3.0)
        else:
            r_nm = 0.0

    # N + L from f_v and r.
    if r_nm > 0 and f_v_saturated > 0:
        r_m = r_nm * 1e-9
        N = 3.0 * f_v_saturated / (4.0 * math.pi * r_m**3)
        L_nm = (1.0 / N) ** (1.0 / 3.0) * 1e9
    else:
        N = 0.0
        L_nm = 0.0

    return PrecipitatePopulation(
        phase="M2C",
        radius_nm=r_nm,
        number_density_per_m3=N,
        volume_fraction=f_v_saturated,
        spacing_nm=L_nm if L_nm > 0 else None,
        coherency="coherent",
        composition_at_frac=dict(M54_M2C_COMPOSITION),
    )
