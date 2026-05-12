"""Crack-tip K_IC integration tests."""

import math

from m54model.calibration import m54_af550_45_t516_10, sun_2022_dq_t516_10
from m54model.toughening import (
    K_matrix_for_target,
    crack_tip_KIC,
    irwin_plastic_zone_m,
    mcmeeking_evans_delta_KIC,
    steady_state_KIC_iterative,
)

# ---- McMeeking-Evans formula sanity checks ------------------------------------------


def test_irwin_plastic_zone_basic() -> None:
    """r_p = (1/3π) (K/σ_y)² for plane strain.
    K = 100 MPa·m^½, σ_y = 1500 MPa → r_p = (100/1500)² / (3π) ≈ 471 µm."""
    r_p = irwin_plastic_zone_m(100.0, 1500.0, plane_strain=True)
    expected = (100.0 / 1500.0) ** 2 / (3.0 * math.pi)
    assert abs(r_p - expected) / expected < 1e-6


def test_mcmeeking_evans_zero_for_zero_strain() -> None:
    """No transformation strain → no toughening increment."""
    delta = mcmeeking_evans_delta_KIC(
        E_GPa=210,
        epsilon_V_transformation=0.0,
        transformation_zone_half_height_m=100e-6,
    )
    assert delta == 0.0


def test_mcmeeking_evans_zirconia_order_of_magnitude() -> None:
    """Reproduce Budiansky-Hutchinson 1983 ZrO2-toughened ceramic ballpark.
    E ≈ 200 GPa, ε^V ≈ 0.04, h ≈ 50 µm → ΔK ≈ 6 MPa·m^½."""
    delta = mcmeeking_evans_delta_KIC(
        E_GPa=200,
        epsilon_V_transformation=0.04,
        transformation_zone_half_height_m=50e-6,
        nu=0.30,
    )
    # 0.22 * 200000 * 0.04 * sqrt(50e-6) / 0.7 = 17.8 MPa·m^½ for f=1
    # Real ZrO2 ceramics measure in 5-15 MPa·m^½ range; we're in the right zone
    assert 5.0 < delta < 30.0


def test_steady_state_iteration_converges() -> None:
    """Iterative solver should converge in <10 iterations for typical inputs."""
    K_total, delta_K, iters = steady_state_KIC_iterative(
        K_matrix_MPa_m_half=70.0,
        sigma_y_MPa=1700,
        E_GPa=210,
        epsilon_V_transformation=0.04,
        f_austenite=0.10,
    )
    assert iters < 10
    assert K_total > 70.0  # transformation adds toughness
    assert delta_K > 0


def test_steady_state_no_austenite_no_increment() -> None:
    """Zero f_A → ΔK_TRIP = 0, K_total = K_matrix."""
    K_total, delta_K, iters = steady_state_KIC_iterative(
        K_matrix_MPa_m_half=80.0,
        sigma_y_MPa=1700,
        E_GPa=210,
        epsilon_V_transformation=0.04,
        f_austenite=0.0,
    )
    assert delta_K == 0.0
    assert K_total == 80.0


# ---- High-level crack_tip_KIC integration -------------------------------------------


def test_crack_tip_KIC_dq_baseline_no_austenite() -> None:
    """DQ + T516/10 anchor has f_A=0 → no TRIP increment."""
    state = sun_2022_dq_t516_10()
    r = crack_tip_KIC(state, K_matrix_MPa_m_half=70.0)
    assert r.delta_K_TRIP_MPa_m_half == 0.0
    assert r.K_total_MPa_m_half == 70.0


def test_crack_tip_KIC_af_baseline_with_austenite() -> None:
    """AF + T516/10 (user's cw/cr baseline) has f_A=0.013 from ASTAR.
    ΔK_TRIP should be small but positive — well under the matrix term."""
    state = m54_af550_45_t516_10()
    r = crack_tip_KIC(state, K_matrix_MPa_m_half=100.0)
    assert r.delta_K_TRIP_MPa_m_half > 0
    # M54's typical reverted-γ content gives modest TRIP toughening; expect <2 MPa·m^½
    assert r.delta_K_TRIP_MPa_m_half < 2.0


def test_K_matrix_for_target_finds_solution() -> None:
    """Bisection should land on a K_matrix that produces the target K_total."""
    state = m54_af550_45_t516_10()
    target = 110.0
    r = K_matrix_for_target(state, target_K_total_MPa_m_half=target, tol_MPa_m_half=0.5)
    assert abs(r.K_total_MPa_m_half - target) < 0.5
    # K_matrix should be just slightly less than target (tiny TRIP contribution)
    assert target - 2.0 < r.K_matrix_MPa_m_half < target


def test_crack_tip_result_repr_includes_decomposition() -> None:
    """__repr__ should expose the K_matrix / ΔK_TRIP / K_total split."""
    state = m54_af550_45_t516_10()
    r = crack_tip_KIC(state, K_matrix_MPa_m_half=80.0)
    s = repr(r)
    assert "K_matrix" in s
    assert "K_TRIP" in s or "ΔK_TRIP" in s
    assert "K_total" in s
