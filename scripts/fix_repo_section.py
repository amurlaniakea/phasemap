#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Sustituye la seccion obsoleta 'DE VISOR A REPOSITORIO' por el estado real del repo.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "web", "index.html")
s = open(P, encoding="utf-8").read()
if "EL REPOSITORIO · PUBLICADO" in s:
    print("OK: la seccion ya estaba actualizada"); raise SystemExit(0)
start = s.find('<section id="repo"')
assert start != -1, "no se encontro la seccion repo"
end = s.find("</section>", start) + len("</section>")
NEW = """<section id="repo" class="section">
  <div class="sec-head reveal"><div class="eyebrow">EL REPOSITORIO · PUBLICADO</div>
    <h2>Phasemap v0.2.0</h2>
    <p>Lo que empezó como propuesta es hoy un repositorio real y verificado: núcleo stdlib, 76 tests, dos visores en vivo y datos con límites declarados. AGPL-3.0.</p>
  </div>
  <div class="repo-grid">
    <div class="panel verdict reveal" style="--i:0">
      <h3><span>Estado:</span> Fases 1–9 completadas</h3>
      <p><b>Núcleo:</b> envolvente convexa + Newton sobre potenciales químicos, en Python stdlib (sin numpy/scipy). 76 tests analíticos en CI.</p>
      <p><b>Visores:</b> este (2 fases · Pb–Sn, Cu–Ni, Ag–Cu, agua) y <a href="multifase.html">multifase</a> (Fe–C, Al–Si). Canvas puro, 0 dependencias.</p>
      <p><b>Datos:</b> CSV de fronteras + tabla de límites frente a ASM / IAPWS / Datchi. Se regeneran con <span class="mono">make verify</span>.</p>
      <p><b>Siguiente (Fase 10):</b> sublattice de dos subredes para Al–Si y eutectoide sólido del Fe–C.</p>
      <p style="margin-top:12px"><a href="https://github.com/amurlaniakea/phasemap" target="_blank" rel="noopener">Repositorio ↗</a> &nbsp;·&nbsp; <a href="https://github.com/amurlaniakea/phasemap/releases/tag/v0.2.0" target="_blank" rel="noopener">Release v0.2.0 ↗</a></p>
    </div>
    <div class="panel tree-panel reveal" style="--i:1">
      <div class="panel-head"><span class="led"></span><h3>Arquitectura actual</h3></div>
<pre><span class="d">phasemap/</span>
├── <span class="d">src/phasemap/</span>
│   ├── <span class="d">core/</span>      <span class="c"># gibbs, hull, equilibrium, multiphase</span>
│   ├── <span class="d">models/</span>    <span class="c"># regular+RK, miscibility, water IAPWS</span>
│   └── <span class="d">systems/</span>   <span class="c"># presets + compounds (Al-Si, Fe-C)</span>
├── <span class="d">tests/</span>         <span class="c"># 76 tests: núcleo + multifase + web</span>
├── <span class="d">scripts/</span>       <span class="c"># build_data, verify_release</span>
├── <span class="d">data/</span>          <span class="c"># CSV + limits_report + references</span>
├── <span class="d">web/</span>           <span class="c"># index.html + multifase.html</span>
├── <span class="d">docs/</span>          <span class="c"># theory, limits, roadmap</span>
├── <span class="f">Makefile</span>       <span class="c"># test / data / verify / serve</span>
├── <span class="f">CHANGELOG.md</span>
└── <span class="f">LICENSE</span>        <span class="c"># AGPL-3.0</span></pre>
    </div>
  </div>
</section>"""
s = s[:start] + NEW + s[end:]
if ".verdict a{" not in s:
    s = s.replace("</style>", ".verdict a{color:var(--teal);text-decoration:none}.verdict a:hover{text-decoration:underline}\n</style>", 1)
open(P, "w", encoding="utf-8").write(s)
print("OK: seccion 'DE VISOR A REPOSITORIO' sustituida por el estado real (v0.2.0)")
