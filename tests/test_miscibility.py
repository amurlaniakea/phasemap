"""Lacuna de miscibilidad: T_c, binodal, espinodal y zonas."""
import pytest
from phasemap import MiscibilityGap, R

@pytest.fixture(scope="module")
def gap():
    return MiscibilityGap(18000.0)

def test_critical_temperature(gap):
    assert gap.Tc == pytest.approx(18000.0 / (2 * R), rel=1e-12)

def test_binodal_equal_chemical_potentials(gap):
    for T in (400.0, 700.0, 900.0, 1050.0):
        x1, x2 = gap.binodal(T)
        assert gap.phase.muA(x1, T) == pytest.approx(gap.phase.muA(x2, T), abs=1e-6)
        assert gap.phase.muB(x1, T) == pytest.approx(gap.phase.muB(x2, T), abs=1e-6)

def test_spinodal_zero_curvature(gap):
    for T in (400.0, 800.0, 1000.0):
        x1, x2 = gap.spinodal(T)
        assert gap.phase.d2G(x1, T) == pytest.approx(0.0, abs=1e-6)
        assert gap.phase.d2G(x2, T) == pytest.approx(0.0, abs=1e-6)

def test_binodal_inside_spinodal_ordering(gap):
    for T in (500.0, 900.0):
        xb1, xb2 = gap.binodal(T)
        xs1, xs2 = gap.spinodal(T)
        assert xb1 < xs1 < xs2 < xb2

def test_symmetry(gap):
    x1, x2 = gap.binodal(750.0)
    assert x1 + x2 == pytest.approx(1.0, abs=1e-12)

def test_above_Tc_no_gap(gap):
    assert gap.binodal(gap.Tc + 1.0) is None
    assert gap.spinodal(gap.Tc + 1.0) is None
    assert gap.classify(gap.Tc + 1.0, 0.5) == "estable"

def test_zones(gap):
    T = 800.0
    assert gap.classify(T, 0.5) == "inestable"
    xb1, xs1 = gap.binodal(T)[0], gap.spinodal(T)[0]
    assert gap.classify(T, (xb1 + xs1) / 2) == "metaestable"
    assert gap.classify(T, 0.01) == "estable"

def test_lever(gap):
    fr = gap.lever(800.0, 0.4)
    assert sum(f[2] for f in fr) == pytest.approx(1.0, abs=1e-12)
    assert sum(f[2] * f[1] for f in fr) == pytest.approx(0.4, abs=1e-12)
