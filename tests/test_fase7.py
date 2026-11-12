# Fase 7: compuesto de línea, clasificación de invariantes y Al-Si / Fe-C.
import pytest
from phasemap.core.multiphase import (LineCompound, equilibrium_multi,
                                      find_invariants, scan_multi)
from phasemap.systems.compounds import al_si, fe_c


def test_line_compound_on_hull():
    ph = [LineCompound("A", 0.0), LineCompound("C", 0.5, Hf=-10000.0),
          LineCompound("B", 1.0)]
    segs, H = equilibrium_multi(ph, 300.0, n=100)
    xs = [v[0] for v in H]
    assert 0.5 in xs  # el compuesto estable aparece en el hull


def test_peritectic_classification():
    # L en un extremo, sólido interior => peritéctico (construido por garantía)
    ph = [LineCompound("L", 0.0), LineCompound("beta", 0.5), LineCompound("alpha", 1.0)]
    iv = find_invariants(ph, 1000.0, n=100)
    assert iv and iv[0]["kind"] == "peritectico"


def test_eutectic_classification():
    # L interior => eutéctico
    ph = [LineCompound("alpha", 0.0), LineCompound("L", 0.5), LineCompound("beta", 1.0)]
    iv = find_invariants(ph, 1000.0, n=100)
    assert iv and iv[0]["kind"] == "eutectico"


def test_al_si_eutectic():
    d = scan_multi(al_si(), 700.0, 1800.0, rows=160, n=300)
    eut = [i for i in d["invariants"] if i["kind"] == "eutectico"]
    assert eut
    T = eut[0]["T"]
    assert 700.0 < T < 1000.0


def test_fe_c_invariants():
    d = scan_multi(fe_c(), 1200.0, 2000.0, rows=160, n=300)
    assert len(d["invariants"]) >= 1
