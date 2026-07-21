import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.audio_file_report.cli import get_final_plot_path, parse_arguments

PROG = Path(__file__).resolve().parents[1] / "audio_report.py"


class CliPlottingRegressionTests(unittest.TestCase):
    def test_verbose_and_plot_none_combination_is_accepted(self):
        test_argv = [
            "audio_report.py",
            "assets/audio/test_audio.wav",
            "--verbose",
            "--plot",
            "none",
        ]

        with mock.patch.object(sys, "argv", test_argv):
            args = parse_arguments()

        self.assertTrue(args.verbose)
        self.assertEqual(args.plot, "none")
        self.assertEqual(args.report_format, "verbose")

    def test_plot_file_nested_parent_directory_is_created(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "nested" / "plots" / "out.png"
            test_argv = [
                "audio_report.py",
                "assets/audio/test_audio.wav",
                "--plot-file",
                str(target),
            ]

            with mock.patch.object(sys, "argv", test_argv):
                args = parse_arguments()

            resolved = get_final_plot_path(Path("assets/audio/test_audio.wav"), args)
            self.assertEqual(resolved, target)
            self.assertTrue(target.parent.exists())

    def test_output_dir_combines_with_bare_plot_file(self):
        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td) / "artifacts" / "plots"
            test_argv = [
                "audio_report.py",
                "assets/audio/test_audio.wav",
                "--output-dir",
                str(out_dir),
                "--plot-file",
                "named.png",
            ]

            with mock.patch.object(sys, "argv", test_argv):
                args = parse_arguments()

            resolved = get_final_plot_path(Path("assets/audio/test_audio.wav"), args)
            self.assertEqual(resolved, out_dir / "named.png")
            self.assertTrue(out_dir.exists())

    def test_plotting_failure_no_unboundlocalerror(self):
        test_audio = Path(__file__).resolve().parents[1] / "assets" / "audio" / "test_audio.wav"
        if not test_audio.exists():
            self.skipTest("assets/audio/test_audio.wav not present")

        with tempfile.TemporaryDirectory() as td:
            bad_plot = Path(td) / "bad.unsupported_extension"
            res = subprocess.run(
                [
                    sys.executable,
                    str(PROG),
                    str(test_audio),
                    "--plot-file",
                    str(bad_plot),
                    "--overwrite",
                ],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Error: plotting failed:", res.stderr)
        self.assertNotIn("UnboundLocalError", res.stderr)


if __name__ == "__main__":
    unittest.main()
