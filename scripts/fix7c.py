#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 7c: detector de invariantes por margen entre fases + presets + tests.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MP = os.path.join(ROOT, "src", "phasemap", "core", "multiphase.py")
src = open(MP, encoding="utf-8").read()
if "import itertools" not in src:
    src = src.replace("import math", "import math\nimport itertools", 1)
i = src.find("def scan_multi(")
assert i != -1
TAIL = '''def _seg_at(H, x):
    if x <= H[0][0]: return H[0], H[0]
    if x >= H[-1][0]: return H[-1], H[-1]
    for a, b in zip(H, H[1:]):
        if a[0] <= x <= b[0]: return a, b
    return H[-1], H[-1]


def _margin(phases, b, a, c, T, n):
    pts = sorted([(x, g, k) for k in (a, c) for (x, g) in sample_phase(phases[k], T, n)])
    best = {}
    for (x, g, k) in pts:
        if x not in best or g < best[x][1]: best[x] = (x, g, k)
    H = _hull([best[x] for x in sorted(best)])
    bm = None
    for (x, g) in sample_phase(phases[b], T, n):
        p, q = _seg_at(H, x)
        if p[2] == q[2] or not (p[0] < x < q[0]): continue
        t = (x - p[0]) / (q[0] - p[0]); m = g - (p[1] + t * (q[1] - p[1]))
        if bm is None or m < bm[0]: bm = (m, x)
    return bm


def scan_multi(phases, Tmin, Tmax, rows=240, n=400):
    dT = (Tmax - Tmin) / (rows - 1); inv = []; rows_out = []
    for r in range(rows):
        T = Tmax - r * dT
        segs, H = equilibrium_multi(phases, T, n)
        rows_out.append((T, segs))
    for b in range(len(phases)):
        for a, c in itertools.combinations([k for k in range(len(phases)) if k != b], 2):
            prev = None; prevT = None
            for (T, segs) in rows_out:
                bm = _margin(phases, b, a, c, T, n); m = bm[0] if bm else 1e9
                if prev is not None and (prev > 0) != (m > 0) and bm:
                    f = prev / (prev - m); Ti = prevT + f * (T - prevT)
                    la, lb, lc = _lab(phases[a]), _lab(phases[b]), _lab(phases[c])
                    kind = "eutectico" if lb == "L" else ("peritectico" if "L" in (la, lc) else "solido")
                    inv.append({"T": Ti, "kind": kind, "phases": tuple(sorted((la, lc))) + (lb,), "x": bm[1]})
                prev = m; prevT = T
    inv.sort(key=lambda d: -d["T"])
    out = []
    for iv in inv:
        if not out or iv["phases"] != out[-1]["phases"] or abs(iv["T"] - out[-1]["T"]) > 20:
            out.append(iv)
    return {"rows": rows_out, "invariants": out, "Tmin": Tmin, "Tmax": Tmax}
'''
open(MP, "w", encoding="utf-8").write(src[:i] + TAIL)

CP = os.path.join(ROOT, "src", "phasemap", "systems", "compounds.py")
open(CP, "w", encoding="utf-8").write('''"""Fase 7: sistemas con compuestos / alotropia (Al-Si, Fe-C). Aproximados."""
from ..models.regular import RegularPhase
from ..core.multiphase import LineCompound


def al_si():
    return [
        RegularPhase("L", L0=-16000.0, dHfA=10710.0, TmA=933.5, dHfB=50210.0, TmB=1687.0),
        RegularPhase("(Al)", L0=16000.0, L1=16000.0),
        LineCompound("(Si)", 1.0),
    ]


def fe_c():
    return [
        RegularPhase("L", L0=-15000.0, dHfA=13810.0, TmA=1811.0, dHfB=0.0, TmB=4000.0),
        RegularPhase("delta", L0=20000.0, L1=20000.0, dHfA=0.0, TmA=1811.0),
        RegularPhase("gamma", L0=12000.0, L1=12000.0, dHfA=-2000.0, TmA=1811.0),
        LineCompound("Fe3C", 0.25, Hf=-25000.0, Sf=-10.0),
    ]
''')

TP = os.path.join(ROOT, "tests", "test_fase7.py")
open(TP, "w", encoding="utf-8").write('''# Fase 7: compuesto de linea, clasificacion de invariantes, Fe-C peritectico.
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
''')
print("OK: Fase 7c aplicada (detector margen + presets + tests)")
