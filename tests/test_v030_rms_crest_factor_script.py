import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from src.audio_file_report.v030_levels_dynamics.rms_crest_factor import (
    analyze_rms_crest_factor,
)


class V030RmsCrestFactorScriptTests(unittest.TestCase):
    def _write_stereo_wav(self, path: Path, left: np.ndarray, right: np.ndarray, sample_rate: int = 1000):
        interleaved = np.column_stack((left, right)).astype(np.int16).ravel()
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(interleaved.tobytes())

    def test_report_contains_rms_and_windowed_fields(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 10000, -10000, 0, 12000, -12000], dtype=np.int16)
            right = np.array([0, 5000, -5000, 0, 6000, -6000], dtype=np.int16)
            self._write_stereo_wav(p, left, right)

            report = analyze_rms_crest_factor(p, window_ms=2.0, hop_ms=1.0)

        self.assertEqual(report["channels"], 2)
        values = report["rms_crest_factor"]["left"]
        keys = {
            "whole_file_rms_linear",
            "whole_file_rms_dbfs",
            "crest_factor_linear",
            "crest_factor_db",
            "rms_window_duration_ms",
            "rms_hop_duration_ms",
            "max_windowed_rms_linear",
            "max_windowed_rms_dbfs",
            "min_active_windowed_rms_linear",
            "min_active_windowed_rms_dbfs",
            "median_windowed_rms_linear",
            "median_windowed_rms_dbfs",
            "time_of_max_windowed_rms_seconds",
            "windowed_rms_range_linear",
            "rms_variability_linear_std",
            "windowed_rms_time_seconds",
            "windowed_rms_linear",
            "windowed_rms_dbfs",
        }
        self.assertEqual(set(values.keys()), keys)

    def test_window_configuration_changes_window_count(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 10000, -10000, 0, 12000, -12000, 0, 8000], dtype=np.int16)
            right = left.copy()
            self._write_stereo_wav(p, left, right, sample_rate=1000)

            report_default = analyze_rms_crest_factor(p, window_ms=4.0)
            report_small_hop = analyze_rms_crest_factor(p, window_ms=4.0, hop_ms=1.0)

        n_default = len(report_default["rms_crest_factor"]["left"]["windowed_rms_linear"])
        n_small_hop = len(report_small_hop["rms_crest_factor"]["left"]["windowed_rms_linear"])
        self.assertGreater(n_small_hop, n_default)


if __name__ == "__main__":
    unittest.main()
