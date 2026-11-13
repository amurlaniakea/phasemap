# Fase 7/10: compuesto de linea, clasificacion, Al-Si eutectico y Fe-C eutectoide.
import pytest
from phasemap.core.multiphase import (LineCompound, equilibrium_multi,
                                      find_invariants, scan_multi)
from phasemap.systems.compounds import al_si, fe_c


def test_line_compound_on_hull():
    ph = [LineCompound("A", 0.0), LineCompound("C", 0.5, Hf=-10000.0), LineCompound("B", 1.0)]
    segs, H = equilibrium_multi(ph, 300.0, n=100)
    assert 0.5 in [v[0] for v in H]


def test_peritectic_classification():
    ph = [LineCompound("L", 0.0), LineCompound("beta", 0.5), LineCompound("alpha", 1.0)]
    iv = find_invariants(ph, 1000.0, n=100)
    assert iv and iv[0]["kind"] == "peritectico"


def test_eutectic_classification():
    ph = [LineCompound("alpha", 0.0), LineCompound("L", 0.5), LineCompound("beta", 1.0)]
    iv = find_invariants(ph, 1000.0, n=100)
    assert iv and iv[0]["kind"] == "eutectico"


def test_al_si_eutectic():
    d = scan_multi(al_si(), 700.0, 1000.0, rows=160, n=240)
    eut = [i for i in d["invariants"] if i["kind"] == "eutectico"]
    assert eut
    assert 800.0 < eut[0]["T"] < 900.0


def test_fe_c_eutectoid():
    # Eutectoide gamma -> alpha + Fe3C: comprobacion directa del ensamblaje (robusta,
    # independiente de la resolucion del detector de invariantes).
    from phasemap.core.multiphase import equilibrium_multi
    ph = fe_c()
    x = 0.03
    def assemblage(T):
        segs, H = equilibrium_multi(ph, T, n=240)
        q = next((s for s in segs if s[0] <= x <= s[1]), segs[-1])
        return q[5]
    low = assemblage(1100.0)    # por debajo del eutectoide
    high = assemblage(1250.0)   # por encima del eutectoide
    assert "alpha" in low and "Fe3C" in low and "gamma" not in low
    assert "gamma" in high
