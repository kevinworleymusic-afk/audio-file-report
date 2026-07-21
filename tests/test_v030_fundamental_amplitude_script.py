import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from src.audio_file_report.v030_levels_dynamics.fundamental_amplitude import (
    analyze_fundamental_amplitude,
)


class V030FundamentalAmplitudeScriptTests(unittest.TestCase):
    def _write_stereo_wav(self, path: Path, left: np.ndarray, right: np.ndarray, sample_rate: int = 1000):
        interleaved = np.column_stack((left, right)).astype(np.int16).ravel()
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(interleaved.tobytes())

    def test_report_contains_all_fundamental_amplitude_fields(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 16384, -16384, 0], dtype=np.int16)
            right = np.array([0, 8192, -8192, 0], dtype=np.int16)
            self._write_stereo_wav(p, left, right)

            report = analyze_fundamental_amplitude(p)

        self.assertEqual(report["channels"], 2)
        self.assertEqual(report["bit_depth"], 16)
        self.assertEqual(report["frames"], 4)

        for ch in ("left", "right"):
            values = report["fundamental_amplitude"][ch]
            expected_keys = {
                "sample_peak_linear",
                "sample_peak_dbfs",
                "headroom_below_0dbfs",
                "peak_to_peak_amplitude",
                "mean_absolute_amplitude",
                "minimum_sample_value",
                "maximum_sample_value",
                "positive_peak_value",
                "negative_peak_value",
                "positive_negative_peak_asymmetry",
                "peak_sample_position",
                "peak_time_seconds",
            }
            self.assertEqual(set(values.keys()), expected_keys)

    def test_peak_position_and_time(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 1000, -32000, 0], dtype=np.int16)
            right = np.array([0, 0, 0, 0], dtype=np.int16)
            self._write_stereo_wav(p, left, right, sample_rate=2000)

            report = analyze_fundamental_amplitude(p)

        left_report = report["fundamental_amplitude"]["left"]
        self.assertEqual(left_report["peak_sample_position"], 2)
        self.assertAlmostEqual(left_report["peak_time_seconds"], 0.001, places=9)


if __name__ == "__main__":
    unittest.main()
