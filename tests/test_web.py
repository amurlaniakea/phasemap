# Fase 9: regresion web (sin dependencias externas, multifase y fix de controles).
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
