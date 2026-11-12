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

"""Barrido de diagramas: eutectico, lente isomorfa y fronteras."""
import pytest

from phasemap import PRESETS, scan_diagram


@pytest.fixture(scope="module")
def pbsn_diagram():
    return scan_diagram(PRESETS["pbsn"].system(), rows=200, n=240)

@pytest.fixture(scope="module")
def cuni_diagram():
    return scan_diagram(PRESETS["cuni"].system(), rows=160, n=220)

def test_pbsn_eutectic_exists(pbsn_diagram):
    e = pbsn_diagram.eutectic
    assert e is not None
    assert 400.0 < e["T"] < 480.0
    assert 0.60 < e["xE"] < 0.85
    assert e["xa"] < e["xE"] < e["xb"]

def test_pbsn_vs_experiment(pbsn_diagram):
    """Desviacion frente a Massalski (456.15 K, x=0.739): < 8% declarado."""
    e = pbsn_diagram.eutectic
    assert abs(e["T"] - 456.15) / 456.15 < 0.08
    assert abs(e["xE"] - 0.739) / 0.739 < 0.08

def test_cuni_isomorphous_no_eutectic(cuni_diagram):
    assert cuni_diagram.eutectic is None
    assert len(cuni_diagram.boundaries["liquidus"]) > 10
    assert len(cuni_diagram.boundaries["solidus"]) > 10

def test_liquidus_starts_at_pure_melting(pbsn_diagram):
    d = pbsn_diagram
    top_T = max(T for _, T in d.boundaries["liquidus"])
    assert top_T == pytest.approx(600.6, abs=2.5 * d.dT)

def test_solvus_below_eutectic(pbsn_diagram):
    d = pbsn_diagram
    assert all(T <= d.eutectic["T"] + d.dT for _, T in d.boundaries["solvus"])

def test_spinodal_dome_inside_gap(pbsn_diagram):
    d = pbsn_diagram
    assert len(d.spinodal_left) > 10
    for (xl, T), (xr, T2) in zip(d.spinodal_left, d.spinodal_right):
        assert 0.0 < xl < xr < 1.0 and T == T2
