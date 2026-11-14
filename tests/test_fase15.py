# Fase 15: invariantes del Fe-C por seccion Fe-Fe3C (detector robusto).
from phasemap.systems.compounds import fe_c
from phasemap.core.multiphase import invariants_section


def test_fe_c_three_invariants():
    iv = invariants_section(fe_c(), 900.0, 1900.0, rows=200, n=260)
    assert "peritectico" in iv and "eutectico" in iv and "eutectoide" in iv
    assert 1650.0 < iv["peritectico"] < 1800.0
    assert 1350.0 < iv["eutectico"] < 1550.0
    assert 900.0 < iv["eutectoide"] < 1250.0
    assert iv["eutectoide"] < iv["eutectico"] < iv["peritectico"]
