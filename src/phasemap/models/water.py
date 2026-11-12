"""Agua P-T: Wagner (IAPWS-95 supp.), sublimacion y fusion Ih (IAPWS R14-08),
hielos III-VII por Simon-Glatzel anclado a puntos triples (aprox. declarada).

Referencias:
  - Wagner & Pruss (2002), J. Phys. Chem. Ref. Data 31, 387 (IAPWS-95).
  - IAPWS R14-08 (2011): melting & sublimation curves of ordinary water.
  - Datchi, Loubeyre & LeToullec (2000), Phys. Rev. B 61, 6535 (hielo VII).
  - Simon & Glatzel (1929) para la forma p = p0 + a[(T/T0)^c - 1].
"""
import math

R_WATER = 8.314462618
Tt, Pt = 273.16, 611.657          # punto triple
Tc, Pc = 647.096, 22.064e6        # punto critico
T_IhIII, P_IhIII = 251.165, 208.566e6
T_IIIV, P_IIIV = 256.164, 350.1e6
T_VVI, P_VVI = 273.31, 632.4e6
T_VIVII, P_VIVII = 355.0, 2216.0e6
T_MIN, T_MAX = 180.0, 800.0

def p_vap(T):
    """Presion de saturacion liquido-vapor (Wagner). Valida [Tt, Tc]. Pa."""
    if not (Tt <= T <= Tc):
        return None
    tau = 1.0 - T / Tc
    f = (-7.85951783 * tau + 1.84408259 * tau ** 1.5 - 11.7866497 * tau ** 3
         + 22.6807411 * tau ** 3.5 - 15.9618719 * tau ** 4 + 1.80122502 * tau ** 7.5)
    return Pc * math.exp(Tc / T * f)

def p_subl(T):
    """Presion de sublimacion hielo Ih-vapor (IAPWS R14-08). Valida [50, Tt]. Pa."""
    if not (50.0 <= T <= Tt):
        return None
    th = T / Tt
    f = (-21.2144006 * th ** (1.0 / 300.0) + 27.3203819 * th ** 1.20666667
         - 6.10598130 * th ** 1.70333333)
    return Pt * math.exp(Tt / T * f)

def p_melt_Ih(T):
    """Fusion hielo Ih (IAPWS R14-08, 3 terminos). Valida [251.165, 273.16]. Pa."""
    if not (T_IhIII <= T <= Tt):
        return None
    th = T / Tt
    f = (0.119539337e7 * (1.0 - th ** 3)
         + 0.808183159e5 * (1.0 - th ** 25.9376775)
         + 0.333826860e4 * (1.0 - th ** 103.259729))
    return Pt * (1.0 + f)

def _simon(T, T0, P0, T1, P1, c=3.0):
    a = (P1 - P0) / ((T1 / T0) ** c - 1.0)
    return P0 + a * ((T / T0) ** c - 1.0)

def p_melt_III(T):
    if not (T_IhIII <= T <= T_IIIV):
        return None
    return _simon(T, T_IhIII, P_IhIII, T_IIIV, P_IIIV)

def p_melt_V(T):
    if not (T_IIIV <= T <= T_VVI):
        return None
    return _simon(T, T_IIIV, P_IIIV, T_VVI, P_VVI)

def p_melt_VI(T):
    if not (T_VVI <= T <= T_VIVII):
        return None
    return _simon(T, T_VVI, P_VVI, T_VIVII, P_VIVII)

def p_melt_VII(T):
    """Simon-Glatzel (c=3) anclada al triple VI-VII-L de IAPWS (355 K, 2.216 GPa)
    y al punto experimental de Datchi et al., PRB 61, 6535 (2000): 751.5 K, 13.09 GPa.
    El ajuste publicado (a=1.253 GPa, T0=354.8 K) difiere <5% en todo el rango.
    Por encima de 751.5 K es extrapolacion declarada.
    """
    if not (T_VIVII <= T <= T_MAX):
        return None
    return _simon(T, T_VIVII, P_VIVII, 751.5, 13.09e9)

def classify(T, P):
    """Fase estable en (T, P). Fronteras solido-solido: verticales (aprox.)."""
    if T >= Tc and P >= Pc:
        return "fluido supercritico"
    ps = p_subl(T)
    if T < T_IhIII:
        return "hielo Ih" if (P > P_IhIII or (ps is not None and P > ps)) else "vapor"
    if T < T_IIIV:
        ice, pm = "hielo III", p_melt_III(T)
    elif T < T_VVI:
        ice, pm = "hielo V", p_melt_V(T)
    elif T < T_VIVII:
        ice, pm = "hielo VI", p_melt_VI(T)
    else:
        ice, pm = "hielo VII", p_melt_VII(T)
    if pm is not None and P > pm:
        return ice
    if T < Tt:
        pih = p_melt_Ih(T)
        if pih is not None and P > pih:
            return "liquido"
        return "hielo Ih" if (ps is not None and P > ps) else "vapor"
    if T < Tc:
        return "liquido" if P > p_vap(T) else "vapor"
    return "vapor"

def clausius_latent(T, h=0.02):
    """L_est = R T^2 d ln P/dT sobre la curva de saturacion (vapor ideal). J/mol."""
    p1, p2 = p_vap(T - h), p_vap(T + h)
    if p1 is None or p2 is None:
        return None
    return R_WATER * T * T * (math.log(p2) - math.log(p1)) / (2.0 * h)

def boiling_temperature(P=101325.0):
    """T de ebullicion a presion P (biseccion sobre Wagner). K."""
    a, b = Tt + 1e-6, Tc - 1e-6
    for _ in range(80):
        m = (a + b) / 2.0
        if p_vap(m) < P:
            a = m
        else:
            b = m
    return (a + b) / 2.0

def triple_points():
    return [
        ("Ih-liquido-vapor", Tt, Pt),
        ("Ih-III-liquido", T_IhIII, P_IhIII),
        ("III-V-liquido", T_IIIV, P_IIIV),
        ("V-VI-liquido", T_VVI, P_VVI),
        ("VI-VII-liquido", T_VIVII, P_VIVII),
    ]
