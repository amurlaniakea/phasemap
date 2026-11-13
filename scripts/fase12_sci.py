#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 12 cientifica: RK dependiente de T (CALPHAD/SGTE) + referencias assessed + assessment.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)

# 1) RegularPhase: L0(T)=L0+L0T*T, L1(T)=L1+L1T*T (retrocompatible, L0T=L1T=0 por defecto)
P = "src/phasemap/models/regular.py"; s = read(P)
s = s.replace("dHfA=0.0, TmA=math.inf, dHfB=0.0, TmB=math.inf):",
              "dHfA=0.0, TmA=math.inf, dHfB=0.0, TmB=math.inf, L0T=0.0, L1T=0.0):")
s = s.replace("self.dHfB, self.TmB = float(dHfB), float(TmB)",
              "self.dHfB, self.TmB = float(dHfB), float(TmB)\n        self.L0T, self.L1T = float(L0T), float(L1T)")
s = s.replace("+ x * (1.0 - x) * (self.L0 + self.L1 * (2.0 * x - 1.0)))",
              "+ x * (1.0 - x) * ((self.L0 + self.L0T * T) + (self.L1 + self.L1T * T) * (2.0 * x - 1.0)))")
s = s.replace("+ (1.0 - 2.0 * x) * (self.L0 + self.L1 * (2.0 * x - 1.0))\n                + 2.0 * self.L1 * x * (1.0 - x))",
              "+ (1.0 - 2.0 * x) * ((self.L0 + self.L0T * T) + (self.L1 + self.L1T * T) * (2.0 * x - 1.0))\n                + 2.0 * (self.L1 + self.L1T * T) * x * (1.0 - x))")
s = s.replace("return R * T / (xm * (1.0 - xm)) - 2.0 * self.L0 + 6.0 * self.L1 * (1.0 - 2.0 * x)",
              "return R * T / (xm * (1.0 - xm)) - 2.0 * (self.L0 + self.L0T * T) + 6.0 * (self.L1 + self.L1T * T) * (1.0 - 2.0 * x)")
write(P, s); print("OK: RegularPhase con L0T/L1T (RK dependiente de T)")

# 2) referencias assessed (valores experimentales evaluados tipo CALPHAD/SGTE, con citas)
write("src/phasemap/systems/references.py", '''"""Fase 12: puntos invariantes assessed (evaluados tipo CALPHAD/SGTE) con citas.

Estos son los valores de referencia experimentales/evaluados contra los que se
contrasta el modelo. Fuentes: Massalski (ASM), IAPWS, Datchi et al. (2000).
"""
ASSESSED = {
    "pbsn": {"eutectic_T_K": 456.15, "eutectic_x": 0.739,
             "src": "Massalski, Binary Alloy Phase Diagrams (ASM): 183 C, 61.9 wt% Sn"},
    "agcu": {"eutectic_T_K": 1052.0, "eutectic_x": 0.399,
             "src": "ASM: 779 C, 28.1 wt% Cu"},
    "alsi": {"eutectic_T_K": 850.0, "eutectic_x": 0.122,
             "src": "ASM: 577 C, 12.6 wt% Si"},
    "fec":  {"peritectic_T_K": 1768.0, "eutectic_T_K": 1421.0, "eutectoid_T_K": 1000.0,
             "src": "ASM (Fe-Fe3C metaestable): 1495 C, 1148 C, 727 C"},
    "cuni": {"Tm_A_K": 1357.77, "Tm_B_K": 1728.3, "src": "ASM: isomorfo"},
    "water": {"triple_T_K": 273.16, "triple_P_Pa": 611.657,
              "critical_T_K": 647.096, "critical_P_Pa": 22.064e6, "src": "IAPWS R14-08 / Wagner"},
}
''')

# 3) informe de assessment sistematico
write("scripts/build_assessment.py", '''#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 12: contraste sistematico modelo vs referencias assessed -> data/assessment.csv + docs/assessment.md
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
from phasemap import PRESETS, scan_diagram
from phasemap.core.multiphase import scan_multi
from phasemap.systems.compounds import al_si, fe_c
from phasemap.systems.references import ASSESSED
from phasemap.models import water as w
DATA = os.path.join(ROOT, "data"); os.makedirs(DATA, exist_ok=True)
rows = []
def add(sysname, mag, model, ref, src):
    dev = abs(model - ref) / abs(ref) * 100.0 if ref else None
    rows.append([sysname, mag, f"{model:.4g}", f"{ref:.4g}" if ref else "-",
                 f"{dev:.2f}" if dev is not None else "-", src])
for key in ("pbsn", "agcu"):
    d = scan_diagram(PRESETS[key].system(), rows=300, n=320)
    if d.eutectic:
        a = ASSESSED[key]
        add(key, "eutectic_T_K", d.eutectic["T"], a["eutectic_T_K"], a["src"])
        add(key, "eutectic_x", d.eutectic["xE"], a["eutectic_x"], a["src"])
d = scan_multi(al_si(), 700, 1000, rows=200, n=300)
eut = [i for i in d["invariants"] if i["kind"] == "eutectico"]
if eut:
    add("alsi", "eutectic_T_K", eut[0]["T"], ASSESSED["alsi"]["eutectic_T_K"], ASSESSED["alsi"]["src"])
    add("alsi", "eutectic_x", eut[0]["x"], ASSESSED["alsi"]["eutectic_x"], ASSESSED["alsi"]["src"])
d = scan_multi(fe_c(), 900, 1900, rows=240, n=300)
per = [i for i in d["invariants"] if i["kind"] == "peritectico"]
sol = [i for i in d["invariants"] if i["kind"] == "solido"]
if per: add("fec", "peritectic_T_K", per[0]["T"], ASSESSED["fec"]["peritectic_T_K"], ASSESSED["fec"]["src"])
if sol: add("fec", "eutectoid_T_K", sol[0]["T"], ASSESSED["fec"]["eutectoid_T_K"], ASSESSED["fec"]["src"])
add("water", "triple_T_K", w.Tt, ASSESSED["water"]["triple_T_K"], ASSESSED["water"]["src"])
add("water", "critical_T_K", w.Tc, ASSESSED["water"]["critical_T_K"], ASSESSED["water"]["src"])
with open(os.path.join(DATA, "assessment.csv"), "w", newline="") as f:
    wr = csv.writer(f); wr.writerow(["system", "quantity", "model", "assessed", "dev_pct", "source"]); wr.writerows(rows)
md = ["# Assessment: modelo vs referencias assessed (CALPHAD/SGTE)", "",
      "| Sistema | Magnitud | Modelo | Assessed | Desv. % | Fuente |", "|---|---|---|---|---|---|"]
for r in rows: md.append("| " + " | ".join(r) + " |")
md += ["", "Los valores assessed son los puntos invariantes experimentales evaluados (Massalski/ASM, IAPWS).",
       "El modelo de solucion regular reproduce la topologia; las desviaciones cuantitativas se declaran.", ""]
open(os.path.join(ROOT, "docs", "assessment.md"), "w").write("\\n".join(md))
for r in rows: print(f"{r[0]:6s} {r[1]:16s} modelo={r[2]:>10s} assessed={r[3]:>10s} desv={r[4]}%")
print("Assessment: data/assessment.csv + docs/assessment.md")
''')

# 4) tests Fase 12
write("tests/test_fase12.py", '''# Fase 12: RK dependiente de T + referencias assessed.
import math
import pytest
from phasemap import RegularPhase
from phasemap.systems.references import ASSESSED

def test_L0T_derivatives():
    p = RegularPhase("s", L0=8000.0, L1=6000.0, L0T=-2.0, L1T=0.5)
    T, h = 480.0, 1e-6
    for x in (0.2, 0.5, 0.8):
        num = (p.G(x + h, T) - p.G(x - h, T)) / (2 * h)
        assert num == pytest.approx(p.dG(x, T), rel=1e-5, abs=1e-2)

def test_L0T_backward_compat():
    a = RegularPhase("s", L0=8000.0, L1=6000.0)
    b = RegularPhase("s", L0=8000.0, L1=6000.0, L0T=0.0, L1T=0.0)
    assert a.G(0.5, 480.0) == b.G(0.5, 480.0)

def test_references_present():
    for k in ("pbsn", "agcu", "alsi", "fec", "water"):
        assert k in ASSESSED and "src" in ASSESSED[k]
''')

# 5) version 0.4.0 + changelog
for rel, a, b in [("pyproject.toml", 'version = "0.3.1"', 'version = "0.4.0"'),
                  ("src/phasemap/__init__.py", '__version__ = "0.3.1"', '__version__ = "0.4.0"')]:
    t = read(rel)
    if a in t: write(rel, t.replace(a, b, 1))
ch = read("CHANGELOG.md")
if "v0.4.0" not in ch:
    e = ("## v0.4.0\n- Fase 12 cientifica: Redlich-Kister dependiente de T (L0T/L1T, forma G=a+bT de CALPHAD/SGTE). "
         "Modulo de referencias assessed (Massalski/ASM, IAPWS) e informe de assessment sistematico "
         "(data/assessment.csv + docs/assessment.md). Citacion Zenodo (CITATION.cff + .zenodo.json).\n\n")
    write("CHANGELOG.md", ch.replace("# Changelog\n", "# Changelog\n\n" + e, 1))
print("OK: Fase 12 cientifica aplicada (v0.4.0)")
