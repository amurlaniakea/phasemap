"""Envolvente convexa inferior (monotone chain) sobre curvas G(x) muestreadas."""

def lower_hull(points):
    """points: lista de tuplas (x, g, tag) ordenada por x ascendente.

    Devuelve los vertices de la envolvente convexa inferior. Cada tramo
    entre vertices consecutivos es una fase estable (curva) o una linea
    de reparto (cuerda comun entre dos fases).
    """
    hull = []
    for p in points:
        while len(hull) >= 2:
            o, a = hull[-2], hull[-1]
            cross = (a[0] - o[0]) * (p[1] - o[1]) - (a[1] - o[1]) * (p[0] - o[0])
            if cross <= 0.0:
                hull.pop()
            else:
                break
        hull.append(p)
    return hull
