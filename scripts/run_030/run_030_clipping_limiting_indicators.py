#!/usr/bin/env python3
"""Run the 0.3.0 clipping/limiting analysis pathway."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from audio_file_report.v030_levels_dynamics.clipping_limiting_indicators import main


if __name__ == "__main__":
    raise SystemExit(main())
