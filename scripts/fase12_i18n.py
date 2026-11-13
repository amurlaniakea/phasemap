#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 12: actualiza estado (v0.3.1 / Fases 1-11), README y anade toggle ES/EN al visor.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)

# 1) Seccion de estado en Pages: v0.2.0 -> v0.3.1, Fases 1-9 -> 1-11
P = "web/index.html"; s = read(P); o = s
s = s.replace("Phasemap v0.2.0", "Phasemap v0.3.1")
s = s.replace("Fases 1–9 completadas", "Fases 1–11 completadas")
s = s.replace("<b>Siguiente (Fase 10):</b> sublattice de dos subredes para Al–Si y eutectoide sólido del Fe–C.",
              "<b>Fase 10–11:</b> Al–Si calibrado por estabilidad de red (eutéctico ≈850 K) y eutectoide γ→α+Fe₃C. <b>Siguiente (Fase 12):</b> contraste CALPHAD/SGTE.")
s = s.replace("núcleo stdlib, 76 tests, dos visores en vivo y datos con límites declarados. AGPL-3.0.",
              "núcleo stdlib, 76 tests, motor multifase con eutectoide, dos visores en vivo y datos con límites declarados. AGPL-3.0.")

# 2) Toggle ES/EN: capa aditiva (diccionario + traductor + MutationObserver), sin tocar la logica.
if "pm-lang" not in s:
    I18N = r'''<style>
.lang-btn{font:600 10.5px var(--mono);letter-spacing:.08em;color:var(--cyan);background:rgba(77,163,255,.08);border:1px solid rgba(77,163,255,.35);border-radius:20px;padding:6px 12px;cursor:pointer;transition:all .2s}
.lang-btn:hover{background:rgba(77,163,255,.18);transform:translateY(-1px)}
</style>
<script>
(function(){
"use strict";
var DICT={
"TERMODINÁMICA COMPUTACIONAL · CERO DEPENDENCIAS · CANVAS PURO":"COMPUTATIONAL THERMODYNAMICS · ZERO DEPENDENCIES · PURE CANVAS",
"El equilibrio de fases,":"Phase equilibrium,",
"Energía libre de Gibbs, tangentes comunes y regla de la palanca — calculadas en vivo sobre solución regular y Redlich–Kister, con el agua de IAPWS como segundo sistema. Arrastra el punto de estado y mira responder a la materia.":"Gibbs free energy, common tangents and the lever rule — computed live on regular-solution and Redlich–Kister models, with IAPWS water as a second system. Drag the state point and watch matter respond.",
"sistemas":"systems","dependencias JS":"JS dependencies","validación":"validation","en vivo":"live",
"Controles":"Controls","Sistema":"System","Eutéctico":"Eutectic","Lacuna":"Miscibility gap","Agua P–T":"Water P–T",
"Preset de aleación":"Alloy preset","Temperatura":"Temperature","Composición global x₀":"Overall composition x₀",
"Presión · log₁₀":"Pressure · log₁₀","Ω · interacción":"Ω · interaction","Modelo · regular + RK":"Model · regular + RK",
"L₀ sólido":"L₀ solid","L₁ asimetría":"L₁ asymmetry","Ω líquido":"Ω liquid","T fusión A":"T melting A","T fusión B":"T melting B",
"Espinodal":"Spinodal","Reparto":"Tie-line","Rejilla":"Grid","Etiquetas":"Labels","Aleatorio":"Random","Punto notable ▸":"Notable point ▸","Copiar estado JSON":"Copy state JSON",
"Diagrama eutéctico binario · T–x":"Binary eutectic diagram · T–x","Lacuna de miscibilidad · T–x":"Miscibility gap · T–x","Agua · P–T (log)":"Water · P–T (log)",
"G(x) · tangente común":"G(x) · common tangent","G(x) · solución regular":"G(x) · regular solution","Punto de estado":"State point",
"Arrastra":"Drag","sobre el diagrama para mover el punto de estado":"on the diagram to move the state point","flechas":"arrows","ajuste fino":"fine tuning","clic en la leyenda = descripción":"click legend = description",
"RIGOR VERIFICABLE":"VERIFIABLE RIGOR","Modelo y límites explícitos":"Model and explicit limits",
"La misma filosofía que Orbitae: cada identidad termodinámica se comprueba en vivo, y cada desviación frente a la realidad se declara en una tabla. Nada se esconde detrás de una interpolación bonita.":"The same philosophy as Orbitae: every thermodynamic identity is checked live, and every deviation from reality is declared in a table. Nothing hides behind a pretty interpolation.",
"Energía de mezcla":"Mixing energy","Tangente común":"Common tangent","Regla de la palanca":"Lever rule","Espinodal y punto crítico":"Spinodal and critical point","Regla de fases de Gibbs":"Gibbs phase rule",
"EL REPOSITORIO · PUBLICADO":"THE REPOSITORY · PUBLISHED","Arquitectura actual":"Current architecture","Estado:":"Status:","Núcleo:":"Core:","Visores:":"Viewers:","Datos:":"Data:","Repositorio ↗":"Repository ↗",
"Líquido (L)":"Liquid (L)","Sólido α (rico en A)":"Solid α (A-rich)","Sólido β (rico en B)":"Solid β (B-rich)","α + Líquido":"α + Liquid","Líquido + β":"Liquid + β",
"Temperatura eutéctica":"Eutectic temperature","Composición eutéctica":"Eutectic composition","modelo vs. referencia":"model vs. reference","Magnitud":"Quantity","Este modelo":"This model","Referencia real":"Real reference","Desviación":"Deviation",
"monofásico":"single-phase","bifásico":"two-phase","invariante":"invariant","estable":"stable","metaestable":"metastable","inestable":"unstable",
"fracción molar":"mole fraction","Presión":"Pressure","Fase":"Phase","Fracción molar":"Mole fraction",
"SONIDO ON":"SOUND ON","SONIDO OFF":"SOUND OFF","Multifase ↗":"Multiphase ↗","Repositorio":"Repository","Laboratorio":"Laboratory","Modelo y límites":"Model & limits"
};
var RX=[[/fracción molar/g,"mole fraction"],[/K · x_E/g,"K · x_E"],[/eutéctico/g,"eutectic"],[/peritéctico/g,"peritectic"],[/eutectoide/g,"eutectoid"]];
var lang="es";try{lang=localStorage.getItem("pm-lang")||"es";}catch(e){}
var originals=new Map();var applying=false;
function tr(s){var t=s.trim();if(DICT[t]!==undefined)return s.replace(t,DICT[t]);var o=s;for(var i=0;i<RX.length;i++){o=o.replace(RX[i][0],RX[i][1]);}return o;}
function walk(root){applying=true;var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null);var n;while((n=w.nextNode())){var p=n.parentNode;if(!p||p.nodeName==="SCRIPT"||p.nodeName==="STYLE")continue;var v=n.nodeValue;if(!v||!v.trim())continue;var t=tr(v);if(t!==v){if(!originals.has(n))originals.set(n,v);n.nodeValue=t;}}applying=false;}
function toES(){originals.forEach(function(v,n){if(n.isConnected)n.nodeValue=v;});originals.clear();}
function setLang(l){lang=l;try{localStorage.setItem("pm-lang",l);}catch(e){}document.documentElement.lang=l;if(l==="en"){walk(document.body);}else{toES();}var b=document.getElementById("langBtn");if(b)b.textContent=(l==="en")?"EN ✓":"ES ✓";}
function addBtn(){var host=document.querySelector(".top-actions");if(!host||document.getElementById("langBtn"))return;var b=document.createElement("button");b.id="langBtn";b.className="lang-btn";b.type="button";b.setAttribute("aria-label","Cambiar idioma / Switch language");b.textContent=(lang==="en")?"EN ✓":"ES ✓";b.onclick=function(){setLang(lang==="en"?"es":"en");};host.insertBefore(b,host.firstChild);}
var mo=new MutationObserver(function(muts){if(lang!=="en"||applying)return;applying=true;for(var i=0;i<muts.length;i++){var m=muts[i];if(m.type==="childList"){for(var j=0;j<m.addedNodes.length;j++){var nd=m.addedNodes[j];if(nd.nodeType===1){walk(nd);}else if(nd.nodeType===3){var v=nd.nodeValue||"";var t=tr(v);if(t!==v){if(!originals.has(nd))originals.set(nd,v);nd.nodeValue=t;}}}}else if(m.type==="characterData"){var nd2=m.target;var v2=nd2.nodeValue||"";var t2=tr(v2);if(t2!==v2){if(!originals.has(nd2))originals.set(nd2,v2);nd2.nodeValue=t2;}}}applying=false;});
function init(){addBtn();document.documentElement.lang=lang;if(lang==="en"){walk(document.body);}mo.observe(document.body,{childList:true,subtree:true,characterData:true});}
if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",init);}else{init();}
})();
</script>
'''
    s = s.replace("</body>", I18N + "</body>", 1)
if s != o: write(P, s); print("OK: estado v0.3.1 + toggle ES/EN en index.html")

# 3) README: actualiza referencias de version/tests (defensivo)
R = "README.md"; r = read(R); ro = r
r = r.replace("64 tests", "76 tests").replace("v0.2.0", "v0.3.1")
if "multifase" not in r:
    r = r.replace("## Quickstart", "## Visores\n\n- 2 fases: <https://amurlaniakea.github.io/phasemap/> (Pb–Sn, Cu–Ni, Ag–Cu, agua).\n- Multifase: <https://amurlaniakea.github.io/phasemap/multifase.html> (Fe–C con eutectoide, Al–Si calibrado).\n\n## Quickstart", 1)
if r != ro: write(R, r); print("OK: README actualizado")
print("OK: Fase 12 aplicada")
