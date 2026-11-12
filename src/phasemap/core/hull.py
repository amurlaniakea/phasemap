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
