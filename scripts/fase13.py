#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 13: page "Siguiente" al dia + multifase (invariantes con x, CSV/JSON, tabla de limites).
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)

# A) page: parrafo Fase 10-11 / Siguiente (Fase 12) -> estado real (Fase 12 hecha)
P = "web/index.html"; s = read(P)
s2 = re.sub(r"<p><b>Fase 10–11:</b>.*?</p>",
    "<p><b>Fase 10–12:</b> Al–Si calibrado (eutéctico ≈850 K), eutectoide γ→α+Fe₃C y contraste CALPHAD/SGTE (assessment). <b>Siguiente:</b> afinar Fe–C (1421/1000 K) y más binarios.</p>",
    s, count=1, flags=re.DOTALL)
if s2 != s: write(P, s2); print("OK: page 'Siguiente' actualizado (Fase 12 hecha)")
else: print("AVISO: no se encontro el parrafo Fase 10-11")

# B) multifase
P = "web/multifase.html"; s = read(P); o = s
# B1: invariantes con composicion x
s = s.replace("inv.push({T:Ti,kind,ph:[la,lb,lc].sort().join('+')});",
              "inv.push({T:Ti,kind,ph:[la,lb,lc].sort().join('+'),x:bm[1]});")
# B2: panel muestra x de cada invariante
s = s.replace("""for(const iv of inv)html+=`<div class="inv"><b>${iv.kind}</b> ${iv.T.toFixed(0)} K · ${iv.ph}</div>`;""",
              """for(const iv of inv)html+=`<div class="inv"><b>${iv.kind}</b> ${iv.T.toFixed(0)} K · ${iv.ph}${iv.x!==undefined?' · x='+iv.x.toFixed(3):''}</div>`;""")
# B3: botones CSV/JSON junto a PNG
s = s.replace("""<button class="btn p" id="png">▼ PNG</button>""",
              """<button class="btn p" id="png">▼ PNG</button>
      <button class="btn" id="csv">▼ CSV</button>
      <button class="btn" id="json">▼ JSON</button>""")
# B4: funciones de export CSV/JSON
s = s.replace("""document.getElementById('png').onclick=()=>{const a=document.createElement('a');a.download='phasemap_multifase_'+cur+'.png';a.href=cv.toDataURL('image/png');a.click();};""",
              """document.getElementById('png').onclick=()=>{const a=document.createElement('a');a.download='phasemap_multifase_'+cur+'.png';a.href=cv.toDataURL('image/png');a.click();};
function dl(name,blob){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000);}
document.getElementById('csv').onclick=()=>{const{rows}=cache;let c='T_K,phase_regions\\n';for(const[T,segs]of rows){c+=T.toFixed(1)+',"'+segs.map(q=>q.label+'['+q.x0.toFixed(3)+','+q.x1.toFixed(3)+']').join(';')+'"\\n';}dl('phasemap_'+cur+'.csv',new Blob([c],{type:'text/csv'}));};
document.getElementById('json').onclick=()=>{const{s,inv}=cache;dl('phasemap_'+cur+'_invariants.json',new Blob([JSON.stringify({system:s.name,invariants:inv},null,2)],{type:'application/json'}));};""")
# B5: tabla de limites de referencia bajo el lienzo
s = s.replace("""<div class="note">Arrastra para mover el punto de estado. Envoltura convexa sobre N fases; compuestos de línea (Fe₃C, (Si)) como puntos. Invariantes por cruce de margen entre fases.</div>""",
              """<div class="note">Arrastra para mover el punto de estado. Envoltura convexa sobre N fases; compuestos de línea (Fe₃C, (Si)) como puntos. Invariantes por cruce de margen entre fases.</div>
    <div class="note"><b>Referencia real:</b> Fe–Fe₃C → peritéctico 1495 °C · eutéctico (ledeburita) 1147 °C · eutectoide (perlita) 727 °C. Al–Si → eutéctico 577 °C / 12.6 wt% Si. El modelo reproduce la topología; las desviaciones de temperatura se declaran en docs/assessment.md.</div>""")
if s != o: write(P, s); print("OK: multifase (invariantes x + CSV/JSON + tabla limites)")
else: print("AVISO: multifase sin cambios (revisa anclas)")
