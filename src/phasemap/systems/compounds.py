"""Fase 10: Al-Si (estabilidad de red = sublattice efectivo) y Fe-C con eutectoide.

Al-Si: el (Al) fcc lleva un termino lineal +dG_Si_fcc (Si fcc metaestable frente
al diamante), equivalente a un sublattice (Al,Si)1(Va)3: suprime la rama rica en B
que competia con el (Si). Eutectico ~850 K / x_Si~0.11.
Fe-C: liquido + delta + gamma + alpha(ferrita) + Fe3C -> peritectico, eutectico y
eutectoide (gamma -> alpha + Fe3C). Parametros aproximados; desviaciones declaradas.
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
        RegularPhase("delta", L0=20000.0, L1=20000.0, dHfA=0.0, TmA=1811.0),
        RegularPhase("gamma", L0=12000.0, L1=12000.0, dHfA=-2000.0, TmA=1811.0),
        RegularPhase("alpha", L0=30000.0, L1=30000.0, dHfA=-4500.0, TmA=1400.0),
        LineCompound("Fe3C", 0.25, Hf=-25000.0, Sf=-10.0),
    ]
