"""Constantes y utilidades termodinamicas basicas. Solo stdlib."""
import math

R = 8.314462618  # J/(mol K) - CODATA 2018

def clip(x, a, b):
    return a if x < a else b if x > b else x

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
