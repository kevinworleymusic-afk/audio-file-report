import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from src.audio_file_report.v030_levels_dynamics.dynamic_envelope import (
    analyze_dynamic_envelope,
)


class V030DynamicEnvelopeScriptTests(unittest.TestCase):
    def _write_stereo_wav(self, path: Path, left: np.ndarray, right: np.ndarray, sample_rate: int = 1000):
        interleaved = np.column_stack((left, right)).astype(np.int16).ravel()
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(interleaved.tobytes())

    def test_report_contains_dynamic_envelope_fields(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 8000, 12000, 0, -12000, -8000, 0, 4000], dtype=np.int16)
            right = np.array([0, 4000, 6000, 0, -6000, -4000, 0, 2000], dtype=np.int16)
            self._write_stereo_wav(p, left, right)

            report = analyze_dynamic_envelope(
                p,
                window_ms=2.0,
                hop_ms=1.0,
                level_change_threshold_db=3.0,
                sustained_min_duration_ms=0.0,
            )

        values = report["dynamic_envelope"]["left"]
        keys = {
            "envelope_window_duration_ms",
            "envelope_hop_duration_ms",
            "peak_envelope_linear",
            "peak_envelope_dbfs",
            "rms_envelope_linear",
            "rms_envelope_dbfs",
            "crest_factor_over_time_linear",
            "crest_factor_over_time_db",
            "envelope_time_seconds",
            "loudest_continuous_region",
            "quietest_active_region",
            "loudest_quietest_active_difference_db",
            "large_level_changes_count",
            "large_level_changes",
            "largest_upward_level_change",
            "largest_downward_level_change",
            "sustained_high_level_regions",
            "sustained_low_level_regions",
        }
        self.assertEqual(set(values.keys()), keys)
        self.assertEqual(len(values["peak_envelope_linear"]), len(values["envelope_time_seconds"]))
        self.assertEqual(len(values["rms_envelope_linear"]), len(values["envelope_time_seconds"]))

    def test_level_change_detection_and_sustained_regions(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([
                0,
                1000,
                1000,
                1000,
                28000,
                28000,
                28000,
                1000,
                1000,
                1000,
            ], dtype=np.int16)
            right = left.copy()
            self._write_stereo_wav(p, left, right, sample_rate=1000)

            report = analyze_dynamic_envelope(
                p,
                window_ms=2.0,
                hop_ms=1.0,
                level_change_threshold_db=6.0,
                sustained_high_threshold_dbfs=-4.0,
                sustained_low_threshold_dbfs=-28.0,
                sustained_min_duration_ms=2.0,
            )

        values = report["dynamic_envelope"]["left"]
        self.assertGreater(values["large_level_changes_count"], 0)
        self.assertGreaterEqual(len(values["sustained_high_level_regions"]), 1)
        self.assertGreaterEqual(len(values["sustained_low_level_regions"]), 1)


if __name__ == "__main__":
    unittest.main()
