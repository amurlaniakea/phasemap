"""Fase 7: motor multifase (N fases) + compuestos estequiométricos + invariantes.

Generaliza el hull convexo a cualquier número de fases:
  - fases de solución (RegularPhase) muestreadas en malla,
  - compuestos de línea (LineCompound) como un único punto en x_c.
Detecta invariantes de 3 fases por colinealidad en el hull y los clasifica
en eutéctico (L interior) / peritéctico (L en un extremo) / sólido.
"""
import math
from .gibbs import R, clip, mix_entropy


class LineCompound:
    """Fase estequiométrica en x_c con G_c(T) = Hf - T*Sf (J/mol)."""
    def __init__(self, label, xc, Hf=0.0, Sf=0.0):
        self.label = label
        self.xc = float(xc)
        self.Hf = float(Hf)
        self.Sf = float(Sf)

    def Gc(self, T):
        return self.Hf - T * self.Sf

    def sample(self, T, n):
        return [(self.xc, self.Gc(T))]


def sample_phase(ph, T, n):
    if hasattr(ph, "sample"):
        return ph.sample(T, n)
    return [(i / n, ph.G(i / n, T)) for i in range(n + 1)]


def _hull(pts):
    h = []
    for p in pts:
        while len(h) >= 2:
            o, a = h[-2], h[-1]
            if (a[0]-o[0])*(p[1]-o[1]) - (a[1]-o[1])*(p[0]-o[0]) <= 0:
                h.pop()
            else:
                break
        h.append(p)
    return h


def equilibrium_multi(phases, T, n=400):
    """Partición de [0,1] en regiones monofásicas / cuerdas bifásicas a T."""
    best = {}
    for k, ph in enumerate(phases):
        for (x, g) in sample_phase(ph, T, n):
            if x not in best or g < best[x][1]:
                best[x] = (x, g, k)
    H = _hull([best[x] for x in sorted(best)])
    dx = 1.0 / n
    raw = []
    for a, b in zip(H, H[1:]):
        if b[0]-a[0] < 1e-12:
            continue
        raw.append([a[0], b[0], a[2], b[2], (b[0]-a[0] > 2.5*dx) or (a[2] != b[2])])
    segs = []
    for s in raw:
        if not s[4] and segs and not segs[-1][4] and segs[-1][2] == s[2]:
            segs[-1][1] = s[1]
        else:
            segs.append(s)
    for s in segs:
        s.append(phases[s[2]].label if not s[4]
                 else phases[s[2]].label + "+" + phases[s[3]].label)
    return segs, H


def find_invariants(phases, T, n=400, tol=1e-7):
    """Tres vértices de fases distintas colineales en el hull => invariante."""
    segs, H = equilibrium_multi(phases, T, n)
    out = []
    for a, b, c in zip(H, H[1:], H[2:]):
        if len({a[2], b[2], c[2]}) < 3:
            continue
        cross = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])
        scale = max(1.0, abs(c[1]-a[1])) * (c[0]-a[0])
        if abs(cross) < tol * scale:
            la, lb, lc = phases[a[2]].label, phases[b[2]].label, phases[c[2]].label
            if lb == "L":
                kind = "eutectico"
            elif "L" in (la, lc):
                kind = "peritectico"
            else:
                kind = "solido"
            out.append({"T": T, "kind": kind, "phases": (la, lb, lc),
                        "x0": a[0], "x1": c[0]})
    return out


def scan_multi(phases, Tmin, Tmax, rows=240, n=400):
    dT = (Tmax - Tmin) / (rows - 1)
    inv, rows_out = [], []
    for r in range(rows):
        T = Tmax - r * dT
        segs, H = equilibrium_multi(phases, T, n)
        rows_out.append((T, segs))
        for iv in find_invariants(phases, T, n):
            if not inv or iv["phases"] != inv[-1]["phases"] or abs(iv["T"]-inv[-1]["T"]) > 3*dT:
                inv.append(iv)
    return {"rows": rows_out, "invariants": inv, "Tmin": Tmin, "Tmax": Tmax}
