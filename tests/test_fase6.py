# Fase 6: Ag-Cu eutectico.
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
