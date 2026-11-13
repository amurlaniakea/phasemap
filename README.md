# PHASEMAP 🌡️

[![tests](https://github.com/amurlaniakea/phasemap/actions/workflows/tests.yml/badge.svg)](https://github.com/amurlaniakea/phasemap/actions/workflows/tests.yml)
[![pages](https://github.com/amurlaniakea/phasemap/actions/workflows/pages.yml/badge.svg)](https://amurlaniakea.github.io/phasemap/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24205629.svg)](https://doi.org/10.5281/zenodo.24205629)

**Visores en vivo:** [2 fases](https://amurlaniakea.github.io/phasemap/) · [multifase (Fe–C, Al–Si)](https://amurlaniakea.github.io/phasemap/multifase.html)

![Phasemap — visor de diagramas de fase](docs/screenshot.jpg)

**Diagramas de fase verificables** — solucion regular, Redlich-Kister e IAPWS.
Nucleo Python stdlib (cero dependencias), suite pytest analitica y visor web Canvas.
Serie cientifica: **Orbitae · Relmap · Phasemap**.

> El equilibrio de fases no se dibuja: se minimiza. Tangentes comunes sobre la
> envolvente convexa de G(x), refinadas con Newton hasta |Δμ| < 1e-7 J/mol.

    scripts/                build_data, build_data_fase7, build_assessment, verify_release

| Sistema | Magnitud | Modelo | Referencia | Desv. |
|---|---|---|---|---|
| Pb-Sn | T eutectica | 447.0 K | 456.15 K (ASM) | 2.0 % |
| Pb-Sn | x eutectica | 0.733 | 0.739 | 0.8 % |
| Pb-Sn | Sol. max. Sn en α | 0.291 | 0.293 | 0.7 % |
| Pb-Sn | Sol. max. Pb en β | 0.020 | 0.0145 | 37.9 % (declarado) |
| Cu-Ni | Lente isomorfa | sin eutectico | isomorfo | — |
| H2O | T ebullicion 1 atm | 373.124 K | 373.124 K | <0.01 % |
| H2O | L_vap 373 K (vapor ideal) | 41.31 kJ/mol | 40.657 | +1.6 % |
| H2O | Fusion VII 751.5 K | 13.09 GPa | Datchi 2000 | ancla exacta |
| Lacuna | T_c = Ω/2R | 1082.5 K | analitico | 0 % |

79 tests: derivadas, Gibbs-Duhem, tangentes comunes, palanca, regla de fases,
binodal/espinodal, Wagner/IAPWS, Clausius-Clapeyron. Limites: docs/limits.md.

## Visores

- 2 fases: <https://amurlaniakea.github.io/phasemap/> (Pb–Sn, Cu–Ni, Ag–Cu, agua).
- Multifase: <https://amurlaniakea.github.io/phasemap/multifase.html> (Fe–C con eutectoide, Al–Si calibrado).

## Quickstart

    python3 -m venv .venv && source .venv/bin/activate
    pip install -e ".[dev]"
    python -m pytest -q
    python -m phasemap
    scripts/                build_data, build_data_fase7, build_assessment, verify_release

## Estructura

    src/phasemap/core/      gibbs, hull, equilibrium (Newton), multiphase (N fases + invariantes)
    src/phasemap/models/    regular + RK (L0T/L1T), miscibility, water (IAPWS/Wagner)
    src/phasemap/systems/   presets (Pb-Sn, Cu-Ni, Ag-Cu), compounds (Al-Si, Fe-C), references
    tests/                  79 tests analiticos
    scripts/                build_data, build_data_fase7, build_assessment, verify_release
    web/                    index.html (2 fases) + multifase.html — Canvas 0-deps, ES/EN
    docs/                   theory, limits, assessment, roadmap

## Licencia

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](LICENSE)

Este proyecto se distribuye bajo la licencia **AGPL-3.0-or-later** (GNU Affero General Public License versión 3 o posterior). Ver el archivo [`LICENSE`](LICENSE) para el texto legal completo.

**Autor:** Pedro Sordo Martínez <amurlaniakea@gmail.com>  
**Serie:** Orbitae · Relmap · Phasemap

## Citación / Citation

Si usas Phasemap, cítalo (botón «Cite this repository» en GitHub, `CITATION.cff`). Archivado en Zenodo con DOI: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24205629.svg)](https://doi.org/10.5281/zenodo.24205629).
