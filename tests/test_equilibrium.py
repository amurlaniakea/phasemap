"""Tangentes comunes, particion del eje, palanca y limites puros."""
import pytest
from phasemap import PRESETS, equilibrium_at, lever, tangent_residual

@pytest.fixture(scope="module")
def pbsn():
    return PRESETS["pbsn"].system()

@pytest.mark.parametrize("T", [350.0, 420.0, 480.0, 560.0])
def test_partition_covers_unit_interval(pbsn, T):
    segs = equilibrium_at(pbsn, T)
    assert segs[0].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[-1].x1 == pytest.approx(1.0, abs=1e-9)
    for a, b in zip(segs, segs[1:]):
        assert a.x1 == pytest.approx(b.x0, abs=1e-9)

@pytest.mark.parametrize("T", [350.0, 420.0, 480.0])
def test_common_tangent_residual(pbsn, T):
    for s in equilibrium_at(pbsn, T):
        if s.tie:
            assert tangent_residual(pbsn, s, T) < 1e-5

def test_lever_mass_balance(pbsn):
    T = 420.0
    segs = equilibrium_at(pbsn, T)
    for x0 in (0.05, 0.2, 0.35, 0.5, 0.65, 0.8, 0.97):
        fr, _ = lever(segs, x0)
        assert sum(f.fraction for f in fr) == pytest.approx(1.0, abs=1e-12)
        assert sum(f.fraction * f.x for f in fr) == pytest.approx(x0, abs=1e-9)
        assert all(0.0 <= f.fraction <= 1.0 for f in fr)

def test_all_liquid_above_liquidus(pbsn):
    segs = equilibrium_at(pbsn, 700.0)
    assert len(segs) == 1 and segs[0].label == "L"

def test_solid_terminals_below_eutectic(pbsn):
    segs = equilibrium_at(pbsn, 320.0)
    fr0, _ = lever(segs, 0.0)
    fr1, _ = lever(segs, 1.0)
    assert fr0[0].label == "alpha" and fr1[0].label == "beta"

def test_isomorphous_labels():
    cuni = PRESETS["cuni"].system()
    segs = equilibrium_at(cuni, 1500.0)
    labels = {s.label for s in segs}
    assert labels == {"L", "L+alpha", "alpha"}
