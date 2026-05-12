"""Phase 3.7a — derived mechanical properties from σ_y predictions.

Forward-calc helpers that turn the model's σ_y output into auxiliary
predictions we can compare to additional measured anchors:

- Tabor-style hardness from yield/UTS
- Phase-corrected martensite hardness H_α′ (Ch 5 Eq. 1 inverted)
- Composite hardness H_composite (Ch 5 Eq. 1 forward)

Calibrated to Chapter 5's measured H_α′ at 0 % CR (6.8 GPa) and the
measured σ_UTS at 0 % CR (2100 MPa). The empirically clean Tabor
coefficient for tempered martensitic UHSS is C ≈ 3.24 with σ_UTS as the
input (canonical Tabor σ_UTS / 3 ≈ H), NOT σ_y / 3 (which would need
C ≈ 5.2 for this material — too high, reflects the strong work-hardening
of M54).

H_γ = 4.0 ± 0.5 GPa is the austenite-region nanoindentation value
measured in Chapter 5 (~15 indents on identifiable γ regions in 0 % CR
specimen). Within Fe-Ni austenite literature range.

References:
- Tabor relation: D. Tabor, Hardness of Metals, OUP 1951.
- Phase-correction Eq. 1: J. Edwards et al., Chapter 5 of CSM thesis,
  "Contributions to Strength and Plasticity in Incremental Cold Rolled
  Ausformed and Tempered Ferrium M54" (in preparation), §"Phase-
  Corrected Martensite Hardness".
"""

from __future__ import annotations

from dataclasses import dataclass

# ---- Tabor + phase-correction constants (Chapter 5 calibration) ------------------------

DEFAULT_TABOR_COEFFICIENT_SIGMA_UTS = 3.24
"""H[GPa] ≈ σ_UTS[MPa] / (1000 · C); empirically C ≈ 3.24 for AF+T M54
matches the 0 % CR baseline (σ_UTS = 2100 MPa, H_α′ = 6.8 GPa per
Chapter 5 Fig 5). Within canonical Tabor range (typically 2.8-3.5 for
metals with significant strain hardening)."""

DEFAULT_TABOR_COEFFICIENT_SIGMA_Y = 5.23
"""H[GPa] ≈ σ_y[MPa] / (1000 · C); empirically C ≈ 5.23 for AF+T M54.
Higher than canonical Tabor (3) because M54 has significant work-
hardening (σ_UTS/σ_y ≈ 1.62 at 0 % CR), so YS isn't the right "flow
stress" for the indentation regime — UTS is."""

DEFAULT_H_GAMMA_GPA = 4.0
"""Austenite hardness from Chapter 5 indents on identifiable γ regions
in 0 % CR specimen (~15 indents). 4.0 ± 0.5 GPa is the published value;
within Fe-Ni austenite literature range."""

DEFAULT_H_GAMMA_STD_GPA = 0.5
"""1σ uncertainty on H_γ from Chapter 5 measurement."""


# ---- Tabor relations ------------------------------------------------------------------


def tabor_hardness_GPa_from_sigma_uts(
    sigma_uts_MPa: float,
    tabor_coefficient: float = DEFAULT_TABOR_COEFFICIENT_SIGMA_UTS,
) -> float:
    """H[GPa] = (C · σ_UTS[MPa]) / 1000 with C ≈ 3.24 for AF+T M54.

    Canonical Tabor relation H ≈ C · σ_flow. The empirical C is the
    H_α′(0 % CR)/σ_UTS(0 % CR) ratio = 6.8/2.1 = 3.24, within textbook
    range for metals with significant work hardening (typically 2.8-3.5).
    """
    if sigma_uts_MPa <= 0:
        raise ValueError(f"σ_UTS must be > 0, got {sigma_uts_MPa}")
    if tabor_coefficient <= 0:
        raise ValueError(f"tabor_coefficient must be > 0, got {tabor_coefficient}")
    return tabor_coefficient * sigma_uts_MPa / 1000.0


def tabor_hardness_GPa_from_sigma_y(
    sigma_y_MPa: float,
    tabor_coefficient: float = DEFAULT_TABOR_COEFFICIENT_SIGMA_Y,
) -> float:
    """H[GPa] = (C · σ_y[MPa]) / 1000 with C ≈ 5.23 for AF+T M54.

    The H/σ_y ratio is higher than canonical Tabor (~3) because M54 has
    substantial work-hardening capacity (σ_UTS/σ_y ≈ 1.62 at 0 % CR), so
    the indentation samples a flow stress closer to σ_UTS than σ_y.
    Use the σ_UTS-based Tabor when possible; this σ_y form is provided
    for cases where only σ_y is available.
    """
    if sigma_y_MPa <= 0:
        raise ValueError(f"σ_y must be > 0, got {sigma_y_MPa}")
    if tabor_coefficient <= 0:
        raise ValueError(f"tabor_coefficient must be > 0, got {tabor_coefficient}")
    return tabor_coefficient * sigma_y_MPa / 1000.0


def sigma_uts_MPa_from_hardness(
    H_GPa: float,
    tabor_coefficient: float = DEFAULT_TABOR_COEFFICIENT_SIGMA_UTS,
) -> float:
    """Inverse Tabor: σ_UTS[MPa] = 1000 · H[GPa] / C."""
    if H_GPa <= 0:
        raise ValueError(f"H must be > 0, got {H_GPa}")
    if tabor_coefficient <= 0:
        raise ValueError(f"tabor_coefficient must be > 0, got {tabor_coefficient}")
    return 1000.0 * H_GPa / tabor_coefficient


# ---- Chapter 5 Eq. 1 — phase-correction rule of mixtures ------------------------------


def composite_hardness_GPa(
    H_alpha_prime_GPa: float,
    f_gamma: float,
    H_gamma_GPa: float = DEFAULT_H_GAMMA_GPA,
) -> float:
    """Chapter 5 Eq. 1 (forward): H_composite = f_γ · H_γ + (1−f_γ) · H_α′.

    Linear rule-of-mixtures with austenite phase fraction f_γ.
    """
    if not 0.0 <= f_gamma <= 1.0:
        raise ValueError(f"f_gamma must be in [0, 1], got {f_gamma}")
    if H_alpha_prime_GPa <= 0 or H_gamma_GPa <= 0:
        raise ValueError("hardnesses must be > 0")
    return f_gamma * H_gamma_GPa + (1.0 - f_gamma) * H_alpha_prime_GPa


def phase_corrected_alpha_prime_hardness_GPa(
    H_composite_GPa: float,
    f_gamma: float,
    H_gamma_GPa: float = DEFAULT_H_GAMMA_GPA,
) -> float:
    """Chapter 5 Eq. 1 (inverted): H_α′ = (H_composite − f_γ · H_γ) / (1 − f_γ).

    Recover the matrix-only martensite hardness from a measured
    composite hardness given a known γ fraction. Use this when you have
    a bulk H measurement (nanoindent average) and want the underlying
    martensite-only H to compare to a model prediction.

    Returns 0 if (1 − f_γ) is too small to invert reliably (avoids
    blowup at f_γ → 1).
    """
    if not 0.0 <= f_gamma <= 1.0:
        raise ValueError(f"f_gamma must be in [0, 1], got {f_gamma}")
    denom = 1.0 - f_gamma
    if denom < 0.05:
        return 0.0  # f_γ too close to 1 — Eq. 1 numerically degenerate
    return (H_composite_GPa - f_gamma * H_gamma_GPa) / denom


# ---- High-level prediction wrappers ---------------------------------------------------


@dataclass(frozen=True)
class DerivedPropertyPrediction:
    """Bundle of derived-property predictions for one state."""

    label: str
    sigma_y_qs_MPa: float
    """Quasi-static yield (linear sum, before austenite correction)."""
    sigma_y_corrected_MPa: float
    """Yield with rule-of-mixtures austenite correction."""
    sigma_y_user_rate_MPa: float
    """× strain-rate factor 1.054 for direct comparison to user tensile."""
    H_alpha_prime_GPa: float
    """Predicted martensite-only hardness via Tabor on UTS proxy."""
    H_composite_GPa: float
    """Predicted bulk hardness via Eq. 1 forward, using f_γ from state."""
    f_gamma: float
    work_hardening_ratio: float
    """Assumed σ_UTS/σ_y used to estimate UTS for Tabor."""


def predict_derived_properties(
    state,
    *,
    work_hardening_ratio: float = 1.62,
    H_gamma_GPa: float = DEFAULT_H_GAMMA_GPA,
    tabor_C_uts: float = DEFAULT_TABOR_COEFFICIENT_SIGMA_UTS,
    apply_strain_rate_correction: bool = True,
) -> DerivedPropertyPrediction:
    """Forward-calc bundle for one MicrostructuralState.

    Steps:
      1. Compute σ_y_qs (linear sum) and σ_y_corrected (with f_A
         rule-of-mix) via the existing strengthening assembler.
      2. Apply strain-rate correction (×1.054 default) for user-rate σ_y.
      3. Estimate σ_UTS_α′ ≈ σ_y_α′ · `work_hardening_ratio` (matrix only,
         before austenite correction). Default ratio 1.62 = empirical
         AF+T M54 0 % CR baseline.
      4. Predict H_α′ via Tabor: H_α′[GPa] = σ_UTS_α′[MPa] / (1000 · C).
      5. Predict H_composite via Eq. 1 forward with state's f_γ.

    `work_hardening_ratio` is the single calibration knob for UTS-from-YS.
    Default 1.62 is calibrated to 0 % CR (σ_UTS=2100, σ_y=1300). The user's
    measured ratios at 47/53/60 % CR are 1.44, 1.47, 1.42 — slightly lower
    once heavy CW saturates work-hardening, so this default over-predicts
    UTS by ~10 % at high CR. A future enhancement could fit a CR-dependent
    work-hardening exponent.
    """
    from m54model.calibration.strain_rate import (
        EPS_DOT_SUN_2022_S_INV,
        EPS_DOT_USER_TENSILE_S_INV,
        strain_rate_correction,
    )
    from m54model.strengthening import assemble_yield_strength

    res = assemble_yield_strength(state)
    # Phase 3.6f sub-block HP increment is stashed on the state by the
    # cw factory (see m54_af_t516_10_cw); pick it up so our derived
    # predictions track the same σ_y the cw sweep uses.
    delta_subblock = getattr(state, "_subblock_HP_increment_MPa", 0.0)
    sigma_y_qs = res.sigma_y_MPa + delta_subblock  # matrix-only, no f_A correction
    sigma_y_corrected = res.sigma_y_austenite_corrected_MPa + delta_subblock

    factor = (
        strain_rate_correction(
            EPS_DOT_USER_TENSILE_S_INV, EPS_DOT_SUN_2022_S_INV, m=0.01
        )
        if apply_strain_rate_correction
        else 1.0
    )
    sigma_y_user_rate = sigma_y_corrected * factor

    # Tabor on the matrix-only UTS (NOT the rule-of-mix-corrected value,
    # since H_α′ is by definition the matrix-only hardness).
    sigma_uts_alpha_prime = sigma_y_qs * work_hardening_ratio
    H_alpha_prime = tabor_hardness_GPa_from_sigma_uts(
        sigma_uts_alpha_prime, tabor_coefficient=tabor_C_uts
    )

    # Composite hardness — folds the predicted H_α′ with the state's f_γ.
    H_comp = composite_hardness_GPa(H_alpha_prime, state.f_austenite, H_gamma_GPa=H_gamma_GPa)

    return DerivedPropertyPrediction(
        label=state.label,
        sigma_y_qs_MPa=sigma_y_qs,
        sigma_y_corrected_MPa=sigma_y_corrected,
        sigma_y_user_rate_MPa=sigma_y_user_rate,
        H_alpha_prime_GPa=H_alpha_prime,
        H_composite_GPa=H_comp,
        f_gamma=state.f_austenite,
        work_hardening_ratio=work_hardening_ratio,
    )


# Empirical work-hardening ratio σ_UTS/σ_y per CR condition, from
# USER_M54_TENSILE (Chapter 5 Table 3): linearly fit across measured
# points and bracketed for 20 % / 40 % CR (no measurement yet).
# At 0 % CR: 2100/1300 = 1.62; at 60 % CR: 2700/1900 = 1.42.
EMPIRICAL_WORK_HARDENING_RATIO_BY_CR = {0: 1.62, 20: 1.55, 40: 1.49, 60: 1.42}
"""Per-CR σ_UTS/σ_y ratio from user tensile data (linear interp 0→60 % CR).
Drops with CR because cold work consumes work-hardening capacity. Used as
the default UTS-from-σ_y multiplier in `predict_derived_properties_cw_cr_sweep`."""


def predict_derived_properties_cw_cr_sweep(
    *,
    location: str = "core",
    cw_pcts: tuple[int, ...] = (0, 20, 40, 60),
    work_hardening_ratio: float | None = None,
    H_gamma_GPa: float = DEFAULT_H_GAMMA_GPA,
    subblock_hp_K_MPa_um_half: float = 0.0,
    refinement_engagement_fraction: float | None = None,
    apply_strain_rate_correction: bool = True,
) -> list[dict[str, float | str | None]]:
    """Predict derived properties across the user's cw/cr sweep + compare to
    measurements (Chapter 5 phase-corrected H_α′ + USER_M54_NANOINDENTATION
    bulk H + USER_M54_TENSILE σ_UTS where available).

    `work_hardening_ratio`: if None (default), uses CR-dependent
    empirical ratio from `EMPIRICAL_WORK_HARDENING_RATIO_BY_CR`. Pass a
    constant float to override (e.g. 1.62 for the conventional 0 % CR
    value across all conditions).
    """
    from m54model.calibration import (
        m54_af_t516_10_cw,
        nanoindent_for_cr,
        tensile_for_cr,
    )

    # Chapter 5 Fig 5 phase-corrected H_α′ values (read from the figure)
    CH5_PHASE_CORRECTED_H_ALPHA_PRIME_GPA = {0: 6.8, 20: 8.2, 40: 9.8, 60: 8.9}

    rows: list[dict[str, float | str | None]] = []
    for cw in cw_pcts:
        state = m54_af_t516_10_cw(
            float(cw),
            location=location,
            subblock_hp_K_MPa_um_half=subblock_hp_K_MPa_um_half,
            refinement_engagement_fraction=refinement_engagement_fraction,
        )
        wh_ratio = (
            work_hardening_ratio
            if work_hardening_ratio is not None
            else EMPIRICAL_WORK_HARDENING_RATIO_BY_CR.get(cw, 1.5)
        )
        pred = predict_derived_properties(
            state,
            work_hardening_ratio=wh_ratio,
            H_gamma_GPa=H_gamma_GPa,
            apply_strain_rate_correction=apply_strain_rate_correction,
        )
        # Measured anchors
        try:
            m_tensile = tensile_for_cr(float(cw))
            uts_meas_MPa = m_tensile.UTS_MPa
            yield_meas_MPa = m_tensile.sigma_y_MPa
        except KeyError:
            uts_meas_MPa = None
            yield_meas_MPa = None
        try:
            ni_zones = nanoindent_for_cr(float(cw))
            H_bulk_meas_GPa = sum(z.H_GPa for z in ni_zones) / len(ni_zones)
        except KeyError:
            H_bulk_meas_GPa = None
        H_alpha_prime_ch5 = CH5_PHASE_CORRECTED_H_ALPHA_PRIME_GPA.get(cw)
        rows.append(
            {
                "cw_pct": float(cw),
                "f_gamma": pred.f_gamma,
                # Yield
                "sigma_y_user_rate_MPa": round(pred.sigma_y_user_rate_MPa, 1),
                "sigma_y_meas_MPa": yield_meas_MPa,
                # UTS (matrix-only via Tabor)
                "sigma_uts_alpha_prime_pred_MPa": round(
                    pred.sigma_y_qs_MPa * pred.work_hardening_ratio, 1
                ),
                "sigma_uts_meas_MPa": uts_meas_MPa,
                # Hardness
                "H_alpha_prime_pred_GPa": round(pred.H_alpha_prime_GPa, 2),
                "H_alpha_prime_ch5_meas_GPa": H_alpha_prime_ch5,
                "H_composite_pred_GPa": round(pred.H_composite_GPa, 2),
                "H_composite_meas_GPa": (
                    round(H_bulk_meas_GPa, 2) if H_bulk_meas_GPa is not None else None
                ),
            }
        )
    return rows
