"""Identidades termodinamicas basicas y derivadas analiticas."""
import pytest
from phasemap import RegularPhase, phase_rule

SOLID = RegularPhase("s", L0=9500.0, L1=3500.0)
LIQUID = RegularPhase("l", L0=800.0, dHfA=4770.0, TmA=600.6, dHfB=7030.0, TmB=505.1)

@pytest.mark.parametrize("ph", [SOLID, LIQUID])
@pytest.mark.parametrize("x", [0.07, 0.3, 0.5, 0.72, 0.95])
def test_first_derivative(ph, x):
    T, h = 480.0, 1e-6
    num = (ph.G(x + h, T) - ph.G(x - h, T)) / (2 * h)
    assert num == pytest.approx(ph.dG(x, T), rel=1e-6, abs=1e-3)

@pytest.mark.parametrize("ph", [SOLID, LIQUID])
@pytest.mark.parametrize("x", [0.13, 0.5, 0.87])
def test_second_derivative(ph, x):
    T, h = 480.0, 1e-5
    num = (ph.G(x + h, T) - 2 * ph.G(x, T) + ph.G(x - h, T)) / h ** 2
    assert num == pytest.approx(ph.d2G(x, T), rel=1e-4, abs=1e-2)

@pytest.mark.parametrize("ph", [SOLID, LIQUID])
def test_euler_identity(ph):
    """G = (1-x) mu_A + x mu_B (homogeneidad de primer orden)."""
    T = 500.0
    for x in (0.1, 0.4, 0.6, 0.9):
        assert ph.G(x, T) == pytest.approx(
            (1 - x) * ph.muA(x, T) + x * ph.muB(x, T), abs=1e-8)

def test_gibbs_duhem():
    """(1-x) dmu_A/dx + x dmu_B/dx = 0 a T constante."""
    T, h = 500.0, 1e-6
    for x in (0.2, 0.5, 0.8):
        dA = (SOLID.muA(x + h, T) - SOLID.muA(x - h, T)) / (2 * h)
        dB = (SOLID.muB(x + h, T) - SOLID.muB(x - h, T)) / (2 * h)
        assert (1 - x) * dA + x * dB == pytest.approx(0.0, abs=1e-3)

def test_phase_rule():
    assert phase_rule(2, 1, fixed_pressure=True) == 2
    assert phase_rule(2, 2, fixed_pressure=True) == 1
    assert phase_rule(2, 3, fixed_pressure=True) == 0
    assert phase_rule(1, 3) == 0
    assert phase_rule(1, 1) == 2
