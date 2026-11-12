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

"""Presets binarios con datos de referencia (Massalski, ASM Handbook).

Pb-Sn: L0/L1/omL afinados por busqueda en malla (con L1 <= L0 para mantener
el exceso positivo en todo x) minimizando la desviacion frente al eutectico
experimental (456.15 K, x_Sn = 0.739). La desviacion residual se declara.
"""
from dataclasses import dataclass, field

from ..models.regular import BinarySystem, RegularPhase


@dataclass
class Preset:
    key: str
    name: str
    A: str
    B: str
    TmA: float
    TmB: float
    dHfA: float
    dHfB: float
    L0: float
    L1: float
    omL: float
    reference: dict = field(default_factory=dict)

    def system(self):
        solid = RegularPhase("solido", L0=self.L0, L1=self.L1)
        liquid = RegularPhase("liquido", L0=self.omL,
                              dHfA=self.dHfA, TmA=self.TmA,
                              dHfB=self.dHfB, TmB=self.TmB)
        return BinarySystem(self.name, solid, liquid, A=self.A, B=self.B)

PRESETS = {
    "pbsn": Preset(
        key="pbsn", name="Pb-Sn", A="Pb", B="Sn",
        TmA=600.6, TmB=505.1, dHfA=4770.0, dHfB=7030.0,
        L0=8000.0, L1=6000.0, omL=4000.0,
        reference={
            "Te_K": 456.15, "xE": 0.739, "solA": 0.293, "solB_Pb": 0.0145,
            "source": "Massalski, Binary Alloy Phase Diagrams (ASM): 183 C, 61.9 wt% Sn",
        }),
    "cuni": Preset(
        key="cuni", name="Cu-Ni", A="Cu", B="Ni",
        TmA=1357.8, TmB=1728.3, dHfA=13260.0, dHfB=17480.0,
        L0=2000.0, L1=0.0, omL=-800.0,
        reference={
            "TmA_K": 1357.77, "TmB_K": 1728.3,
            "source": "ASM: sistema isomorfo, solubilidad total en solido y liquido",
        }),
    "agcu": Preset(
        key="agcu", name="Ag-Cu", A="Ag", B="Cu",
        TmA=1234.9, TmB=1357.8, dHfA=11300.0, dHfB=13260.0,
        L0=16000.0, L1=0.0, omL=7000.0,
        reference={
            "Te_K": 1052.0, "xE": 0.399, "solA": 0.141, "solB_Pb": 0.049,
            "source": "ASM: eutectico 779 C, 28.1 wt% Cu",
        }),
    "generic": Preset(
        key="generic", name="Generico A-B", A="A", B="B",
        TmA=1000.0, TmB=700.0, dHfA=10000.0, dHfB=8500.0,
        L0=16000.0, L1=2000.0, omL=0.0,
        reference={"source": "Sistema didactico sin referencia experimental"}),
}
