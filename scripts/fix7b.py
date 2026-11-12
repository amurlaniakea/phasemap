#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 7b: reemplaza scan_multi por deteccion de invariantes via minimo de cross.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "src", "phasemap", "core", "multiphase.py")
src = open(P, encoding="utf-8").read()
i = src.find("def scan_multi(")
assert i != -1, "no se encontro scan_multi"
NEW = '''def scan_multi(phases, Tmin, Tmax, rows=240, n=400):
    dT = (Tmax - Tmin) / (rows - 1)
    rows_out = []
    sig = {}
    for r in range(rows):
        T = Tmax - r * dT
        segs, H = equilibrium_multi(phases, T, n)
        rows_out.append((T, segs))
        for a, b, c in zip(H, H[1:], H[2:]):
            if len({a[2], b[2], c[2]}) < 3:
                continue
            cross = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
            sig.setdefault((a[2], b[2], c[2]), []).append((T, abs(cross), a[0], c[0]))
    inv = []
    for key, vals in sig.items():
        if len(vals) < 3:
            continue
        crosses = [v[1] for v in vals]
        imin = min(range(len(vals)), key=lambda k: crosses[k])
        if max(crosses) > 0 and crosses[imin] < 0.05 * max(crosses):
            T, _, x0, x1 = vals[imin]
            la, lb, lc = (_lab(phases[key[0]]), _lab(phases[key[1]]), _lab(phases[key[2]]))
            kind = "eutectico" if lb == "L" else ("peritectico" if "L" in (la, lc) else "solido")
            inv.append({"T": T, "kind": kind, "phases": (la, lb, lc), "x0": x0, "x1": x1})
    inv.sort(key=lambda d: -d["T"])
    return {"rows": rows_out, "invariants": inv, "Tmin": Tmin, "Tmax": Tmax}
'''
open(P, "w", encoding="utf-8").write(src[:i] + NEW)
print("OK: scan_multi reemplazado (deteccion por minimo de cross)")
