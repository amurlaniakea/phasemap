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
    d = scan_multi(fe_c(), 900.0, 1900.0, rows=160, n=240)
    sol = [i for i in d["invariants"] if i["kind"] == "solido"]
    assert sol
    assert any(900.0 < i["T"] < 1300.0 for i in sol)
