import sys
import unittest
from unittest import mock

from src.audio_file_report.cli import parse_arguments


class CliArgumentMatrixTests(unittest.TestCase):
    def _parse(self, argv_tail):
        argv = ["audio_report.py", "assets/audio/test_audio.wav", *argv_tail]
        with mock.patch.object(sys, "argv", argv):
            return parse_arguments()

    def test_report_flags_remain_mutually_exclusive(self):
        matrix = [
            ["--brief", "--verbose"],
            ["--brief", "--quiet"],
            ["--verbose", "--quiet"],
        ]

        for args_tail in matrix:
            with self.subTest(args_tail=args_tail):
                with self.assertRaises(SystemExit) as exc:
                    self._parse(args_tail)
                self.assertNotEqual(exc.exception.code, 0)

    def test_report_flag_and_plot_mode_combinations_are_accepted(self):
        matrix = [
            ["--brief", "--plot", "none"],
            ["--verbose", "--plot", "save"],
            ["--quiet", "--plot", "both"],
            ["--verbose", "--plot-file", "custom.png"],
            ["--brief", "--output-dir", "artifacts/plots"],
        ]

        for args_tail in matrix:
            with self.subTest(args_tail=args_tail):
                args = self._parse(args_tail)
                self.assertIsNotNone(args)

    def test_report_format_explicitly_overrides_flag_mapping(self):
        args = self._parse(["--brief", "--report-format", "timed"])
        self.assertTrue(args.brief)
        self.assertEqual(args.report_format, "timed")

    def test_show_flag_overrides_plot_mode(self):
        args = self._parse(["--plot", "none", "--show"])
        self.assertEqual(args.plot, "show")

    def test_dpi_choice_overrides_numeric_dpi(self):
        args = self._parse(["--dpi", "72", "--dpi-choice", "print"])
        self.assertEqual(args.dpi, 300)


if __name__ == "__main__":
    unittest.main()
