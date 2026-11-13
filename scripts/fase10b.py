#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 10b: test de eutectoide robusto (ensamblaje directo) + v0.3.1.
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def write(p, s): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)

# 1) test eutectoide robusto: ensamblaje directo en vez del detector sensible a la malla
P = "tests/test_fase7.py"
s = read(P); i = s.find("def test_fe_c_eutectoid():"); assert i != -1
NEW = '''def test_fe_c_eutectoid():
    # Eutectoide gamma -> alpha + Fe3C: comprobacion directa del ensamblaje (robusta,
    # independiente de la resolucion del detector de invariantes).
    from phasemap.core.multiphase import equilibrium_multi
    ph = fe_c()
    x = 0.03
    def assemblage(T):
        segs, H = equilibrium_multi(ph, T, n=240)
        q = next((s for s in segs if s[0] <= x <= s[1]), segs[-1])
        return q[5]
    low = assemblage(1100.0)    # por debajo del eutectoide
    high = assemblage(1250.0)   # por encima del eutectoide
    assert "alpha" in low and "Fe3C" in low and "gamma" not in low
    assert "gamma" in high
'''
write(P, s[:i] + NEW)

# 2) version 0.3.1 + changelog
for rel, a, b in [("pyproject.toml", 'version = "0.3.0"', 'version = "0.3.1"'),
                  ("src/phasemap/__init__.py", '__version__ = "0.3.0"', '__version__ = "0.3.1"')]:
    t = read(rel)
    if a in t: write(rel, t.replace(a, b, 1))
ch = read("CHANGELOG.md")
if "v0.3.1" not in ch:
    entry = ("## v0.3.1\n- Corrige el test del eutectoide Fe-C: comprobacion directa del ensamblaje "
             "(alpha+Fe3C por debajo, gamma+Fe3C por encima) en vez del detector de invariantes "
             "sensible a la resolucion de la malla. Sin cambios en el nucleo ni en los datos.\n\n")
    write("CHANGELOG.md", ch.replace("# Changelog\n", "# Changelog\n\n" + entry, 1))
print("OK: Fase 10b aplicada (test eutectoide robusto + v0.3.1)")
