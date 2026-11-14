#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 15: detector de invariantes por seccion en el nucleo + assessment Fe-C completo.
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)

# 1) añadir invariants_section al nucleo
P = "src/phasemap/core/multiphase.py"; s = read(P)
if "def invariants_section(" not in s:
    s += '''

def invariants_section(phases, Tmin, Tmax, xmax=0.25, xe=0.034, rows=260, n=340,
                       liquid="L", high_solid="delta", low_solid="alpha"):
    """Invariantes por cambio de ensamblaje en una seccion [0, xmax].

    Robusto frente a la resolucion de la malla (no depende de colinealidad):
      - peritectico: desaparece el solido de alta T con liquido presente,
      - eutectico: desaparece el liquido dentro de la seccion,
      - eutectoide: aparece el solido de baja T sin liquido en xe.
    Pensado para secciones con compuesto de linea (Fe-Fe3C, x <= 0.25).
    """
    dT = (Tmax - Tmin) / (rows - 1)
    prevL = prevD = False
    out = {}
    for r in range(rows):
        T = Tmax - r * dT
        segs, H = equilibrium_multi(phases, T, n)
        L = any((not s[4]) and s[5] == liquid and s[0] < xmax for s in segs)
        D = any((not s[4]) and s[5] == high_solid and s[0] < xmax for s in segs)
        q = next((s for s in segs if s[0] <= xe <= s[1]), segs[-1])
        A = q[5]
        if prevD and not D and L and "peritectico" not in out:
            out["peritectico"] = T
        if prevL and not L and "eutectico" not in out:
            out["eutectico"] = T
        if "eutectoide" not in out and low_solid in A and liquid not in A:
            out["eutectoide"] = T
        prevL, prevD = L, D
    return out
'''
    write(P, s); print("OK: invariants_section en el nucleo")

# 2) assessment: usar el detector de seccion para Fe-C
P = "scripts/build_assessment.py"; s = read(P)
i = s.find("d = scan_multi(fe_c()")
j = s.find('add("water", "triple_T_K"')
if i != -1 and j != -1 and j > i:
    NEW = '''from phasemap.core.multiphase import invariants_section
iv = invariants_section(fe_c(), 900.0, 1900.0, xmax=0.25, xe=0.034, rows=260, n=340)
for key, ref in (("peritectico", "peritectic_T_K"),
                 ("eutectico", "eutectic_T_K"),
                 ("eutectoide", "eutectoid_T_K")):
    if key in iv:
        add("fec", ref, iv[key], ASSESSED["fec"][ref], ASSESSED["fec"]["src"])
'''
    write(P, s[:i] + NEW + s[j:]); print("OK: assessment Fe-C con los tres invariantes")
else:
    print("AVISO: no se encontraron las anclas en build_assessment.py")

# 3) test del detector de seccion
write("tests/test_fase15.py", '''# Fase 15: invariantes del Fe-C por seccion Fe-Fe3C (detector robusto).
from phasemap.systems.compounds import fe_c
from phasemap.core.multiphase import invariants_section


def test_fe_c_three_invariants():
    iv = invariants_section(fe_c(), 900.0, 1900.0, rows=200, n=260)
    assert "peritectico" in iv and "eutectico" in iv and "eutectoide" in iv
    assert 1650.0 < iv["peritectico"] < 1800.0
    assert 1350.0 < iv["eutectico"] < 1550.0
    assert 1000.0 < iv["eutectoide"] < 1250.0
    assert iv["eutectoide"] < iv["eutectico"] < iv["peritectico"]
''')
print("OK: tests/test_fase15.py")
