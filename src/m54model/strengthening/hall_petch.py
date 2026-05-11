"""Hall-Petch grain-boundary strengthening."""

from m54model.constants import Convention, StrengtheningConstants


def sigma_hall_petch(
    block_width_um: float,
    constants: StrengtheningConstants | None = None,
) -> float:
    """sigma_HP = K_HP * d^(-1/2), with d = martensite block width in micrometers.

    Default K_HP = 230 MPa·µm^(1/2) (Sun 2022 fit on M54). Switch to 300 (Wang/Zhu)
    via `StrengtheningConstants.from_convention(Convention.WANG)`.
    """
    c = constants or StrengtheningConstants.from_convention(Convention.SUN)
    if block_width_um <= 0:
        raise ValueError(f"block_width_um must be positive, got {block_width_um}")
    return c.K_HP_MPa_um_half * block_width_um**-0.5
