"""Fase 7: sistemas con compuestos / alotropía (Al-Si, Fe-C).

Al-Si: líquido + (Al) fcc + (Si) diamante como compuesto de línea.
Fe-C: líquido + delta(bcc) + gamma(fcc) + Fe3C (cementita, línea).
Parámetros aproximados; desviaciones declaradas en data/limits.
El eutectoide sólido (gamma -> alpha+Fe3C) no se modela: Fase 8.
"""
from ..models.regular import RegularPhase
from ..core.multiphase import LineCompound


def al_si():
    return [
        RegularPhase("L", L0=2000.0, dHfA=10710.0, TmA=933.5,
                     dHfB=50210.0, TmB=1687.0),
        RegularPhase("(Al)", L0=16000.0),
        LineCompound("(Si)", 1.0),
    ]


def fe_c():
    return [
        RegularPhase("L", L0=-10000.0, dHfA=13810.0, TmA=1811.0,
                     dHfB=0.0, TmB=4000.0),
        RegularPhase("delta", L0=20000.0, dHfA=0.0, TmA=1811.0),
        RegularPhase("gamma", L0=12000.0, dHfA=-2000.0, TmA=1811.0),
        LineCompound("Fe3C", 0.25, Hf=-25000.0, Sf=-10.0),
    ]
