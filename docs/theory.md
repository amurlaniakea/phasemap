# Teoria y algoritmos

## Energia libre de mezcla (solucion regular + Redlich-Kister)

    G(x,T) = (1-x) gA(T) + x gB(T) + RT [x ln x + (1-x) ln(1-x)]
             + x(1-x) [L0 + L1 (2x-1)]

con g_i(T) = dHf_i (1 - T/Tm_i) para el liquido (referencia: solido puro).

    G'  = gB - gA + RT ln(x/(1-x)) + (1-2x)(L0 + L1(2x-1)) + 2 L1 x(1-x)
    G'' = RT/(x(1-x)) - 2 L0 + 6 L1 (1-2x)
    mu_A = G - x G' ;  mu_B = G + (1-x) G'

## Equilibrio: envolvente convexa + tangente comun

1. Malla de 321 puntos por fase; union ordenada por x.
2. Envolvente convexa inferior (monotone chain, O(n)).
3. Aristas consecutivas de la misma fase -> regiones monofasicas.
4. Newton 2x2 sobre F = (mu_A^1 - mu_A^2, mu_B^1 - mu_B^2), |F| < 1e-7 J/mol.
5. Palanca: f_1 = (x2 - x0)/(x2 - x1); Sum f = 1 y Sum f x = x0.

## Lacuna de miscibilidad (simetrica, analitica)

    T_c = Omega/(2R) ;  espinodal: x(1-x) = RT/(2 Omega)
    binodal: ln(x/(1-x)) + (Omega/RT)(1-2x) = 0  (biseccion)

## Agua P-T

- Vaporizacion: Wagner (IAPWS-95 suplementaria), [Tt, Tc].
- Sublimacion y fusion Ih: IAPWS R14-08 (2011).
- Hielos III, V, VI: Simon-Glatzel c=3 anclada a puntos triples IAPWS.
- Hielo VII: anclada al triple (355 K, 2.216 GPa) y a Datchi (751.5 K, 13.09 GPa).
- Clausius-Clapeyron: L_est = R T^2 d ln P/dT (vapor ideal, v_liq ~ 0).

## Referencias

- Wagner & Pruss (2002). J. Phys. Chem. Ref. Data 31, 387. (IAPWS-95)
- IAPWS R14-08 (2011). Melting and Sublimation Curves of Ordinary Water.
- Datchi, Loubeyre & LeToullec (2000). Phys. Rev. B 61, 6535.
- Massalski. Binary Alloy Phase Diagrams. ASM International.
- Bragg & Williams (1934); Redlich & Kister (1948); Simon & Glatzel (1929).
