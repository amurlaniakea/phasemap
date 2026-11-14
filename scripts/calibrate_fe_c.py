#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Fase 14b: calibra Fe-C con exceso intersticial (L0=L1) en gamma/alpha.

Alotropia del Fe puro analitica: alpha<->gamma 1185 K, gamma<->delta 1667 K.
gamma/alpha: exceso 2L x^2(1-x) (intersticial, sin laguna en el lado Fe).
delta: exceso simetrico L0 (sin laguna por encima de 1667 K).
Fe3C: compuesto de linea; Hf/Sf controlan eutectico y eutectoide.
Filtra candidatos con comprobaciones de ensamblaje para no romper los tests.
Uso: python scripts/calibrate_fe_c.py [--quick]
"""
import os, re, sys, itertools
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
from phasemap.models.regular import RegularPhase
from phasemap.core.multiphase import LineCompound, equilibrium_multi

TARGET = (1768.0, 1421.0, 1000.0)   # peritectico, eutectico, eutectoide
XE = 0.034

def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)

def phases(Hf, Sf, Lg, La):
    return [
        RegularPhase("L", L0=-15000.0, dHfA=13810.0, TmA=1811.0, dHfB=0.0, TmB=4000.0),
        RegularPhase("delta", L0=20000.0, L1=0.0, dHfA=0.0, TmA=1811.0),
        RegularPhase("gamma", L0=Lg, L1=Lg, dHfA=-2000.0, TmA=1667.0),
        RegularPhase("alpha", L0=La, L1=La, dHfA=-4500.0, TmA=1360.0),
        LineCompound("Fe3C", 0.25, Hf=Hf, Sf=Sf),
    ]

def asm(ph, T, x=XE, n=240):
    segs, H = equilibrium_multi(ph, T, n)
    q = next((s for s in segs if s[0] <= x <= s[1]), segs[-1])
    return q[5]

def features(ph, rows, n):
    Tmin, Tmax = 900.0, 1900.0
    dT = (Tmax - Tmin) / (rows - 1)
    prevL = prevD = False
    Tp = Te = Teu = None
    for r in range(rows):
        T = Tmax - r * dT
        segs, H = equilibrium_multi(ph, T, n)
        L = any((not s[4]) and s[5] == "L" for s in segs)
        D = any((not s[4]) and s[5] == "delta" for s in segs)
        q = next((s for s in segs if s[0] <= XE <= s[1]), segs[-1]); A = q[5]
        if prevD and not D and L and Tp is None: Tp = T
        if prevL and not L and Te is None: Te = T
        if Teu is None and "alpha" in A and "L" not in A: Teu = T
        prevL, prevD = L, D
    return Tp, Te, Teu

def score(v):
    s = 0.0
    for got, ref in zip(v, TARGET):
        s += abs(got - ref) / ref if got else 1.0   # penaliza ausentes
    return s

quick = "--quick" in sys.argv
rows, n = (60, 140) if quick else (100, 200)
grid = list(itertools.product((-20000.0, -16000.0, -12000.0, -8000.0),
                              (-12.0, -6.0, 0.0),
                              (8000.0, 12000.0, 16000.0, 20000.0),
                              (40000.0, 80000.0, 120000.0)))
print("Calibrando Fe-C (intersticial): %d candidatos, rows=%d n=%d" % (len(grid), rows, n))
best = None; passing = 0
for Hf, Sf, Lg, La in grid:
    ph = phases(Hf, Sf, Lg, La)
    lo, hi = asm(ph, 900.0, n=160), asm(ph, 1300.0, n=160)
    if not ("alpha" in lo and "Fe3C" in lo and "gamma" not in lo and "gamma" in hi):
        continue
    passing += 1
    v = features(ph, rows, n)
    sc = score(v)
    if best is None or sc < best[0]:
        best = (sc, Hf, Sf, Lg, La, v)
        print("  mejor: err=%.3f  Tp=%s Te=%s Teu=%s" %
              (sc, *[round(x) if x else None for x in v]))
print("Candidatos que pasan el filtro de ensamblaje: %d/%d" % (passing, len(grid)))
if best is None:
    print("AVISO: ninguno paso el filtro. No se modifica nada. Prueba sin --quick.")
    sys.exit(1)
sc, Hf, Sf, Lg, La, _ = best
ph = phases(Hf, Sf, Lg, La)
fine = features(ph, 240, 320)
print("\nElegido: Fe3C Hf=%.0f Sf=%.1f | L0_gamma=%.0f L0_alpha=%.0f" % (Hf, Sf, Lg, La))
for name, got, ref in zip(("peritectico", "eutectico", "eutectoide"), fine, TARGET):
    if got: print("  %-12s %7.1f K  (real %.0f K, desv %.1f%%)" % (name, got, ref, abs(got-ref)/ref*100))
    else:   print("  %-12s no detectado" % name)

write("src/phasemap/systems/compounds.py", '''"""Fase 14b: Al-Si (estabilidad de red) y Fe-C calibrado (exceso intersticial).

Alotropia del Fe puro analitica: alpha<->gamma 1185 K, gamma<->delta 1667 K.
gamma/alpha usan exceso 2L x^2(1-x) (L0=L1), propio del C intersticial:
solubilidad limitada sin laguna simetrica en el lado rico en Fe.
Fe3C como compuesto de linea. Invariantes calibrados contra ASM.
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
        RegularPhase("delta", L0=20000.0, L1=0.0, dHfA=0.0, TmA=1811.0),
        RegularPhase("gamma", L0=__LG__, L1=__LG__, dHfA=-2000.0, TmA=1667.0),
        RegularPhase("alpha", L0=__LA__, L1=__LA__, dHfA=-4500.0, TmA=1360.0),
        LineCompound("Fe3C", 0.25, Hf=__HF__, Sf=__SF__),
    ]
'''.replace("__LG__", "%.1f" % Lg).replace("__LA__", "%.1f" % La)
   .replace("__HF__", "%.1f" % Hf).replace("__SF__", "%.1f" % Sf))
print("OK: compounds.py")

P = "web/multifase.html"; s = read(P)
NEW = ("fec:{name:'Fe–C',Tmin:900,Tmax:1900,ph:["
       "new Reg({label:'L',L0:-15000,dHfA:13810,TmA:1811,dHfB:0,TmB:4000}),"
       "new Reg({label:'δ',L0:20000,L1:0,dHfA:0,TmA:1811}),"
       "new Reg({label:'γ',L0:%g,L1:%g,dHfA:-2000,TmA:1667}),"
       "new Reg({label:'α',L0:%g,L1:%g,dHfA:-4500,TmA:1360}),"
       "new Line('Fe₃C',0.25,%g,%g)]}" % (Lg, Lg, La, La, Hf, Sf))
s2 = re.sub(r"fec:\{name:'Fe–C'.*?\]\}", NEW, s, count=1, flags=re.DOTALL)
if s2 != s: write(P, s2); print("OK: multifase.html (Tmin=900 K)")

write("tests/test_fase14.py", '''# Fase 14: alotropia del Fe puro (analitica) y region eutectoide.
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
''')
P = "tests/test_fase7.py"; t = read(P)
t = t.replace("assemblage(1100.0)", "assemblage(900.0)").replace("assemblage(1250.0)", "assemblage(1300.0)")
write(P, t)
print("OK: tests (alotropia garantizada + region eutectoide)")
