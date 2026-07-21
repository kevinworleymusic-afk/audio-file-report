#!/usr/bin/env python3
"""Shared launcher used by category wrappers to call the main CLI entrypoint."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run_category(category_name: str, argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    repo_root = Path(__file__).resolve().parents[1]
    main_script = repo_root / "audio_report.py"

    env = os.environ.copy()
    env["AFR_CATEGORY"] = category_name

    cmd = [sys.executable, str(main_script), *args]
    return subprocess.call(cmd, cwd=repo_root, env=env)
