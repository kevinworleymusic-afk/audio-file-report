#!/usr/bin/env python3
"""Wrapper for 0.2.0 Reliable CLI and File Handling workstream."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from _run_main import run_category


if __name__ == "__main__":
    raise SystemExit(run_category("0.2.0 - Reliable CLI and File Handling"))
