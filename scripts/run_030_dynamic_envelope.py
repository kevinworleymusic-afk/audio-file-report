#!/usr/bin/env python3
"""Run the 0.3.0 dynamic envelope analysis pathway."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from audio_file_report.v030_levels_dynamics.dynamic_envelope import main


if __name__ == "__main__":
    raise SystemExit(main())
