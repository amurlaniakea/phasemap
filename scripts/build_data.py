#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Pedro Sordo Martínez <amurlaniakea@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Pedro Sordo Martínez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

"""Fase 4 - datos y limites: CSV de fronteras, curvas del agua e informe de error.

Uso: python scripts/build_data.py   (no requiere instalar el paquete)
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

from phasemap import PRESETS, MiscibilityGap, R, scan_diagram
from phasemap.models import water as w

DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
os.makedirs(DATA, exist_ok=True)
os.makedirs(DOCS, exist_ok=True)

def boundary_cells(segs):
    m = {}
    for a, b in zip(segs, segs[1:]):
        m[a.label + "|" + b.label] = a.x1
    def g(*keys):
        for k in keys:
            if k in m:
                return f"{m[k]:.5f}"
        return ""
    return [g("alpha|alpha+beta"), g("alpha|alpha+L"), g("alpha+L|L"),
            g("L|L+beta", "L|alpha+L"), g("L+beta|beta", "alpha+L|alpha"),
            g("alpha+beta|beta")]

HEADER = ["T_K", "x_solvus_alpha", "x_solidus_alpha", "x_liquidus_alpha",
          "x_liquidus_beta", "x_solidus_beta", "x_solvus_beta"]

limits = []

def add_limit(sysname, mag, model, ref, source="", tol_ok=5.0, tol_mid=20.0):
    if ref:
        dev = abs(model - ref) / abs(ref) * 100.0
        state = "OK" if dev < tol_ok else ("APROX" if dev < tol_mid else "DESVIADO")
        limits.append([sysname, mag, f"{model:.4g}", f"{ref:.4g}", f"{dev:.2f}", state, source])
    else:
        limits.append([sysname, mag, f"{model:.4g}", "-", "-", "MODELO", source])

for key, pr in PRESETS.items():
    d = scan_diagram(pr.system(), rows=300, n=320)
    path = os.path.join(DATA, f"binary_{key}_boundaries.csv")
    with open(path, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(HEADER)
        for T, segs in d.rows:
            wr.writerow([f"{T:.2f}"] + boundary_cells(segs))
    e = d.eutectic
    ref = pr.reference
    if e:
        print(f"{pr.name}: eutectico T={e['T']:.1f} K  xE={e['xE']:.3f}  -> {os.path.basename(path)}")
        add_limit(pr.name, "T_eutectica_K", e["T"], ref.get("Te_K"), source=ref.get("source", ""))
        add_limit(pr.name, "x_eutectica", e["xE"], ref.get("xE"), source=ref.get("source", ""))
        add_limit(pr.name, "solubilidad_max_B_en_alpha", e["xa"], ref.get("solA"), source=ref.get("source", ""))
        add_limit(pr.name, "solubilidad_max_A_en_beta", 1.0 - e["xb"], ref.get("solB_Pb"), source=ref.get("source", ""))
    else:
        print(f"{pr.name}: isomorfo (sin eutectico) -> {os.path.basename(path)}")
        limits.append([pr.name, "eutectico", "ausente", "ausente (isomorfo)", "0", "OK", ref.get("source", "")])
    if key == "cuni":
        add_limit(pr.name, "T_fusion_Cu_K", pr.TmA, ref["TmA_K"], source=ref["source"], tol_ok=0.1)
        add_limit(pr.name, "T_fusion_Ni_K", pr.TmB, ref["TmB_K"], source=ref["source"], tol_ok=0.1)

gap = MiscibilityGap(18000.0)
path = os.path.join(DATA, "miscibility_binodal_spinodal.csv")
with open(path, "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["T_K", "x_binodal_left", "x_binodal_right", "x_spinodal_left", "x_spinodal_right"])
    T = 150.0
    while T <= max(1500.0, 1.3 * gap.Tc):
        b, s = gap.binodal(T), gap.spinodal(T)
        cells = [f"{v:.5f}" for v in (b[0], b[1], s[0], s[1])] if b else ["", "", "", ""]
        wr.writerow([f"{T:.2f}"] + cells)
        T += 5.0
add_limit("Lacuna regular", "T_c_K", gap.Tc, 18000.0 / (2 * R), source="T_c = Omega/2R (analitico)", tol_ok=0.01)
print(f"Lacuna: Tc={gap.Tc:.1f} K -> {os.path.basename(path)}")

path = os.path.join(DATA, "water_pt_curves.csv")
with open(path, "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["T_K", "p_sublimation_Pa", "p_vaporization_Pa", "p_melt_Ih_Pa",
                 "p_melt_III_Pa", "p_melt_V_Pa", "p_melt_VI_Pa", "p_melt_VII_Pa"])
    T = 180.0
    while T <= 800.0:
        vals = [w.p_subl(T), w.p_vap(T), w.p_melt_Ih(T), w.p_melt_III(T),
                w.p_melt_V(T), w.p_melt_VI(T), w.p_melt_VII(T)]
        wr.writerow([f"{T:.2f}"] + [("" if v is None else f"{v:.6e}") for v in vals])
        T += 2.0
L373 = w.clausius_latent(373.15) / 1000.0
add_limit("H2O", "L_vap_373K_kJ_mol", L373, 40.657,
          source="vapor ideal; Z_vap~0.984 explica el +1.6%", tol_ok=3.0)
add_limit("H2O", "T_ebullicion_1atm_K", w.boiling_temperature(), 373.124, source="Wagner/IAPWS", tol_ok=0.1)
add_limit("H2O", "p_vap_triple_Pa", w.p_vap(w.Tt), w.Pt, source="Wagner vs IAPWS R14-08", tol_ok=0.1)
add_limit("H2O", "p_fusion_VII_751K_GPa", w.p_melt_VII(751.5) / 1e9, 13.09,
          source="Datchi et al., PRB 61, 6535 (2000)", tol_ok=1.0)
print(f"Agua: L(373.15K)={L373:.2f} kJ/mol  T_ebul={w.boiling_temperature():.3f} K -> {os.path.basename(path)}")

with open(os.path.join(DATA, "limits_report.csv"), "w", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["sistema", "magnitud", "modelo", "referencia", "desviacion_pct", "estado", "fuente"])
    wr.writerows(limits)

refs = {
    "constants": {"R_J_mol_K": R, "H2O_triple": [w.Tt, w.Pt], "H2O_critical": [w.Tc, w.Pc]},
    "H2O_triple_points": [{"name": n, "T_K": T, "P_Pa": P} for n, T, P in w.triple_points()],
    "sources": [
        "Wagner & Pruss (2002), J. Phys. Chem. Ref. Data 31, 387 (IAPWS-95)",
        "IAPWS R14-08 (2011), melting & sublimation curves of ordinary water",
        "Datchi, Loubeyre & LeToullec (2000), Phys. Rev. B 61, 6535 (hielo VII)",
        "Massalski, Binary Alloy Phase Diagrams, ASM International (Pb-Sn, Cu-Ni)",
        "Bragg & Williams (1934); Redlich & Kister (1948); Simon & Glatzel (1929)",
    ],
}
with open(os.path.join(DATA, "references.json"), "w") as f:
    json.dump(refs, f, indent=2, ensure_ascii=False)

md = ["# Tabla de error y limites (generada por scripts/build_data.py)", "",
      "| Sistema | Magnitud | Modelo | Referencia | Desv. % | Estado | Fuente |",
      "|---|---|---|---|---|---|---|"]
for row in limits:
    md.append("| " + " | ".join(str(c) for c in row) + " |")
md += ["", "## Supuestos del modelo", "",
       "- Solucion regular con Omega independientes de T (sin entropia de exceso).",
       "- Una unica red solida: alpha y beta son ramas de la misma fase; sin compuestos intermedios ni peritecticos.",
       "- P fija = 1 atm en binarios (regla de fases condensada F = C - P + 1).",
       "- Clausius-Clapeyron con vapor ideal y v_liquido despreciable: L_est sobrestima ~1.6% (Z_vap ~ 0.984 a 373 K).",
       "- Hielos III-VII: Simon-Glatzel c=3 anclada a puntos triples IAPWS; VII anclada tambien a Datchi (751.5 K, 13.09 GPa).",
       "- Fronteras solido-solido del agua: verticales en T del triple (aproximacion).",
       "- Hielos II, IX, XI, XII... no incluidos. CALPHAD multicomponente: fase futura.", ""]
with open(os.path.join(DOCS, "limits.md"), "w") as f:
    f.write("\n".join(md))
print("Informe: data/limits_report.csv + docs/limits.md + data/references.json")
