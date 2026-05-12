"""Empirical strain-rate correction for cross-comparing tensile data.

The model predicts quasi-static σ_y, but the user's tensile data was
collected at 10⁻¹ s⁻¹ — 200× faster than Sun 2022's 5 × 10⁻⁴ s⁻¹.
For low-SRS BCC steels (tempered martensite at room temp), the Norton
power law gives a small but non-negligible correction:

  σ_y(ε̇₂) / σ_y(ε̇₁) = (ε̇₂ / ε̇₁)^m       [Norton; e.g. Bridgman 1944]

with m ≈ 0.01 for tempered M54 (literature value, low strain-rate
sensitivity at room temp; see Hopkinson-bar data in Zhu 2025 Fig. 12 for
qualitative confirmation that high-SRS regime kicks in only at ε̇ ≥ 10² s⁻¹).

For the user's 200× ratio:
  (200)^0.01 = exp(0.01 · ln 200) ≈ 1.054

→ ~5 % above the quasi-static prediction. Worth ~70-90 MPa at M54
strength levels (1400-1800 MPa).
"""

from __future__ import annotations

import math

# Default strain-rate sensitivity exponent for tempered M54 at room temp.
# Empirical; literature range for tempered martensitic UHSS is m ∈ [0.005, 0.02].
M_TEMPERED_M54_DEFAULT = 0.01

# Reference quasi-static rate the model anchors are calibrated at (Sun 2022).
EPS_DOT_SUN_2022_S_INV = 5.0e-4

# Rate at which the user's tensile data was collected.
EPS_DOT_USER_TENSILE_S_INV = 1.0e-1


def strain_rate_correction(
    eps_dot_target_s_inv: float,
    eps_dot_reference_s_inv: float = EPS_DOT_SUN_2022_S_INV,
    m: float = M_TEMPERED_M54_DEFAULT,
) -> float:
    """Multiplicative factor to convert σ_y(reference rate) → σ_y(target rate).

    Returns (ε̇_target / ε̇_reference)^m. Multiply a quasi-static-calibrated
    prediction by this factor when comparing to data collected at a faster
    rate; divide a measurement by this factor to recover the quasi-static
    value before comparison to model.

    Defaults assume the M54 quasi-static reference is Sun 2022 (5 × 10⁻⁴ s⁻¹)
    and the strain-rate sensitivity exponent is m = 0.01 (tempered M54).
    """
    if eps_dot_target_s_inv <= 0 or eps_dot_reference_s_inv <= 0:
        raise ValueError("strain rates must be > 0")
    if m < 0:
        raise ValueError(f"strain-rate sensitivity m must be >= 0, got {m}")
    return (eps_dot_target_s_inv / eps_dot_reference_s_inv) ** m


def explain_strain_rate_correction(
    eps_dot_target_s_inv: float = EPS_DOT_USER_TENSILE_S_INV,
    eps_dot_reference_s_inv: float = EPS_DOT_SUN_2022_S_INV,
    m: float = M_TEMPERED_M54_DEFAULT,
) -> str:
    """Pretty-print the algebra for show-your-work in the notebook."""
    ratio = eps_dot_target_s_inv / eps_dot_reference_s_inv
    factor = strain_rate_correction(eps_dot_target_s_inv, eps_dot_reference_s_inv, m)
    pct = (factor - 1.0) * 100
    return (
        f"  reference rate (Sun 2022 quasi-static):  ε̇_ref  = {eps_dot_reference_s_inv:.1e} s⁻¹\n"
        f"  target rate (user tensile):              ε̇_tgt  = {eps_dot_target_s_inv:.1e} s⁻¹\n"
        f"  ratio:                                   ε̇_tgt / ε̇_ref = {ratio:g}×\n"
        f"  empirical exponent for tempered M54:     m       = {m}\n"
        f"  ln(ratio):                                       = {math.log(ratio):.4f}\n"
        f"  m · ln(ratio):                                   = {m * math.log(ratio):.4f}\n"
        f"  correction factor = exp(m · ln ratio)            = {factor:.4f}\n"
        f"  → multiply quasi-static σ_y by {factor:.3f} (+{pct:.2f} %) to compare to user tensile."
    )
