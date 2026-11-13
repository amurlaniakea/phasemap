# Changelog

## v0.4.0
- Fase 12 cientifica: Redlich-Kister dependiente de T (L0T/L1T, forma G=a+bT de CALPHAD/SGTE). Modulo de referencias assessed (Massalski/ASM, IAPWS) e informe de assessment sistematico (data/assessment.csv + docs/assessment.md). Citacion Zenodo (CITATION.cff + .zenodo.json).


## v0.3.1
- Corrige el test del eutectoide Fe-C: comprobacion directa del ensamblaje (alpha+Fe3C por debajo, gamma+Fe3C por encima) en vez del detector de invariantes sensible a la resolucion de la malla. Sin cambios en el nucleo ni en los datos.


## v0.3.0
- Fase 10: Al-Si calibrado por estabilidad de red (sublattice efectivo): eutectico ~850 K / x_Si~0.11. Eutectoide Fe-C (gamma -> alpha + Fe3C) con ferrita alpha. Filtro topologico de invariantes (elimina cruces metaestables).


## v0.2.0
- Fase 6: sistema Ag-Cu (nucleo, visor, tests, datos) y fix del lienzo eutectico en blanco.
- Fase 7: motor multifase N-fases, compuestos de linea (LineCompound) y deteccion de invariantes.
- Fase 7c: invariantes por margen entre fases; Fe-C muestra peritectico L+delta->gamma.
- Fase 8: visor multifase autonomo (web/multifase.html) para Fe-C y Al-Si; fix del solapamiento del panel de controles.
- Fase 9: limpieza de parches a scripts/legacy/, verificacion unica, Makefile, tests web y documentacion de release.
- Limites declarados: Al-Si necesita sublattice de dos subredes; eutectoide solido Fe-C pendiente.

## v0.1.0
- Fases 1-5: nucleo stdlib (hull convexo + Newton), 64 tests, datos/limites, visor Canvas 0-deps, CI y GitHub Pages.
