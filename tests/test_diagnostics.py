import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROG = Path(__file__).resolve().parents[1] / "audio_report.py"

class DiagnosticsTests(unittest.TestCase):
    def run_cmd(self, args, cwd=None):
        cmd = [sys.executable, str(PROG)] + args
        res = subprocess.run(cmd, cwd=cwd or Path.cwd(), capture_output=True, text=True)
        return res

    def test_missing_file(self):
        res = self.run_cmd(["missing_file.wav"])
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("does not exist", res.stderr)

    def test_empty_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "empty.wav"
            p.write_bytes(b"")
            res = self.run_cmd([str(p)])
            self.assertEqual(res.returncode, 4)
            self.assertIn("empty", res.stderr)

    def test_bad_wav(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.wav"
            p.write_bytes(b"notawav")
            res = self.run_cmd([str(p)])
            self.assertEqual(res.returncode, 6)
            self.assertIn("unexpected end of file", res.stderr.lower() or res.stderr.lower())

    def test_permission_denied(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "perm.wav"
            p.write_bytes(b"data")
            # remove all permissions
            p.chmod(0)
            try:
                res = self.run_cmd([str(p)])
                self.assertEqual(res.returncode, 3)
                self.assertIn("permission denied", res.stderr.lower())
            finally:
                # restore so temp dir can be cleaned
                p.chmod(stat.S_IWUSR | stat.S_IRUSR)

    def test_missing_runtime_dependencies_message(self):
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])

        with tempfile.TemporaryDirectory() as td:
            fake_site = Path(td) / "sitecustomize.py"
            fake_site.write_text(
                "import builtins\n"
                "import importlib\n"
                "_original_import = builtins.__import__\n"
                "def _fake_import(name, *args, **kwargs):\n"
                "    if name in {'numpy', 'matplotlib'}:\n"
                "        raise ImportError(name)\n"
                "    return _original_import(name, *args, **kwargs)\n"
                "builtins.__import__ = _fake_import\n"
            )
            env["PYTHONPATH"] = f"{td}:{env['PYTHONPATH']}"
            res = subprocess.run(
                [sys.executable, str(PROG), "--version"],
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("Missing required dependency", res.stderr)
            self.assertIn("python -m pip install -r requirements.txt", res.stderr)

    def test_logfile_startup_header(self):
        # Uses existing test_audio.wav in repo
        test_audio = Path(__file__).resolve().parents[1] / "test_audio.wav"
        if not test_audio.exists():
            self.skipTest("test_audio.wav not present")
        with tempfile.TemporaryDirectory() as td:
            logfile = Path(td) / "debug_test.log"
            res = self.run_cmd([str(test_audio), "--log-file", str(logfile)])
            self.assertEqual(res.returncode, 0)
            text = logfile.read_text()
            self.assertIn("Program version", text)
            self.assertIn("matplotlib backend", text)

    def test_metadata_in_log(self):
        test_audio = Path(__file__).resolve().parents[1] / "test_audio.wav"
        if not test_audio.exists():
            self.skipTest("test_audio.wav not present")
        with tempfile.TemporaryDirectory() as td:
            logfile = Path(td) / "debug_meta.log"
            res = self.run_cmd([str(test_audio), "--log-file", str(logfile)])
            self.assertEqual(res.returncode, 0)
            text = logfile.read_text()
            # Duration HH:MM:SS
            self.assertRegex(text, r"Duration: .*\(\d{2}:\d{2}:\d{2}\)")
            self.assertIn("File size:", text)
            self.assertIn("Encoding:", text)
            self.assertIn("Estimated uncompressed bitrate", text)

if __name__ == "__main__":
    unittest.main()
