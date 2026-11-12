#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# Fase 8: confina el sticky de .controls a >1280px (evita tapar 'tangente comun') + enlace.
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "web", "index.html")
s = open(P, encoding="utf-8").read(); o = s
if ".controls{position:static;max-height:none;overflow:visible}" not in s:
    s = s.replace("@media (max-width:1280px){",
                  "@media (max-width:1280px){\n  .controls{position:static;max-height:none;overflow:visible}", 1)
if 'href="multifase.html"' not in s:
    s = s.replace('<a href="#repo" class="nav-link" data-spy="repo">Repositorio</a>',
                  '<a href="#repo" class="nav-link" data-spy="repo">Repositorio</a>\n    <a href="multifase.html" class="nav-link">Multifase ↗</a>', 1)
if s != o: open(P, "w", encoding="utf-8").write(s)
print("OK: sticky confinado + enlace Multifase")
