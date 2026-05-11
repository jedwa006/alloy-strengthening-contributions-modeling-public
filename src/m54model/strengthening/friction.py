"""Lattice friction stress (sigma_0)."""

from m54model.constants import SIGMA_0_MPA


def sigma_friction() -> float:
    """Intrinsic lattice friction stress for secondary-hardening BCC steel.

    Universal value (50 MPa) per Sun 2022, Wang 2024, Zhu 2025.
    """
    return SIGMA_0_MPA
