"""Ensure src/utf is on sys.path so shadow_thirst, thirsty_lang, tarl, tscg, etc.
are importable directly (without the utf. prefix) when running tests from this directory."""
from __future__ import annotations

import sys
from pathlib import Path

UTF_SRC = Path(__file__).resolve().parent.parent  # …/src/utf
SRC = UTF_SRC.parent                               # …/src
ROOT = SRC.parent                                  # …/Project-AI-main

for p in (ROOT, SRC, UTF_SRC):
    s = str(p)
    while s in sys.path:
        sys.path.remove(s)

for p in (ROOT, SRC, UTF_SRC):
    sys.path.insert(0, str(p))

for name in list(sys.modules):
    if name == "tarl" or name.startswith("tarl."):
        sys.modules.pop(name, None)
