import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.audio_file_report.common import (
    EXIT_EMPTY,
    EXIT_INVALID_WAV,
    EXIT_NOT_FILE,
    EXIT_NOT_FOUND,
    EXIT_PERMISSION,
)

PROG = Path(__file__).resolve().parents[1] / "audio_report.py"


class ErrorCodeRegressionTests(unittest.TestCase):
    def run_cmd(self, args, env=None):
        return subprocess.run(
            [sys.executable, str(PROG), *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_missing_file_exit_code(self):
        res = self.run_cmd(["missing_file.wav"])
        self.assertEqual(res.returncode, EXIT_NOT_FOUND)
        self.assertIn("does not exist", res.stderr)

    def test_directory_path_exit_code(self):
        with tempfile.TemporaryDirectory() as td:
            res = self.run_cmd([td])
        self.assertEqual(res.returncode, EXIT_NOT_FILE)
        self.assertIn("is not a file", res.stderr)

    def test_empty_file_exit_code(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "empty.wav"
            p.write_bytes(b"")
            res = self.run_cmd([str(p)])
        self.assertEqual(res.returncode, EXIT_EMPTY)
        self.assertIn("empty", res.stderr.lower())

    def test_invalid_wav_exit_code(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.wav"
            p.write_bytes(b"notawav")
            res = self.run_cmd([str(p)])
        self.assertEqual(res.returncode, EXIT_INVALID_WAV)

    def test_permission_denied_exit_code(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "perm.wav"
            p.write_bytes(b"data")
            p.chmod(0)
            try:
                res = self.run_cmd([str(p)])
            finally:
                p.chmod(stat.S_IRUSR | stat.S_IWUSR)

        self.assertEqual(res.returncode, EXIT_PERMISSION)
        self.assertIn("permission denied", res.stderr.lower())

    def test_plotting_failure_returns_generic_error(self):
        test_audio = Path(__file__).resolve().parents[1] / "assets" / "audio" / "test_audio.wav"
        if not test_audio.exists():
            self.skipTest("assets/audio/test_audio.wav not present")

        with tempfile.TemporaryDirectory() as td:
            unsupported = Path(td) / "out.unsupported_extension"
            res = self.run_cmd([str(test_audio), "--plot-file", str(unsupported), "--overwrite"])

        self.assertEqual(res.returncode, 1)
        self.assertIn("Error: plotting failed:", res.stderr)

    def test_missing_runtime_dependency_error_path(self):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])

        with tempfile.TemporaryDirectory() as td:
            fake_site = Path(td) / "sitecustomize.py"
            fake_site.write_text(
                "import builtins\n"
                "_original_import = builtins.__import__\n"
                "def _fake_import(name, *args, **kwargs):\n"
                "    if name in {'numpy', 'matplotlib'}:\n"
                "        raise ImportError(name)\n"
                "    return _original_import(name, *args, **kwargs)\n"
                "builtins.__import__ = _fake_import\n"
            )
            env["PYTHONPATH"] = f"{td}:{env['PYTHONPATH']}"
            res = self.run_cmd(["--version"], env=env)

        self.assertEqual(res.returncode, 1)
        self.assertIn("Missing required dependency", res.stderr)


if __name__ == "__main__":
    unittest.main()
