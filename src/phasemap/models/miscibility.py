"""Lacuna de miscibilidad en solucion regular simetrica (resultados analiticos).

T_c = Omega / (2R) ; espinodal: x(1-x) = RT/(2 Omega) ;
binodal: ln(x/(1-x)) + (Omega/RT)(1-2x) = 0 (biseccion, simetria x2 = 1-x1).
"""
import math
from ..core.gibbs import R
from .regular import RegularPhase

class MiscibilityGap:
    def __init__(self, omega):
        self.omega = float(omega)
        self.phase = RegularPhase("solido", L0=self.omega)

    @property
    def Tc(self):
        return self.omega / (2.0 * R)

    def spinodal(self, T):
        if T >= self.Tc:
            return None
        s = math.sqrt(1.0 - 2.0 * R * T / self.omega)
        return ((1.0 - s) / 2.0, (1.0 + s) / 2.0)

    def binodal(self, T):
        if T >= self.Tc:
            return None
        k = self.omega / (R * T)
        f = lambda x: math.log(x / (1.0 - x)) + k * (1.0 - 2.0 * x)
        a, b = 1e-12, 0.5 - 1e-12
        if f(b) <= 0.0:
            return None
        for _ in range(80):
            m = (a + b) / 2.0
            if f(m) < 0.0:
                a = m
            else:
                b = m
        x1 = (a + b) / 2.0
        return (x1, 1.0 - x1)

    def classify(self, T, x):
        if T >= self.Tc:
            return "estable"
        xb1, xb2 = self.binodal(T)
        if not (xb1 < x < xb2):
            return "estable"
        xs1, xs2 = self.spinodal(T)
        return "inestable" if xs1 < x < xs2 else "metaestable"

    def lever(self, T, x):
        """Fracciones (alpha, beta) sobre la binodal."""
        if T >= self.Tc:
            return [("alpha", x, 1.0)]
        xb1, xb2 = self.binodal(T)
        if not (xb1 < x < xb2):
            return [("alpha", x, 1.0)]
        f = (xb2 - x) / (xb2 - xb1)
        return [("alpha", xb1, f), ("beta", xb2, 1.0 - f)]
