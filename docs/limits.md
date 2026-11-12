# Tabla de error y limites (generada por scripts/build_data.py)

| Sistema | Magnitud | Modelo | Referencia | Desv. % | Estado | Fuente |
|---|---|---|---|---|---|---|
| Pb-Sn | T_eutectica_K | 447 | 456.1 | 2.01 | OK | Massalski, Binary Alloy Phase Diagrams (ASM): 183 C, 61.9 wt% Sn |
| Pb-Sn | x_eutectica | 0.7331 | 0.739 | 0.79 | OK | Massalski, Binary Alloy Phase Diagrams (ASM): 183 C, 61.9 wt% Sn |
| Pb-Sn | solubilidad_max_B_en_alpha | 0.291 | 0.293 | 0.70 | OK | Massalski, Binary Alloy Phase Diagrams (ASM): 183 C, 61.9 wt% Sn |
| Pb-Sn | solubilidad_max_A_en_beta | 0.02 | 0.0145 | 37.92 | DESVIADO | Massalski, Binary Alloy Phase Diagrams (ASM): 183 C, 61.9 wt% Sn |
| Cu-Ni | eutectico | ausente | ausente (isomorfo) | 0 | OK | ASM: sistema isomorfo, solubilidad total en solido y liquido |
| Cu-Ni | T_fusion_Cu_K | 1358 | 1358 | 0.00 | OK | ASM: sistema isomorfo, solubilidad total en solido y liquido |
| Cu-Ni | T_fusion_Ni_K | 1728 | 1728 | 0.00 | OK | ASM: sistema isomorfo, solubilidad total en solido y liquido |
| Generico A-B | T_eutectica_K | 547.5 | - | - | MODELO | Sistema didactico sin referencia experimental |
| Generico A-B | x_eutectica | 0.6512 | - | - | MODELO | Sistema didactico sin referencia experimental |
| Generico A-B | solubilidad_max_B_en_alpha | 0.05807 | - | - | MODELO | Sistema didactico sin referencia experimental |
| Generico A-B | solubilidad_max_A_en_beta | 0.02229 | - | - | MODELO | Sistema didactico sin referencia experimental |
| Lacuna regular | T_c_K | 1082 | 1082 | 0.00 | OK | T_c = Omega/2R (analitico) |
| H2O | L_vap_373K_kJ_mol | 41.31 | 40.66 | 1.62 | OK | vapor ideal; Z_vap~0.984 explica el +1.6% |
| H2O | T_ebullicion_1atm_K | 373.1 | 373.1 | 0.00 | OK | Wagner/IAPWS |
| H2O | p_vap_triple_Pa | 611.7 | 611.7 | 0.00 | OK | Wagner vs IAPWS R14-08 |
| H2O | p_fusion_VII_751K_GPa | 13.09 | 13.09 | 0.00 | OK | Datchi et al., PRB 61, 6535 (2000) |

## Supuestos del modelo

- Solucion regular con Omega independientes de T (sin entropia de exceso).
- Una unica red solida: alpha y beta son ramas de la misma fase; sin compuestos intermedios ni peritecticos.
- P fija = 1 atm en binarios (regla de fases condensada F = C - P + 1).
- Clausius-Clapeyron con vapor ideal y v_liquido despreciable: L_est sobrestima ~1.6% (Z_vap ~ 0.984 a 373 K).
- Hielos III-VII: Simon-Glatzel c=3 anclada a puntos triples IAPWS; VII anclada tambien a Datchi (751.5 K, 13.09 GPa).
- Fronteras solido-solido del agua: verticales en T del triple (aproximacion).
- Hielos II, IX, XI, XII... no incluidos. CALPHAD multicomponente: fase futura.
