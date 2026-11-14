"""Fase 14c: Al-Si (estabilidad de red) y Fe-C calibrado (seccion Fe-Fe3C).

Alotropia del Fe puro analitica: alpha<->gamma 1185 K, gamma<->delta 1667 K.
gamma/alpha usan exceso 2L x^2(1-x) (L0=L1), propio del C intersticial.
El diagrama metaestable se interpreta en la seccion Fe-Fe3C (x <= 0.25).
Invariantes calibrados contra ASM: 1768 / 1421 / 1000 K.
"""
from ..models.regular import RegularPhase
from ..core.multiphase import LineCompound


def al_si():
    return [
        RegularPhase("L", L0=-12000.0, dHfA=10710.0, TmA=933.5, dHfB=50210.0, TmB=1687.0),
        RegularPhase("(Al)", L0=8000.0, dHfB=30000.0, TmB=1e9),
        LineCompound("(Si)", 1.0),
    ]


def fe_c():
    return [
        RegularPhase("L", L0=-15000.0, dHfA=13810.0, TmA=1811.0, dHfB=0.0, TmB=4000.0),
        RegularPhase("delta", L0=20000.0, L1=0.0, dHfA=0.0, TmA=1811.0),
        RegularPhase("gamma", L0=9000.0, L1=9000.0, dHfA=-2000.0, TmA=1667.0),
        RegularPhase("alpha", L0=800000.0, L1=800000.0, dHfA=-4500.0, TmA=1360.0),
        LineCompound("Fe3C", 0.25, Hf=-24000.0, Sf=-16.0),
    ]
