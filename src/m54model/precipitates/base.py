"""PrecipitatePopulation — uniform structure for all carbide types."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Literal

PhaseType = Literal["M2C", "MC", "M3C", "M6C", "M7C3", "M23C6", "NiAl"]
Coherency = Literal["coherent", "semi_coherent", "incoherent"]


@dataclass(frozen=True)
class PrecipitatePopulation:
    """A statistical population of one carbide type in one microstructural state.

    Sizes can be supplied as (length, width) for rod-like phases like M2C, or
    as a single radius for spherical phases like NiAl. The equivalent radius
    is computed for use in Ashby-Orowan.
    """

    phase: PhaseType
    length_nm: float | None = None  # for rod-like
    width_nm: float | None = None  # for rod-like
    radius_nm: float | None = None  # for spherical
    number_density_per_m3: float | None = None
    volume_fraction: float | None = None
    spacing_nm: float | None = None
    coherency: Coherency = "incoherent"
    composition_at_frac: dict[str, float] = field(default_factory=dict)

    @property
    def equivalent_radius_nm(self) -> float | None:
        """Volume-equivalent spherical radius.

        For rods (length l, width w): r_eq = ((3 * (w/2)^2 * l) / 4)^(1/3)
        following Wang 2024 Eq. 9 (the same form Mondière uses).
        For spheres: just r.
        """
        if self.radius_nm is not None:
            return self.radius_nm
        if self.length_nm is not None and self.width_nm is not None:
            l = self.length_nm
            w = self.width_nm
            return (3.0 * (w / 2.0) ** 2 * l / 4.0) ** (1.0 / 3.0)
        return None

    @property
    def aspect_ratio(self) -> float | None:
        if self.length_nm and self.width_nm:
            return self.length_nm / self.width_nm
        return None

    @property
    def volume_fraction_inferred(self) -> float | None:
        """Compute f_v from N and equivalent radius if not given directly."""
        if self.volume_fraction is not None:
            return self.volume_fraction
        if self.number_density_per_m3 and self.equivalent_radius_nm:
            r_m = self.equivalent_radius_nm * 1e-9
            return self.number_density_per_m3 * (4.0 / 3.0) * math.pi * r_m**3
        return None
