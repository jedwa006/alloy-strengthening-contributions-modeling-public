"""γ → α′ Bain transformation strain from measured lattice parameters.

The Bain correspondence relates the FCC γ unit cell to the BCT/BCC α′
unit cell. The cell-volume ratio gives the "isotropic-equivalent"
volumetric Bain strain ε^V used in McMeeking-Evans transformation
toughening (Phase 3.5/3.6a):

    V_γ = a_γ³                                [4-atom FCC cell]
    V_α′ (per 4 Fe atoms) = 2 · a_α³          [2-atom BCC cell, ×2]
    ε^V = (V_α′ - V_γ) / V_γ
        = (2 · a_α³ / a_γ³) - 1

For Fe-Ni at room temperature: a_γ ≈ 3.59 Å, a_α ≈ 2.872 Å gives ε^V
≈ +0.04 (the textbook +4 % volume expansion). M54-specific values from
the user's XRD give us a slightly different ε^V because Cr/Mo/V/Co
partition between the two phases.
"""

from __future__ import annotations

BAIN_EPSILON_V_FE_NI_TEXTBOOK = 0.04
"""Textbook Fe-Ni γ → α′ volumetric Bain strain (+4 %).
Often quoted casually; appears to over-state pure-iron transformation
strain. Used as the default in Phase 3.5 McMeeking-Evans BEFORE the
M54-specific XRD-derived value below landed.
"""

BAIN_EPSILON_V_M54_XRD = 0.022
"""M54-specific γ → α′ volumetric Bain strain (+2.2 %), measured from
the user's 0 % CR XRD (this work, Phase 3.6b):
    a_α′ (NR extrapolated) = 2.870 Å
    a_γ (highest-angle peak fit) = 3.589 Å
    ε^V = 2 · a_α³ / a_γ³ - 1 = +0.0222

Roughly half the textbook +0.04 — propagating to ΔK_TRIP halves the
McMeeking-Evans transformation toughening estimate. Phase 3.6a's
'ΔK_TRIP < 1 MPa·m^½' qualitative finding gets stronger.

Pure α-Fe (a=2.866 Å) and γ-Fe (extrapolated to RT, a=3.591 Å) give
ε^V = +0.018, so the +0.022 we measure is consistent with modest
alloying-induced expansion of α′ relative to pure Fe (M54's residual C +
substitutional Ni/Co/Cr/Mo). The frequently-quoted +0.04 appears to
include thermal-expansion / high-T contributions and over-states the
RT value.
"""


def bain_volumetric_strain(a_alpha_A: float, a_gamma_A: float) -> float:
    """ε^V = (2 · a_α³ / a_γ³) - 1.

    The factor of 2 converts the 2-atom BCC cell to a 4-atom equivalent
    (matching the FCC γ cell on a per-atom basis). Returns dimensionless
    strain (positive → expansion γ → α′).

    For Fe-Ni textbook values (a_γ=3.59, a_α=2.872): returns ≈ +0.04.
    For M54 with measured a_α and a_γ: typically +0.02 to +0.05 depending
    on alloying-induced lattice expansion.
    """
    if a_alpha_A <= 0 or a_gamma_A <= 0:
        raise ValueError("lattice parameters must be > 0")
    return (2.0 * a_alpha_A**3 / a_gamma_A**3) - 1.0


def fcc_a0_from_bcc_bain_correspondence(
    a_alpha_A: float,
    epsilon_V: float = BAIN_EPSILON_V_FE_NI_TEXTBOOK,
) -> float:
    """Inverse helper: given α′ a₀ + assumed ε^V, predict γ a₀.

    From ε^V = 2·a_α³/a_γ³ - 1:
        a_γ = a_α · (2 / (1 + ε^V))^(1/3)

    Useful for sanity-checking measured γ peak positions against the BCC
    peak when γ is too weak to fit directly.
    """
    if a_alpha_A <= 0:
        raise ValueError("a_alpha_A must be > 0")
    if epsilon_V <= -1:
        raise ValueError(f"epsilon_V must be > -1 (got {epsilon_V})")
    return a_alpha_A * (2.0 / (1.0 + epsilon_V)) ** (1.0 / 3.0)
