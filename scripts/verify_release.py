#!/usr/bin/env python3
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
