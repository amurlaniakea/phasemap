# Fase 7: compuesto de linea, clasificacion de invariantes, Fe-C peritectico.
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


def test_al_si_si_compound_stable():
    # a baja T el compuesto (Si) debe estar en el hull (extremo B)
    segs, H = equilibrium_multi(al_si(), 750.0, n=300)
    assert 1.0 in [v[0] for v in H]


def test_fe_c_peritectic():
    d = scan_multi(fe_c(), 1300.0, 1900.0, rows=160, n=240)
    per = [i for i in d["invariants"] if i["kind"] == "peritectico"]
    assert per
    assert any(1600.0 < i["T"] < 1900.0 for i in per)
