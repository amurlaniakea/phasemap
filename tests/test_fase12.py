# Fase 12: RK dependiente de T + referencias assessed.
import math
import pytest
from phasemap import RegularPhase
from phasemap.systems.references import ASSESSED

def test_L0T_derivatives():
    p = RegularPhase("s", L0=8000.0, L1=6000.0, L0T=-2.0, L1T=0.5)
    T, h = 480.0, 1e-6
    for x in (0.2, 0.5, 0.8):
        num = (p.G(x + h, T) - p.G(x - h, T)) / (2 * h)
        assert num == pytest.approx(p.dG(x, T), rel=1e-5, abs=1e-2)

def test_L0T_backward_compat():
    a = RegularPhase("s", L0=8000.0, L1=6000.0)
    b = RegularPhase("s", L0=8000.0, L1=6000.0, L0T=0.0, L1T=0.0)
    assert a.G(0.5, 480.0) == b.G(0.5, 480.0)

def test_references_present():
    for k in ("pbsn", "agcu", "alsi", "fec", "water"):
        assert k in ASSESSED and "src" in ASSESSED[k]
