"""Fase 7: motor multifase (N fases) + compuestos estequiométricos + invariantes.

Generaliza el hull convexo a cualquier número de fases:
  - fases de solución (RegularPhase) muestreadas en malla,
  - compuestos de línea (LineCompound) como un único punto en x_c.
Detecta invariantes de 3 fases:
  - find_invariants: colinealidad en el hull (casos exactos / tests),
  - scan_multi: rastreo de regiones (L desaparece => eutéctico;
    sólido nuevo con L presente => peritéctico), robusto entre isotermas.
"""
import math
import itertools
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


def _lab(ph):
    return getattr(ph, "label", None) or getattr(ph, "name", "?")


def sample_phase(ph, T, n):
    if hasattr(ph, "sample"):
        return ph.sample(T, n)
    return [(i / n, ph.G(i / n, T)) for i in range(n + 1)]


def _hull(pts):
    h = []
    for p in pts:
        while len(h) >= 2:
            o, a = h[-2], h[-1]
            # < 0 (no <=): conserva vértices colineales = invariantes de 3 fases
            if (a[0]-o[0])*(p[1]-o[1]) - (a[1]-o[1])*(p[0]-o[0]) < 0:
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
        s.append(_lab(phases[s[2]]) if not s[4]
                 else _lab(phases[s[2]]) + "+" + _lab(phases[s[3]]))
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
            la, lb, lc = _lab(phases[a[2]]), _lab(phases[b[2]]), _lab(phases[c[2]])
            if lb == "L":
                kind = "eutectico"
            elif "L" in (la, lc):
                kind = "peritectico"
            else:
                kind = "solido"
            out.append({"T": T, "kind": kind, "phases": (la, lb, lc),
                        "x0": a[0], "x1": c[0]})
    return out


def _seg_at(H, x):
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


def _present(phases, T, n):
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
