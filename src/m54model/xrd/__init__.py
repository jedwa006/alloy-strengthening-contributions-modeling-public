"""XRD peak fitting + phase quantification + lattice-parameter extraction.

Built for Cu-equivalent 2θ spectra of the user's M54 cw/cr samples.
Wired to the source workbooks via `m54model.calibration.data_loaders`.
"""

from m54model.xrd.analysis import (
    XRDAnalysisResult,
    analyze_all_cr_conditions,
    analyze_xrd_for_cr,
)
from m54model.xrd.bain import (
    BAIN_EPSILON_V_FE_NI_TEXTBOOK,
    BAIN_EPSILON_V_M54_XRD,
    bain_volumetric_strain,
    fcc_a0_from_bcc_bain_correspondence,
)
from m54model.xrd.peak_analysis import (
    LAMBDA_CU_KA1_A,
    PeakWindow,
    bcc_alpha_a0_from_peak,
    fcc_gamma_a0_from_peak,
    integrate_peak,
    lattice_parameter_from_2theta,
    modified_miller_V_gamma,
    nelson_riley_extrapolation,
)
from m54model.xrd.williamson_hall import (
    BURGERS_VECTOR_ALPHA_FE_M,
    DEFAULT_BETA_INST_DEG,
    K_ALPHA_BCC_SCREW,
    PeakBroadening,
    WHResult,
    analyze_williamson_hall_all_cr,
    analyze_williamson_hall_for_cr,
    dislocation_density_from_microstrain,
    estimate_fwhm_deg,
    wh_vs_gnd_for_all_cr,
    williamson_hall_regression,
)

__all__ = [
    "LAMBDA_CU_KA1_A",
    "PeakWindow",
    "bcc_alpha_a0_from_peak",
    "fcc_gamma_a0_from_peak",
    "integrate_peak",
    "lattice_parameter_from_2theta",
    "modified_miller_V_gamma",
    "nelson_riley_extrapolation",
    "BAIN_EPSILON_V_FE_NI_TEXTBOOK",
    "BAIN_EPSILON_V_M54_XRD",
    "bain_volumetric_strain",
    "fcc_a0_from_bcc_bain_correspondence",
    "XRDAnalysisResult",
    "analyze_xrd_for_cr",
    "analyze_all_cr_conditions",
    "BURGERS_VECTOR_ALPHA_FE_M",
    "DEFAULT_BETA_INST_DEG",
    "K_ALPHA_BCC_SCREW",
    "PeakBroadening",
    "WHResult",
    "analyze_williamson_hall_for_cr",
    "analyze_williamson_hall_all_cr",
    "dislocation_density_from_microstrain",
    "estimate_fwhm_deg",
    "wh_vs_gnd_for_all_cr",
    "williamson_hall_regression",
]
