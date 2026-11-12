"""Equilibrio de fases: tangentes comunes (Newton 2x2), palanca y diagramas T-x.

Algoritmo:
  1. Muestreo de G(x) de cada fase en una malla comun.
  2. Envolvente convexa inferior (monotone chain) sobre la union de puntos.
  3. Fusion de aristas consecutivas de una misma fase en regiones monofasicas.
  4. Refinamiento de cada cuerda comun igualando mu_A y mu_B (Newton 2x2).
  5. Etiquetado alpha/beta por conectividad con los extremos puros.
"""
from dataclasses import dataclass, field
from .gibbs import R
from .hull import lower_hull

@dataclass
class Segment:
    x0: float
    x1: float
    p0: int
    p1: int
    tie: bool
    label: str = ""
    g0: float = 0.0
    g1: float = 0.0

@dataclass
class PhaseFraction:
    label: str
    x: float
    fraction: float

def refine_tie(phases, seg, T, iters=14, tol=1e-7):
    """Refina los extremos de una cuerda comun igualando mu_A y mu_B.

    F1 = muA_1(x1) - muA_2(x2) ; F2 = muB_1(x1) - muB_2(x2)
    J  = [[-x1 G1'', x2 G2''], [(1-x1) G1'', -(1-x2) G2'']]
    det(J) = G1'' G2'' (x1 - x2)
    """
    x1, x2 = seg.x0, seg.x1
    if x2 - x1 < 1e-6:
        return
    ph1, ph2 = phases[seg.p0], phases[seg.p1]
    for _ in range(iters):
        F1 = ph1.muA(x1, T) - ph2.muA(x2, T)
        F2 = ph1.muB(x1, T) - ph2.muB(x2, T)
        if abs(F1) + abs(F2) < tol:
            break
        g1, g2 = ph1.d2G(x1, T), ph2.d2G(x2, T)
        J11, J12 = -x1 * g1, x2 * g2
        J21, J22 = (1.0 - x1) * g1, -(1.0 - x2) * g2
        det = J11 * J22 - J12 * J21
        if abs(det) < 1e-12:
            break
        n1 = min(max(x1 + (-F1 * J22 + F2 * J12) / det, 1e-6), 1.0 - 1e-6)
        n2 = min(max(x2 + (-F2 * J11 + F1 * J21) / det, 1e-6), 1.0 - 1e-6)
        if not n2 > n1 + 1e-7:
            break
        x1, x2 = n1, n2
    seg.x0, seg.x1 = x1, x2

def equilibrium_at(system, T, n=320, dual=None):
    """Equilibrio a temperatura T. Devuelve la particion de [0,1] en regiones."""
    if dual is None:
        dual = system.dual
    best = {}
    for i in range(n + 1):
        x = i / n
        for k, ph in enumerate(system.phases):
            g = ph.G(x, T)
            if x not in best or g < best[x][1]:
                best[x] = (x, g, k)
    pts = [best[i / n] for i in range(n + 1)]
    hull = lower_hull(pts)
    dx = 1.0 / n
    raw = []
    for a, b in zip(hull, hull[1:]):
        if b[0] - a[0] < 1e-12:
            continue
        tie = (b[0] - a[0] > 2.5 * dx) or (a[2] != b[2])
        raw.append(Segment(a[0], b[0], a[2], b[2], tie))
    segs = []
    for s in raw:
        if (not s.tie and segs and not segs[-1].tie and segs[-1].p0 == s.p0):
            segs[-1].x1 = s.x1
        else:
            segs.append(s)
    for s in segs:
        if s.tie:
            continue
        if s.p0 == 1:
            s.label = "L"
        elif not dual:
            s.label = "alpha"
        else:
            s.label = "alpha" if s.x0 <= 1e-9 else ("beta" if s.x1 >= 1.0 - 1e-9 else "alpha")
    for i, s in enumerate(segs):
        if not s.tie:
            continue
        if s.p0 == 0 and s.p1 == 0:
            s.label = "alpha+beta"
        else:
            lab = None
            if i > 0 and not segs[i - 1].tie and segs[i - 1].p0 == 0:
                lab = segs[i - 1].label
            elif i + 1 < len(segs) and not segs[i + 1].tie and segs[i + 1].p0 == 0:
                lab = segs[i + 1].label
            if lab is None:
                lab = "alpha" if (s.x0 + s.x1) / 2.0 < 0.5 else "beta"
            s.label = lab + "+L" if s.p0 == 0 else "L+" + lab
        refine_tie(system.phases, s, T)
    for i, s in enumerate(segs):
        if s.tie:
            continue
        if i > 0 and segs[i - 1].tie and segs[i - 1].x1 <= s.x1:
            s.x0 = segs[i - 1].x1
        if i + 1 < len(segs) and segs[i + 1].tie and segs[i + 1].x0 >= s.x0:
            s.x1 = segs[i + 1].x0
    for s in segs:
        s.g0 = system.phases[s.p0].G(s.x0, T)
        s.g1 = system.phases[s.p1].G(s.x1, T)
    return segs

def lever(segs, x0):
    """Regla de la palanca: fracciones molares conservando la materia."""
    seg = next((s for s in segs if s.x0 <= x0 <= s.x1), segs[-1])
    if seg.tie:
        labs = seg.label.split("+")
        f0 = (seg.x1 - x0) / (seg.x1 - seg.x0)
        return [PhaseFraction(labs[0], seg.x0, f0),
                PhaseFraction(labs[1], seg.x1, 1.0 - f0)], seg
    return [PhaseFraction(seg.label, x0, 1.0)], seg

def tangent_residual(system, seg, T):
    """Residual de la tangente comun: max(|dmu_A|, |dmu_B|) en J/mol."""
    if not seg.tie:
        return 0.0
    p1, p2 = system.phases[seg.p0], system.phases[seg.p1]
    return max(abs(p1.muA(seg.x0, T) - p2.muA(seg.x1, T)),
               abs(p1.muB(seg.x0, T) - p2.muB(seg.x1, T)))

BCAT = {
    "alpha|alpha+L": "solidus", "alpha+L|alpha": "solidus",
    "L+beta|beta": "solidus", "beta|beta+L": "solidus", "L+alpha|alpha": "solidus",
    "alpha+L|L": "liquidus", "L|alpha+L": "liquidus",
    "L|L+beta": "liquidus", "L|L+alpha": "liquidus", "beta+L|L": "liquidus",
    "alpha|alpha+beta": "solvus", "alpha+beta|beta": "solvus",
}

@dataclass
class Diagram:
    system: object
    Tmin: float
    Tmax: float
    dT: float
    rows: list = field(default_factory=list)
    boundaries: dict = field(default_factory=dict)
    eutectic: object = None
    spinodal_left: list = field(default_factory=list)
    spinodal_right: list = field(default_factory=list)

def scan_diagram(system, Tmin=None, Tmax=None, rows=300, n=320):
    """Barrido de isotermas -> fronteras (liquidus/solidus/solvus) + eutectico."""
    liq = system.liquid
    if Tmin is None:
        Tmin = 0.55 * min(liq.TmA, liq.TmB)
    if Tmax is None:
        Tmax = 1.15 * max(liq.TmA, liq.TmB)
    dT = (Tmax - Tmin) / (rows - 1)
    dia = Diagram(system, Tmin, Tmax, dT,
                  boundaries={"liquidus": [], "solidus": [], "solvus": []})
    prev_L = None
    solid = system.solid
    for r in range(rows):
        T = Tmax - r * dT
        segs = equilibrium_at(system, T, n=n, dual=system.dual)
        dia.rows.append((T, segs))
        for a, b in zip(segs, segs[1:]):
            cat = BCAT.get(a.label + "|" + b.label)
            if cat:
                dia.boundaries[cat].append((a.x1, T))
        Lseg = next((s for s in segs if not s.tie and s.label == "L"), None)
        if prev_L is not None and Lseg is None and system.dual:
            ab = next((s for s in segs if s.tie and s.label == "alpha+beta"), None)
            dia.eutectic = {"T": T + dT / 2.0,
                            "xE": (prev_L.x0 + prev_L.x1) / 2.0,
                            "xa": ab.x0 if ab else 0.0,
                            "xb": ab.x1 if ab else 1.0}
        prev_L = Lseg
        pl = pr = None
        pg = solid.d2G(0.5 / n, T)
        for i in range(1, 200):
            x = i / 200.0
            g2 = solid.d2G(x, T)
            if pg > 0.0 and g2 <= 0.0:
                pl = x
            elif pg <= 0.0 and g2 > 0.0:
                pr = x
            pg = g2
        if pl is not None:
            dia.spinodal_left.append((pl, T))
        if pr is not None:
            dia.spinodal_right.append((pr, T))
    return dia
