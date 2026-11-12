#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 6: corrige el lienzo eutectico en blanco (claves L+alpha/beta+L) y anade Ag-Cu.
# Idempotente. Uso: python scripts/fase6.py
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VP = os.path.join(ROOT, "web", "index.html")
CP = os.path.join(ROOT, "src", "phasemap", "systems", "presets.py")
src = open(VP, encoding="utf-8").read(); orig = src; ch = []

if "'L+α'" not in src:
    src = re.sub(r"const REG\s*=\s*\{",
        "const REG={\n  'L+α':{fill:'#2e8f77',ink:'#7fe8c8',name:'α + Líquido',desc:'Zona bifásica α+L.',hatch:true},\n  'β+L':{fill:'#5f5fc9',ink:'#b9b3ff',name:'Líquido + β',desc:'Zona bifásica L+β.',hatch:true},",
        src, count=1)
    ch.append("REG: alias L+α / β+L (fix lienzo eutectico en blanco)")

NEW_BCAT = "const BCAT={'α|α+L':'solidus','α+L|α':'solidus','L+β|β':'solidus','β|β+L':'solidus','L+α|α':'solidus','α+L|L':'liquidus','L|α+L':'liquidus','L|L+β':'liquidus','L|L+α':'liquidus','β+L|L':'liquidus','α|α+β':'solvus','α+β|β':'solvus'};"
src = re.sub(r"const BCAT\s*=\s*\{[^}]*\}", NEW_BCAT, src, count=1, flags=re.DOTALL)
ch.append("BCAT extendido (transiciones L+α)")

if "agcu:" not in src:
    src = re.sub(r"const PRESETS\s*=\s*\{",
        "const PRESETS={\n  agcu:{name:'Ag–Cu',A:'Ag',B:'Cu',params:{TmA:1234.9,TmB:1357.8,dHfA:11300,dHfB:13260,L0:16000,L1:0,omL:7000},\n    ref:{Te:1052.0,xe:0.399,solA:0.141,solB:0.049,note:'Eutéctico real 779 C, 28.1 wt% Cu. Modelo de una red: desviación declarada.'}},",
        src, count=1)
    src = src.replace('<option value="generic">', '<option value="agcu">Ag–Cu · eutéctico</option><option value="generic">', 1)
    ch.append("visor: preset Ag-Cu + opcion select")

if src != orig: open(VP, "w", encoding="utf-8").write(src)

core = open(CP, encoding="utf-8").read()
if '"agcu"' not in core:
    entry = """    "agcu": Preset(
        key="agcu", name="Ag-Cu", A="Ag", B="Cu",
        TmA=1234.9, TmB=1357.8, dHfA=11300.0, dHfB=13260.0,
        L0=16000.0, L1=0.0, omL=7000.0,
        reference={
            "Te_K": 1052.0, "xE": 0.399, "solA": 0.141, "solB_Pb": 0.049,
            "source": "ASM: eutectico 779 C, 28.1 wt% Cu",
        }),
"""
    core = core.replace('    "generic": Preset(', entry + '    "generic": Preset(', 1)
    open(CP, "w", encoding="utf-8").write(core)
    ch.append("nucleo: preset Ag-Cu en presets.py")

TP = os.path.join(ROOT, "tests", "test_fase6.py")
if not os.path.exists(TP):
    open(TP, "w", encoding="utf-8").write("""# Fase 6: Ag-Cu eutectico.
import pytest
from phasemap import PRESETS, scan_diagram

def test_agcu_eutectic():
    d = scan_diagram(PRESETS["agcu"].system(), rows=200, n=240)
    e = d.eutectic
    assert e is not None
    assert 1000.0 < e["T"] < 1100.0
    assert 0.30 < e["xE"] < 0.55

def test_agcu_vs_experiment():
    d = scan_diagram(PRESETS["agcu"].system(), rows=200, n=240)
    e = d.eutectic
    assert abs(e["T"] - 1052.0) / 1052.0 < 0.05
    assert abs(e["xE"] - 0.399) / 0.399 < 0.15
""")
    ch.append("tests/test_fase6.py creado")
for c in ch: print("OK:", c)
print("Fase 6 aplicada")
