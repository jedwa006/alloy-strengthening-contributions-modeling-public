"""User's measured microstructure data — grain size and GND density by phase
across the cw/cr series.

Companion to `user_trip_data.py` (austenite phase fractions). Together these
three datasets paint a coherent picture of the M54 deformation response:

1. **Grain size** (Table 3 below): bimodal character at 40 % CR Surface is
   direct microstructural evidence for the cellular shear-band network that
   mediates the austenite spike documented in `user_trip_data.py`.
2. **GND density** (Table 4 below): BCC ρ peaks at 40 % CR (concentrated
   plastic-strain energy in dislocation walls); FCC ρ is consistently
   ~5–10 × higher than BCC across all CR conditions, indicating heavily-
   strained austenite — implications for the σ_A = 360 MPa default we use
   in the rule-of-mixtures (likely too low for the cw/cr regime; see
   FINDINGS.md §6 Phase 3.2).
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------- Table 3: ASTAR grain-size statistics by CR + location -----------------------
#
# CR | Loc.  | Mean GA (nm) | Median GA (nm) | %<50nm | %>200nm | Characteristic
# ----|-------|--------------|----------------|--------|---------|------------------------
# 0% | Surf. |   62-75      |       60       |   35   |    5    | Unimodal, lath mart.
# 0% | Core  |   212        |      180       |    5   |   45    | Coarser; PAGs uniform
# 20%| Surf. |   71-75      |       68       |   40   |    8    | Heterogeneous onset
# 20%| Core  |   105        |      60-70     |  40-45 |  15-20  | Coarse, uniform PAGs
# 40%| Surf. |    37        |       —        |   60   |   20    | **Bimodal (fine+remnant)**
# 40%| Core  |   67-73      |       62       |   30   |   10    | Bimodal; moderate refine
# 60%| Surf. |   53-116     |       85       |   20   |   12    | Unimodal; intermed. refine
# 60%| Core  |   51-57      |       50       |   40   |    5    | Continued refinement


@dataclass(frozen=True)
class GrainSizeStats:
    """ASTAR grain-area statistics for one CR condition + cross-section location.

    Mean grain area reported as a range (low, high) for most measurements;
    a single value when only one figure was given.
    """

    cw_pct: float
    location: str  # 'surface' | 'core'
    mean_grain_area_nm_low: float
    mean_grain_area_nm_high: float
    median_grain_area_nm: float | None  # None when '—' in the table
    pct_less_than_50nm: float  # %<50 nm fine population
    pct_greater_than_200nm: float  # %>200 nm coarse population
    characteristic: str  # qualitative description from user

    @property
    def mean_grain_area_nm_mid(self) -> float:
        return 0.5 * (self.mean_grain_area_nm_low + self.mean_grain_area_nm_high)

    @property
    def is_bimodal(self) -> bool:
        """User's flag: bimodal if both fine and coarse populations are
        substantial (heuristic: %<50 nm > 25 % AND %>200 nm > 8 %)."""
        return self.pct_less_than_50nm > 25 and self.pct_greater_than_200nm > 8


USER_M54_GRAIN_SIZE: list[GrainSizeStats] = [
    GrainSizeStats(0, "surface", 62, 75, 60.0, 35, 5, "Unimodal, lath martensite"),
    GrainSizeStats(0, "core", 212, 212, 180.0, 5, 45, "Coarser; PAGs uniform"),
    GrainSizeStats(20, "surface", 71, 75, 68.0, 40, 8, "Heterogeneous onset"),
    GrainSizeStats(20, "core", 105, 105, 65.0, 42.5, 17.5, "Coarse, largely still uniform PAGs"),
    GrainSizeStats(
        40, "surface", 37, 37, None, 60, 20, "Bimodal (fine + remnant) — cellular network signature"
    ),
    GrainSizeStats(40, "core", 67, 73, 62.0, 30, 10, "Bimodal; moderate refinement"),
    GrainSizeStats(60, "surface", 53, 116, 85.0, 20, 12, "Unimodal; intermediate refinement"),
    GrainSizeStats(60, "core", 51, 57, 50.0, 40, 5, "Continued refinement"),
]


# ---------- Table 4: ASTAR-PED extrapolated GND density by phase + CR -------------------
#
# CR  | BCC median ρ (×10¹⁵ m⁻²) | BCC 90th-pct ρ (×10¹⁶ m⁻²) | FCC median ρ (×10¹⁶ m⁻²) | n grains BCC
# ----|---------------------------|------------------------------|----------------------------|--------------
#  0  |          1.6              |             4.8              |            6.5             |     34
# 20  |          6.3              |             4.2              |            3.3             |     46
# 40* |          7.9              |             5.7              |            3.8             |      4    (*small n)
# 60  |          6.3              |             5.0              |            3.2             |     24


@dataclass(frozen=True)
class GNDDensityStats:
    """ASTAR-PED extrapolated GND density at one CR condition, phase-resolved.

    BCC = α′ martensite matrix; FCC = γ retained/reverted austenite films.
    """

    cw_pct: float
    bcc_median_rho_per_m2: float  # m⁻²
    bcc_p90_rho_per_m2: float  # 90th-percentile m⁻²
    fcc_median_rho_per_m2: float  # m⁻² (note: typically 5-10× larger than BCC median)
    n_grains_bcc: int  # sample size for BCC statistic
    notes: str = ""


USER_M54_GND_DENSITY: list[GNDDensityStats] = [
    GNDDensityStats(
        0,
        bcc_median_rho_per_m2=1.6e15,
        bcc_p90_rho_per_m2=4.8e16,
        fcc_median_rho_per_m2=6.5e16,
        n_grains_bcc=34,
        notes="As-quenched baseline; FCC already heavily defected",
    ),
    GNDDensityStats(
        20,
        bcc_median_rho_per_m2=6.3e15,
        bcc_p90_rho_per_m2=4.2e16,
        fcc_median_rho_per_m2=3.3e16,
        n_grains_bcc=46,
    ),
    GNDDensityStats(
        40,
        bcc_median_rho_per_m2=7.9e15,
        bcc_p90_rho_per_m2=5.7e16,
        fcc_median_rho_per_m2=3.8e16,
        n_grains_bcc=4,
        notes="* small n grains; corresponds to the austenite spike",
    ),
    GNDDensityStats(
        60,
        bcc_median_rho_per_m2=6.3e15,
        bcc_p90_rho_per_m2=5.0e16,
        fcc_median_rho_per_m2=3.2e16,
        n_grains_bcc=24,
    ),
]


def gnd_for_cr(cw_pct: float, *, location_phase: str = "BCC_median") -> float:
    """Look up GND density at a given CR condition.

    `location_phase`: one of {'BCC_median', 'BCC_p90', 'FCC_median'}.
    """
    for entry in USER_M54_GND_DENSITY:
        if entry.cw_pct == cw_pct:
            if location_phase == "BCC_median":
                return entry.bcc_median_rho_per_m2
            if location_phase == "BCC_p90":
                return entry.bcc_p90_rho_per_m2
            if location_phase == "FCC_median":
                return entry.fcc_median_rho_per_m2
            raise ValueError(f"unknown location_phase {location_phase!r}")
    raise KeyError(f"no GND data for cw_pct={cw_pct}")


def grain_size_for_cr(cw_pct: float, *, location: str = "surface") -> GrainSizeStats:
    """Look up grain-size stats for a given CR condition + location."""
    for entry in USER_M54_GRAIN_SIZE:
        if entry.cw_pct == cw_pct and entry.location == location:
            return entry
    raise KeyError(f"no grain-size data for cw_pct={cw_pct}, location={location!r}")
