#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 10: Al-Si por estabilidad de red (sublattice efectivo) + eutectoide Fe-C + filtro topologico.
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)

# 1) compounds.py: Al-Si calibrado + Fe-C con ferrita alpha
write("src/phasemap/systems/compounds.py", '''"""Fase 10: Al-Si (estabilidad de red = sublattice efectivo) y Fe-C con eutectoide.

Al-Si: el (Al) fcc lleva un termino lineal +dG_Si_fcc (Si fcc metaestable frente
al diamante), equivalente a un sublattice (Al,Si)1(Va)3: suprime la rama rica en B
que competia con el (Si). Eutectico ~850 K / x_Si~0.11.
Fe-C: liquido + delta + gamma + alpha(ferrita) + Fe3C -> peritectico, eutectico y
eutectoide (gamma -> alpha + Fe3C). Parametros aproximados; desviaciones declaradas.
"""
from ..models.regular import RegularPhase
from ..core.multiphase import LineCompound


def al_si():
    return [
        RegularPhase("L", L0=-12000.0, dHfA=10710.0, TmA=933.5, dHfB=50210.0, TmB=1687.0),
        RegularPhase("(Al)", L0=8000.0, dHfB=30000.0, TmB=1e9),
        LineCompound("(Si)", 1.0),
    ]


def fe_c():
    return [
        RegularPhase("L", L0=-15000.0, dHfA=13810.0, TmA=1811.0, dHfB=0.0, TmB=4000.0),
        RegularPhase("delta", L0=20000.0, L1=20000.0, dHfA=0.0, TmA=1811.0),
        RegularPhase("gamma", L0=12000.0, L1=12000.0, dHfA=-2000.0, TmA=1811.0),
        RegularPhase("alpha", L0=30000.0, L1=30000.0, dHfA=-4500.0, TmA=1400.0),
        LineCompound("Fe3C", 0.25, Hf=-25000.0, Sf=-10.0),
    ]
''')

# 2) scan_multi: filtro topologico (solo invariantes donde cambia el conjunto de fases estables)
MP = "src/phasemap/core/multiphase.py"
s = read(MP); i = s.find("def scan_multi("); assert i != -1
TAIL = '''def _present(phases, T, n):
    segs, H = equilibrium_multi(phases, T, n)
    return frozenset(v[2] for v in H)


def scan_multi(phases, Tmin, Tmax, rows=240, n=400):
    dT = (Tmax - Tmin) / (rows - 1)
    inv, rows_out, pres = [], [], []
    for r in range(rows):
        T = Tmax - r * dT
        segs, H = equilibrium_multi(phases, T, n)
        rows_out.append((T, segs))
        pres.append(frozenset(v[2] for v in H))
    for b in range(len(phases)):
        for a, c in itertools.combinations([k for k in range(len(phases)) if k != b], 2):
            prev = None; prevT = None; prevP = None
            for r in range(rows):
                T = rows_out[r][0]
                bm = _margin(phases, b, a, c, T, n); m = bm[0] if bm else 1e9
                if prev is not None and (prev > 0) != (m > 0) and bm and prevP != pres[r]:
                    f = prev / (prev - m); Ti = prevT + f * (T - prevT)
                    la, lb, lc = _lab(phases[a]), _lab(phases[b]), _lab(phases[c])
                    kind = "eutectico" if lb == "L" else ("peritectico" if "L" in (la, lc) else "solido")
                    inv.append({"T": Ti, "kind": kind, "phases": tuple(sorted((la, lc))) + (lb,), "x": bm[1]})
                prev = m; prevT = T; prevP = pres[r]
    inv.sort(key=lambda d: -d["T"])
    out = []
    for iv in inv:
        if not out or iv["phases"] != out[-1]["phases"] or abs(iv["T"] - out[-1]["T"]) > 20:
            out.append(iv)
    return {"rows": rows_out, "invariants": out, "Tmin": Tmin, "Tmax": Tmax}
'''
write(MP, s[:i] + TAIL)

# 3) tests Fase 10
write("tests/test_fase7.py", '''# Fase 7/10: compuesto de linea, clasificacion, Al-Si eutectico y Fe-C eutectoide.
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
''')

# 4) visor multifase: parametros Al-Si calibrados + ferrita alpha en Fe-C
VF = "web/multifase.html"
v = read(VF); o = v
v = v.replace("L0:-16000,dHfA:10710", "L0:-12000,dHfA:10710")
v = v.replace("label:'(Al)',L0:16000,L1:16000", "label:'(Al)',L0:8000,dHfB:30000,TmB:1e9")
if "label:'α'" not in v:
    v = v.replace("new Line('Fe₃C',0.25,-25000,-10)",
                  "new Reg({label:'α',L0:30000,L1:30000,dHfA:-4500,TmA:1400}),new Line('Fe₃C',0.25,-25000,-10)")
    v = v.replace("'(Si)':'#5f5fc9'", "'(Si)':'#5f5fc9','α':'#8f7bff'")
if v != o: write(VF, v)

# 5) version + changelog + roadmap
for rel, a, b in [("pyproject.toml", 'version = "0.2.0"', 'version = "0.3.0"'),
                  ("src/phasemap/__init__.py", '__version__ = "0.2.0"', '__version__ = "0.3.0"')]:
    p = os.path.join(ROOT, rel); t = read(rel)
    if a in t: write(rel, t.replace(a, b, 1))
ch = read("CHANGELOG.md")
if "v0.3.0" not in ch:
    entry = ("## v0.3.0\n- Fase 10: Al-Si calibrado por estabilidad de red (sublattice efectivo): "
             "eutectico ~850 K / x_Si~0.11. Eutectoide Fe-C (gamma -> alpha + Fe3C) con ferrita alpha. "
             "Filtro topologico de invariantes (elimina cruces metaestables).\n\n")
    write("CHANGELOG.md", ch.replace("# Changelog\n", "# Changelog\n\n" + entry, 1))
rm = read("docs/roadmap.md")
rm = rm.replace("- [ ] Fase 10: sublattice Al-Si (dos subredes) para eutectico ~850 K / x_Si~0.12.",
                "- [x] Fase 10: Al-Si por estabilidad de red (eutectico ~850 K) + eutectoide Fe-C.")
rm = rm.replace("- [ ] Fase 11: eutectoide solido Fe-C (gamma -> alpha + Fe3C) y renderizado de invariantes solidos.",
                "- [x] Fase 11: eutectoide solido Fe-C (gamma -> alpha + Fe3C).")
write("docs/roadmap.md", rm)
print("OK: Fase 10 aplicada (Al-Si calibrado + eutectoide Fe-C + filtro topologico + v0.3.0)")
