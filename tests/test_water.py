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

"""Agua: consistencia IAPWS, Wagner, Clausius-Clapeyron y clasificacion."""
import pytest

from phasemap.models import water as w


def test_triple_point_consistency():
    assert w.p_subl(w.Tt) == pytest.approx(w.Pt, rel=1e-9)
    assert w.p_melt_Ih(w.Tt) == pytest.approx(w.Pt, rel=1e-9)
    assert w.p_vap(w.Tt) == pytest.approx(w.Pt, rel=1e-3)

def test_critical_point():
    assert w.p_vap(w.Tc) == pytest.approx(w.Pc, rel=1e-12)

def test_normal_boiling_point():
    assert w.boiling_temperature(101325.0) == pytest.approx(373.124, abs=0.05)

def test_sublimation_minus20C():
    assert w.p_subl(253.15) == pytest.approx(103.2, abs=1.5)

def test_melt_Ih_negative_slope():
    slope = (w.p_melt_Ih(273.15) - w.Pt) / (273.15 - w.Tt)
    assert slope == pytest.approx(-13.5e6, rel=0.02)

def test_clausius_clapeyron_latent_heat():
    """L_est con vapor ideal: +1.6% sobre 40.657 kJ/mol (Z_vap ~ 0.984). Declarado."""
    L = w.clausius_latent(373.15) / 1000.0
    assert L == pytest.approx(40.657, rel=0.03)

def test_ice_VII_vs_datchi_fit():
    """Nuestro anclaje vs el ajuste publicado P=2.17+1.253[(T/354.8)^3-1] GPa."""
    for T in (450.0, 550.0, 650.0, 750.0):
        datchi = 2.17e9 + 1.253e9 * ((T / 354.8) ** 3 - 1.0)
        assert w.p_melt_VII(T) == pytest.approx(datchi, rel=0.05)
    assert w.p_melt_VII(751.5) == pytest.approx(13.09e9, rel=1e-6)

@pytest.mark.parametrize("T,P,expected", [
    (300.0, 1e5, "liquido"), (263.0, 1e5, "hielo Ih"),
    (700.0, 30e6, "fluido supercritico"), (300.0, 2e9, "hielo VI"),
    (253.0, 180e6, "hielo Ih"), (253.0, 230e6, "liquido"),
    (270.0, 100e6, "liquido"), (560.0, 9e9, "hielo VII"),
    (480.0, 1e3, "vapor"), (240.0, 1e4, "hielo Ih"),
])
def test_classify(T, P, expected):
    assert w.classify(T, P) == expected

def test_saturation_boundary_crossing():
    T = 400.0
    ps = w.p_vap(T)
    assert w.classify(T, ps * 1.01) == "liquido"
    assert w.classify(T, ps * 0.99) == "vapor"

def test_triple_points_table():
    tp = w.triple_points()
    assert len(tp) == 5
    assert tp[0] == ("Ih-liquido-vapor", w.Tt, w.Pt)
