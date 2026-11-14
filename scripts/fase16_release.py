#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Fase 16: remata el visor multifase (x de invariantes, CSV/JSON, limites),
sincroniza page + README con el assessment real y prepara v0.5.0."""
import os, re, csv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)

# --- 1) multifase: idempotente ---
P = "web/multifase.html"; s = read(P); o = s
if "x:bm[1]" not in s:
    s = s.replace("inv.push({T:Ti,kind,ph:[la,lb,lc].sort().join('+')});",
                  "inv.push({T:Ti,kind,ph:[la,lb,lc].sort().join('+'),x:bm[1]});")
if "iv.x!==undefined" not in s:
    s = s.replace("""for(const iv of inv)html+=`<div class="inv"><b>${iv.kind}</b> ${iv.T.toFixed(0)} K · ${iv.ph}</div>`;""",
                  """for(const iv of inv)html+=`<div class="inv"><b>${iv.kind}</b> ${iv.T.toFixed(0)} K · ${iv.ph}${iv.x!==undefined?' · x='+iv.x.toFixed(3):''}</div>`;""")
if 'id="csv"' not in s:
    s = s.replace("""<button class="btn p" id="png">▼ PNG</button>""",
                  """<button class="btn p" id="png">▼ PNG</button>
      <button class="btn" id="csv">▼ CSV</button>
      <button class="btn" id="json">▼ JSON</button>""")
    s = s.replace("""document.getElementById('png').onclick=()=>{const a=document.createElement('a');a.download='phasemap_multifase_'+cur+'.png';a.href=cv.toDataURL('image/png');a.click();};""",
                  """document.getElementById('png').onclick=()=>{const a=document.createElement('a');a.download='phasemap_multifase_'+cur+'.png';a.href=cv.toDataURL('image/png');a.click();};
function dl(name,blob){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),2000);}
document.getElementById('csv').onclick=()=>{const{rows}=cache;let c='T_K,phase_regions\\n';for(const[T,segs]of rows){c+=T.toFixed(1)+',"'+segs.map(q=>q.label+'['+q.x0.toFixed(3)+','+q.x1.toFixed(3)+']').join(';')+'"\\n';}dl('phasemap_'+cur+'.csv',new Blob([c],{type:'text/csv'}));};
document.getElementById('json').onclick=()=>{const{s,inv}=cache;dl('phasemap_'+cur+'_invariants.json',new Blob([JSON.stringify({system:s.name,invariants:inv},null,2)],{type:'application/json'}));};""")
if "ledeburita" not in s:
    s = s.replace("""<div class="note">Arrastra para mover el punto de estado.""",
                  """<div class="note"><b>Referencia real:</b> Fe–Fe₃C → peritéctico 1495 °C · eutéctico (ledeburita) 1147 °C · eutectoide (perlita) 727 °C. Al–Si → eutéctico 577 °C / 12.6 wt% Si. Desviaciones declaradas en docs/assessment.md.</div>
    <div class="note">Arrastra para mover el punto de estado.""")
if s != o: write(P, s); print("OK: multifase (x invariantes + CSV/JSON + limites)")

# --- 2) filas Fe-C reales desde el assessment ---
LBL = {"peritectic_T_K": "peritéctico L+δ→γ", "eutectic_T_K": "eutéctico (ledeburita)",
       "eutectoid_T_K": "eutectoide (perlita)"}
fec = []
with open(os.path.join(ROOT, "data", "assessment.csv"), newline="") as f:
    for r in csv.DictReader(f):
        if r["system"] == "fec" and r["quantity"] in LBL:
            fec.append("| Fe–C | %s | %s K | %s K | %s %% |" %
                       (LBL[r["quantity"]], r["model"], r["assessed"], r["dev_pct"]))

# --- 3) README ---
P = "README.md"; s = read(P)
s = s.replace("79 tests", "83 tests").replace("76 tests", "83 tests").replace("v0.4.0", "v0.5.0")
if fec:
    out = []; done = False
    for ln in s.split("\n"):
        if ln.startswith("| Fe–C |") or ln.startswith("| Fe-C |"):
            if not done: out.extend(fec); done = True
            continue
        out.append(ln)
    s = "\n".join(out)
write(P, s); print("OK: README (83 tests, v0.5.0, filas Fe-C del assessment)")

# --- 4) page ---
P = "web/index.html"; s = read(P)
s = s.replace("Phasemap v0.4.0", "Phasemap v0.5.0").replace("79 tests", "83 tests")
s = s.replace("Fases 1–12 completadas", "Fases 1–15 completadas")
s = s.replace("releases/tag/v0.4.0", "releases/tag/v0.5.0").replace("Release v0.4.0 ↗", "Release v0.5.0 ↗")
s = re.sub(r"<p><b>Fase 10[^<]*</b>.*?</p>",
           "<p><b>Fase 10–15:</b> Al–Si calibrado (≈850 K), Fe–C con los tres invariantes "
           "(peritéctico, eutéctico y eutectoide) en la sección Fe–Fe₃C, y detector de invariantes "
           "por sección en el núcleo. <b>Siguiente:</b> más binarios y CALPHAD multicomponente.</p>",
           s, count=1, flags=re.DOTALL)
write(P, s); print("OK: page (v0.5.0, 83 tests, Fases 1-15)")

# --- 5) version + changelog + roadmap ---
for rel, a, b in [("pyproject.toml", 'version = "0.4.0"', 'version = "0.5.0"'),
                  ("src/phasemap/__init__.py", '__version__ = "0.4.0"', '__version__ = "0.5.0"'),
                  ("CITATION.cff", "version: 0.4.0", "version: 0.5.0")]:
    t = read(rel)
    if a in t: write(rel, t.replace(a, b, 1))
ch = read("CHANGELOG.md")
if "v0.5.0" not in ch:
    e = ("## v0.5.0\n- Fe-C calibrado en la seccion Fe-Fe3C: alotropia del Fe puro analitica "
         "(alpha<->gamma 1185 K, gamma<->delta 1667 K), exceso intersticial en gamma/alpha, "
         "y los tres invariantes (peritectico, eutectico, eutectoide) en el assessment.\n"
         "- invariants_section() en el nucleo: detector robusto por cambio de ensamblaje.\n"
         "- Visor multifase: composicion de invariantes, export CSV/JSON y tabla de limites.\n"
         "- 83 tests. README y page sincronizados con el assessment real.\n\n")
    write("CHANGELOG.md", ch.replace("# Changelog\n", "# Changelog\n\n" + e, 1))
rm = read("docs/roadmap.md")
if "Fase 15" not in rm:
    rm = rm.rstrip() + ("\n- [x] Fase 13: visor multifase (invariantes x, CSV/JSON, limites).\n"
                        "- [x] Fase 14: Fe-C calibrado (alotropia + seccion Fe-Fe3C).\n"
                        "- [x] Fase 15: invariants_section en el nucleo + assessment completo.\n")
    write("docs/roadmap.md", rm)
print("OK: v0.5.0 (version, changelog, roadmap)")
