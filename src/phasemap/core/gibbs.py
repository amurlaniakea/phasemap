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

"""Constantes y utilidades termodinamicas basicas. Solo stdlib."""
import math

R = 8.314462618  # J/(mol K) - CODATA 2018

def clip(x, a, b):
    return a if x < a else min(x, b)

def mix_entropy(x):
    """s_mix/R = x ln x + (1-x) ln(1-x), con proteccion en los extremos."""
    xm = clip(x, 1e-12, 1.0 - 1e-12)
    return xm * math.log(xm) + (1.0 - xm) * math.log(1.0 - xm)

def mu_a(g, dg, x):
    """Potencial quimico de A: mu_A = G - x dG/dx."""
    return g - x * dg

def mu_b(g, dg, x):
    """Potencial quimico de B: mu_B = G + (1-x) dG/dx."""
    return g + (1.0 - x) * dg

def phase_rule(components, phases, fixed_pressure=False):
    """Regla de fases de Gibbs. A P fija (condensada): F = C - P + 1."""
    return components - phases + (1 if fixed_pressure else 2)
