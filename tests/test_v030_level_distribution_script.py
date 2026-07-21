import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from src.audio_file_report.v030_levels_dynamics.level_distribution import (
    analyze_level_distribution,
)


class V030LevelDistributionScriptTests(unittest.TestCase):
    def _write_stereo_wav(self, path: Path, left: np.ndarray, right: np.ndarray, sample_rate: int = 1000):
        interleaved = np.column_stack((left, right)).astype(np.int16).ravel()
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(interleaved.tobytes())

    def test_report_contains_level_distribution_fields(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 1000, 20000, 26000, 1000, 0], dtype=np.int16)
            right = np.array([0, 500, 12000, 14000, 500, 0], dtype=np.int16)
            self._write_stereo_wav(p, left, right)

            report = analyze_level_distribution(p)

        values = report["level_distribution"]["left"]
        self.assertIn("seconds_above_-3dbfs", values)
        self.assertIn("seconds_above_-6dbfs", values)
        self.assertIn("seconds_above_-12dbfs", values)
        self.assertIn("seconds_below_-40dbfs", values)
        self.assertIn("seconds_below_-60dbfs", values)
        self.assertIn("active_audio_percentage", values)
        self.assertIn("most_commonly_occupied_level_range", values)
        self.assertIn("level_histogram", values)

    def test_custom_thresholds_and_crossings_are_reported(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 0, 26000, 26000, 0, 26000, 0, 0], dtype=np.int16)
            right = left.copy()
            self._write_stereo_wav(p, left, right, sample_rate=1000)

            report = analyze_level_distribution(
                p,
                above_thresholds_dbfs=[-10.0],
                below_thresholds_dbfs=[-50.0],
                active_threshold_dbfs=-50.0,
                histogram_bin_width_db=6.0,
            )

        values = report["level_distribution"]["left"]
        self.assertIn("seconds_above_-10dbfs", values)
        self.assertIn("crossings_-10dbfs", values)
        self.assertIn("seconds_below_-50dbfs", values)
        self.assertIn("crossings_below_-50dbfs", values)
        self.assertGreater(values["crossings_-10dbfs"], 0)


if __name__ == "__main__":
    unittest.main()
