"""Fase 12: puntos invariantes assessed (evaluados tipo CALPHAD/SGTE) con citas.

Estos son los valores de referencia experimentales/evaluados contra los que se
contrasta el modelo. Fuentes: Massalski (ASM), IAPWS, Datchi et al. (2000).
"""
ASSESSED = {
    "pbsn": {"eutectic_T_K": 456.15, "eutectic_x": 0.739,
             "src": "Massalski, Binary Alloy Phase Diagrams (ASM): 183 C, 61.9 wt% Sn"},
    "agcu": {"eutectic_T_K": 1052.0, "eutectic_x": 0.399,
             "src": "ASM: 779 C, 28.1 wt% Cu"},
    "alsi": {"eutectic_T_K": 850.0, "eutectic_x": 0.122,
             "src": "ASM: 577 C, 12.6 wt% Si"},
    "fec":  {"peritectic_T_K": 1768.0, "eutectic_T_K": 1421.0, "eutectoid_T_K": 1000.0,
             "src": "ASM (Fe-Fe3C metaestable): 1495 C, 1148 C, 727 C"},
    "cuni": {"Tm_A_K": 1357.77, "Tm_B_K": 1728.3, "src": "ASM: isomorfo"},
    "water": {"triple_T_K": 273.16, "triple_P_Pa": 611.657,
              "critical_T_K": 647.096, "critical_P_Pa": 22.064e6, "src": "IAPWS R14-08 / Wagner"},
}
