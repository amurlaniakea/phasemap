# Fase 14: alotropia del Fe puro (analitica) y region eutectoide.
from phasemap.systems.compounds import fe_c
from phasemap.core.multiphase import equilibrium_multi


def _cross(f, g, a=800.0, b=2000.0):
    for _ in range(80):
        m = (a + b) / 2.0
        if f(m) - g(m) < 0: a = m
        else: b = m
    return (a + b) / 2.0


def _solid(name):
    return next(p for p in fe_c() if getattr(p, "name", None) == name)


def test_alpha_gamma_allotropy():
    a, g = _solid("alpha"), _solid("gamma")
    T = _cross(lambda T: a.G(0.0, T), lambda T: g.G(0.0, T))
    assert 1150.0 < T < 1220.0


def test_gamma_delta_allotropy():
    g, d = _solid("gamma"), _solid("delta")
    T = _cross(lambda T: g.G(0.0, T), lambda T: d.G(0.0, T))
    assert 1640.0 < T < 1700.0


def test_eutectoid_region():
    ph = fe_c()
    def asm(T):
        segs, H = equilibrium_multi(ph, T, 240)
        q = next((s for s in segs if s[0] <= 0.034 <= s[1]), segs[-1])
        return q[5]
    low, high = asm(900.0), asm(1300.0)
    assert "alpha" in low and "Fe3C" in low and "gamma" not in low
    assert "gamma" in high
