"""Solucion regular de Bragg-Williams con un termino de Redlich-Kister.

G(x,T) = (1-x) gA(T) + x gB(T) + RT [x ln x + (1-x) ln(1-x)]
         + x(1-x) [L0 + L1 (2x-1)]

con g_i(T) = dHf_i (1 - T/Tm_i) para la fase liquida (referencia: solido puro).
Magnitudes en J/mol y K. Derivadas analiticas verificadas en tests.
"""
import math
from ..core.gibbs import R, clip, mix_entropy, mu_a, mu_b

class RegularPhase:
    def __init__(self, name, L0=0.0, L1=0.0,
                 dHfA=0.0, TmA=math.inf, dHfB=0.0, TmB=math.inf):
        self.name = name
        self.L0 = float(L0)
        self.L1 = float(L1)
        self.dHfA, self.TmA = float(dHfA), float(TmA)
        self.dHfB, self.TmB = float(dHfB), float(TmB)

    def _pure(self, T):
        gA = self.dHfA * (1.0 - T / self.TmA) if math.isfinite(self.TmA) else 0.0
        gB = self.dHfB * (1.0 - T / self.TmB) if math.isfinite(self.TmB) else 0.0
        return gA, gB

    def G(self, x, T):
        gA, gB = self._pure(T)
        return ((1.0 - x) * gA + x * gB + R * T * mix_entropy(x)
                + x * (1.0 - x) * (self.L0 + self.L1 * (2.0 * x - 1.0)))

    def dG(self, x, T):
        gA, gB = self._pure(T)
        xm = clip(x, 1e-9, 1.0 - 1e-9)
        return (gB - gA + R * T * math.log(xm / (1.0 - xm))
                + (1.0 - 2.0 * x) * (self.L0 + self.L1 * (2.0 * x - 1.0))
                + 2.0 * self.L1 * x * (1.0 - x))

    def d2G(self, x, T):
        xm = clip(x, 1e-9, 1.0 - 1e-9)
        return R * T / (xm * (1.0 - xm)) - 2.0 * self.L0 + 6.0 * self.L1 * (1.0 - 2.0 * x)

    def muA(self, x, T):
        return mu_a(self.G(x, T), self.dG(x, T), x)

    def muB(self, x, T):
        return mu_b(self.G(x, T), self.dG(x, T), x)

class BinarySystem:
    """Sistema binario A-B con dos fases: solido (indice 0) y liquido (indice 1).

    El solido usa una unica red con laguna de miscibilidad (modelo efectivo
    de 3 fases: L, alpha, beta). Sin compuestos intermedios ni peritecticos:
    limite declarado en docs/limits.md.
    """
    def __init__(self, name, solid, liquid, A="A", B="B"):
        self.name = name
        self.phases = [solid, liquid]
        self.A, self.B = A, B
        tmin = 0.55 * min(liquid.TmA, liquid.TmB)
        self.dual = solid.L0 > 2.0 * R * tmin

    @property
    def solid(self):
        return self.phases[0]

    @property
    def liquid(self):
        return self.phases[1]
