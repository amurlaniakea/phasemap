#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 9: release v0.2.0 — archive parches, verificacion unica, docs y tests web.
import os, re, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)

def read(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()

# 1) archivar parches temporales (no se borran, quedan en scripts/legacy/)
legacy_dir = os.path.join(ROOT, "scripts", "legacy")
os.makedirs(legacy_dir, exist_ok=True)
for name in ["patch_viewer.py", "fase6.py", "fix7b.py", "fix7c.py", "fase8_css.py"]:
    src = os.path.join(ROOT, "scripts", name)
    if os.path.exists(src):
        shutil.move(src, os.path.join(legacy_dir, name))
        print("OK: archivado scripts/" + name + " -> scripts/legacy/")

# 2) version 0.2.0
for rel, pat, rep in [
    ("pyproject.toml", r'version = "0\.1\.0"', 'version = "0.2.0"'),
    ("src/phasemap/__init__.py", r'__version__ = "0\.1\.0"', '__version__ = "0.2.0"'),
]:
    p = os.path.join(ROOT, rel)
    s = open(p, encoding="utf-8").read()
    s2 = re.sub(pat, rep, s, count=1)
    if s2 != s:
        open(p, "w", encoding="utf-8").write(s2)
        print("OK: version 0.2.0 en " + rel)

# 3) README: bloque de estado
p = os.path.join(ROOT, "README.md")
s = open(p, encoding="utf-8").read()
if "v0.2.0" not in s:
    block = ("\n**v0.2.0** · motor multifase (Fe–C / Al–Si), visor `web/multifase.html`, "
             "controles sin solapamiento y verificación única (`make verify`).\n"
             "Visor en vivo: <https://amurlaniakea.github.io/phasemap/> · "
             "Multifase: <https://amurlaniakea.github.io/phasemap/multifase.html>\n")
    s = s.replace("# PHASEMAP\n", "# PHASEMAP\n" + block, 1)
    open(p, "w", encoding="utf-8").write(s)
    print("OK: README actualizado")

# 4) CHANGELOG
write("CHANGELOG.md", """# Changelog

## v0.2.0
- Fase 6: sistema Ag-Cu (nucleo, visor, tests, datos) y fix del lienzo eutectico en blanco.
- Fase 7: motor multifase N-fases, compuestos de linea (LineCompound) y deteccion de invariantes.
- Fase 7c: invariantes por margen entre fases; Fe-C muestra peritectico L+delta->gamma.
- Fase 8: visor multifase autonomo (web/multifase.html) para Fe-C y Al-Si; fix del solapamiento del panel de controles.
- Fase 9: limpieza de parches a scripts/legacy/, verificacion unica, Makefile, tests web y documentacion de release.
- Limites declarados: Al-Si necesita sublattice de dos subredes; eutectoide solido Fe-C pendiente.

## v0.1.0
- Fases 1-5: nucleo stdlib (hull convexo + Newton), 64 tests, datos/limites, visor Canvas 0-deps, CI y GitHub Pages.
""")

# 5) roadmap
write("docs/roadmap.md", """# Roadmap

- [x] Fase 1: nucleo termodinamico stdlib.
- [x] Fase 2: suite pytest analitica.
- [x] Fase 3: visor web Canvas 0-deps.
- [x] Fase 4: datos CSV + tabla de limites.
- [x] Fase 5: CI + GitHub Pages + metadatos.
- [x] Fase 6: Ag-Cu + fix lienzo eutectico.
- [x] Fase 7/7c: motor multifase + compuestos de linea + invariantes.
- [x] Fase 8: visor multifase + fix solapamiento controles.
- [x] Fase 9: release v0.2.0, limpieza y verificacion unica.
- [ ] Fase 10: sublattice Al-Si (dos subredes) para eutectico ~850 K / x_Si~0.12.
- [ ] Fase 11: eutectoide solido Fe-C (gamma -> alpha + Fe3C) y renderizado de invariantes solidos.
- [ ] Fase 12: contraste CALPHAD/SGTE y mas sistemas binarios.
""")

# 6) Makefile
write("Makefile", ".PHONY: test data verify serve\n\ntest:\n\tpython -m pytest -q\n\ndata:\n\tpython scripts/build_data.py\n\tpython scripts/build_data_fase7.py\n\nverify:\n\tpython scripts/verify_release.py\n\nserve:\n\tpython -m http.server 8000\n")

# 7) verificacion unica
write("scripts/verify_release.py", """#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Verificacion unica: tests + datos Fase 4 + datos Fase 7.
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cmds = [
    [sys.executable, "-m", "pytest", "-q"],
    [sys.executable, "scripts/build_data.py"],
    [sys.executable, "scripts/build_data_fase7.py"],
]
for c in cmds:
    print(">>", " ".join(c))
    r = subprocess.run(c, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(r.returncode)
print("OK: release verificada (tests + datos)")
""")

# 8) tests web (regresion de solapamiento y visor multifase)
write("tests/test_web.py", """# Fase 9: regresion web (sin dependencias externas, multifase y fix de controles).
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def test_web_files_exist():
    assert (ROOT / "web" / "index.html").exists()
    assert (ROOT / "web" / "multifase.html").exists()

def test_no_external_js():
    for name in ["index.html", "multifase.html"]:
        s = (ROOT / "web" / name).read_text(encoding="utf-8")
        assert "<script src=" not in s

def test_multifase_link():
    s = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    assert "multifase.html" in s

def test_controls_no_overlap():
    s = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    assert ".controls{position:static;max-height:none;overflow:visible}" in s

def test_multifase_engine():
    s = (ROOT / "web" / "multifase.html").read_text(encoding="utf-8")
    assert "function equilibrium" in s
    assert "Fe" in s
""")
print("OK: Fase 9 aplicada (release v0.2.0)")
