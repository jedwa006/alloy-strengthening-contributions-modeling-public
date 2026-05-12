"""Strengthening contribution functions and assembly."""

from m54model.strengthening.dislocation import sigma_dislocation
from m54model.strengthening.friction import sigma_friction
from m54model.strengthening.hall_petch import sigma_hall_petch
from m54model.strengthening.intrinsic_martensite import sigma_intrinsic_martensite
from m54model.strengthening.orowan import sigma_orowan_carbide
from m54model.strengthening.solid_solution import sigma_fleischer
from m54model.strengthening.derived_properties import (
    DEFAULT_H_GAMMA_GPA,
    DEFAULT_TABOR_COEFFICIENT_SIGMA_UTS,
    DEFAULT_TABOR_COEFFICIENT_SIGMA_Y,
    EMPIRICAL_WORK_HARDENING_RATIO_BY_CR,
    DerivedPropertyPrediction,
    composite_hardness_GPa,
    phase_corrected_alpha_prime_hardness_GPa,
    predict_derived_properties,
    predict_derived_properties_cw_cr_sweep,
    sigma_uts_MPa_from_hardness,
    tabor_hardness_GPa_from_sigma_uts,
    tabor_hardness_GPa_from_sigma_y,
)
from m54model.strengthening.through_thickness import (
    PLATE_THICKNESS_UM_BY_CR,
    ZONE_LABELS,
    ZonePrediction,
    interpolate_at_depth,
    microstructure_at_zone,
    predict_bulk_sigma_y_through_thickness,
    predict_zone_sigma_y,
    through_thickness_sweep,
    zone_volume_fraction,
)
from m54model.strengthening.total import StrengtheningResult, assemble_yield_strength

__all__ = [
    "sigma_friction",
    "sigma_fleischer",
    "sigma_hall_petch",
    "sigma_dislocation",
    "sigma_orowan_carbide",
    "sigma_intrinsic_martensite",
    "assemble_yield_strength",
    "StrengtheningResult",
    # Derived-property forward-calc (Phase 3.7a)
    "tabor_hardness_GPa_from_sigma_uts",
    "tabor_hardness_GPa_from_sigma_y",
    "sigma_uts_MPa_from_hardness",
    "composite_hardness_GPa",
    "phase_corrected_alpha_prime_hardness_GPa",
    "predict_derived_properties",
    "predict_derived_properties_cw_cr_sweep",
    "DerivedPropertyPrediction",
    "DEFAULT_TABOR_COEFFICIENT_SIGMA_UTS",
    "DEFAULT_TABOR_COEFFICIENT_SIGMA_Y",
    "DEFAULT_H_GAMMA_GPA",
    "EMPIRICAL_WORK_HARDENING_RATIO_BY_CR",
    # Phase 3.8a — through-thickness mixture model
    "predict_zone_sigma_y",
    "predict_bulk_sigma_y_through_thickness",
    "through_thickness_sweep",
    "microstructure_at_zone",
    "zone_volume_fraction",
    "interpolate_at_depth",
    "ZONE_LABELS",
    "PLATE_THICKNESS_UM_BY_CR",
    "ZonePrediction",
]
