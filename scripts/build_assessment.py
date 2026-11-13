#!/usr/bin/env python3
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
open(os.path.join(ROOT, "docs", "assessment.md"), "w").write("\n".join(md))
for r in rows: print(f"{r[0]:6s} {r[1]:16s} modelo={r[2]:>10s} assessed={r[3]:>10s} desv={r[4]}%")
print("Assessment: data/assessment.csv + docs/assessment.md")
