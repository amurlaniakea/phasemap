#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 12: citacion Zenodo (CITATION.cff + .zenodo.json) + toggle ES/EN en multifase.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)

write("CITATION.cff", '''cff-version: 1.2.0
message: "If you use this software, please cite it as below."
title: "Phasemap: verifiable phase diagrams"
type: software
authors:
  - family-names: "Sordo Martínez"
    given-names: Pedro
license: AGPL-3.0-only
version: 0.4.0
date-released: "2026-11-12"
repository-code: "https://github.com/amurlaniakea/phasemap"
url: "https://amurlaniakea.github.io/phasemap/"
keywords:
  - thermodynamics
  - phase diagrams
  - CALPHAD
  - IAPWS
  - eutectic
  - Gibbs free energy
''')
write(".zenodo.json", '''{
  "title": "Phasemap: verifiable phase diagrams",
  "description": "Verifiable phase-diagram engine: convex-hull + Newton common-tangent equilibrium, regular-solution/Redlich-Kister and IAPWS water, multiphase compounds and invariant detection, with zero-dependency Canvas viewers and declared limits.",
  "upload_type": "software",
  "license": "AGPL-3.0-only",
  "creators": [{"name": "Sordo Martínez, Pedro"}],
  "keywords": ["thermodynamics", "phase diagrams", "CALPHAD", "IAPWS", "eutectic", "Gibbs free energy"],
  "related_identifiers": [
    {"identifier": "https://github.com/amurlaniakea/phasemap", "relation": "isSupplementTo", "scheme": "url"}
  ]
}
''')

# README: seccion de citacion
R = "README.md"; r = read(R)
if "## Citación" not in r and "## Citation" not in r:
    cite = ("\n## Citación / Citation\n\nSi usas Phasemap, cítalo (botón «Cite this repository» en GitHub, `CITATION.cff`). "
            "Archivado en Zenodo con DOI: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX) "
            "(sustituye el DOI tras activar la integración Zenodo–GitHub).\n")
    r = r.rstrip() + "\n" + cite
    write(R, r)

# Toggle ES/EN en multifase (capa aditiva, host=header)
P = "web/multifase.html"; s = read(P)
if "pm-lang" not in s:
    I18N = r'''<style>.lang-btn{font:600 10.5px var(--mono);color:var(--cyan);background:rgba(77,163,255,.08);border:1px solid rgba(77,163,255,.35);border-radius:20px;padding:5px 11px;cursor:pointer;margin-left:auto}</style>
<script>
(function(){
"use strict";
var DICT={"Controles":"Controls","Sistema":"System","Temperatura":"Temperature","Composición x₀":"Composition x₀",
"Etiquetas":"Labels","Rejilla":"Grid","Invariantes":"Invariants","Estado e invariantes":"State & invariants",
"← visor 2 fases":"← 2-phase viewer","repo ↗":"repo ↗","Reset":"Reset",
"Arrastra para mover el punto de estado. Envoltura convexa sobre N fases; compuestos de línea (Fe₃C, (Si)) como puntos. Invariantes por cruce de margen entre fases.":"Drag to move the state point. Convex hull over N phases; line compounds (Fe₃C, (Si)) as points. Invariants by margin crossing between phases.",
"eutéctico":"eutectic","peritéctico":"peritectic","sólido":"solid","fracción molar":"mole fraction"};
var lang="es";try{lang=localStorage.getItem("pm-lang")||"es";}catch(e){}
var originals=new Map();var applying=false;
function tr(s){var t=s.trim();if(DICT[t]!==undefined)return s.replace(t,DICT[t]);return s;}
function walk(root){applying=true;var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null);var n;while((n=w.nextNode())){var p=n.parentNode;if(!p||p.nodeName==="SCRIPT"||p.nodeName==="STYLE")continue;var v=n.nodeValue;if(!v||!v.trim())continue;var t=tr(v);if(t!==v){if(!originals.has(n))originals.set(n,v);n.nodeValue=t;}}applying=false;}
function toES(){originals.forEach(function(v,n){if(n.isConnected)n.nodeValue=v;});originals.clear();}
function setLang(l){lang=l;try{localStorage.setItem("pm-lang",l);}catch(e){}document.documentElement.lang=l;if(l==="en"){walk(document.body);}else{toES();}var b=document.getElementById("langBtn");if(b)b.textContent=(l==="en")?"EN ✓":"ES ✓";}
function addBtn(){var host=document.querySelector("header");if(!host||document.getElementById("langBtn"))return;var b=document.createElement("button");b.id="langBtn";b.className="lang-btn";b.type="button";b.textContent=(lang==="en")?"EN ✓":"ES ✓";b.onclick=function(){setLang(lang==="en"?"es":"en");};host.appendChild(b);}
var mo=new MutationObserver(function(muts){if(lang!=="en"||applying)return;applying=true;for(var i=0;i<muts.length;i++){var m=muts[i];if(m.type==="childList"){for(var j=0;j<m.addedNodes.length;j++){var nd=m.addedNodes[j];if(nd.nodeType===1){walk(nd);}else if(nd.nodeType===3){var v=nd.nodeValue||"";var t=tr(v);if(t!==v){if(!originals.has(nd))originals.set(nd,v);nd.nodeValue=t;}}}}}applying=false;});
function init(){addBtn();document.documentElement.lang=lang;if(lang==="en"){walk(document.body);}mo.observe(document.body,{childList:true,subtree:true,characterData:true});}
if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",init);}else{init();}
})();
</script>
'''
    s = s.replace("</body>", I18N + "</body>", 1); write(P, s)
print("OK: Zenodo (CITATION.cff + .zenodo.json) + citacion README + ES/EN en multifase")
