#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Fase 7: exporta fronteras e invariantes de Al-Si y Fe-C a data/."""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
from phasemap.core.multiphase import scan_multi
from phasemap.systems.compounds import al_si, fe_c

DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)
summary = {}
for name, phases, Tmin, Tmax in [("al_si", al_si(), 700, 1800), ("fe_c", fe_c(), 1200, 2000)]:
    d = scan_multi(phases, Tmin, Tmax, rows=300, n=400)
    with open(os.path.join(DATA, f"fase7_{name}.csv"), "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["T_K", "regiones"])
        for T, segs in d["rows"]:
            wr.writerow([f"{T:.2f}", ";".join(f"{s[5]}[{s[0]:.3f},{s[1]:.3f}]" for s in segs)])
    summary[name] = d["invariants"]
    print(f"{name}: " + ", ".join(f"{i['kind']} {i['T']:.0f}K {i['phases']}" for i in d["invariants"]))
with open(os.path.join(DATA, "fase7_invariants.json"), "w") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print("Fase 7 datos: data/fase7_*.csv + data/fase7_invariants.json")
