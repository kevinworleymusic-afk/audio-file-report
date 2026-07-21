import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from src.audio_file_report.v030_levels_dynamics.clipping_limiting_indicators import (
    analyze_clipping_limiting_indicators,
)


class V030ClippingLimitingIndicatorsScriptTests(unittest.TestCase):
    def _write_stereo_wav(self, path: Path, left: np.ndarray, right: np.ndarray, sample_rate: int = 1000):
        interleaved = np.column_stack((left, right)).astype(np.int16).ravel()
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(interleaved.tobytes())

    def test_report_contains_clipping_fields(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 32767, 32767, -32768, -32768, 0], dtype=np.int16)
            right = np.array([0, 1000, -1000, 0, 1000, -1000], dtype=np.int16)
            self._write_stereo_wav(p, left, right)

            report = analyze_clipping_limiting_indicators(
                p,
                clipping_threshold_dbfs=-0.1,
                near_clipping_threshold_dbfs=-1.0,
            )

        values = report["clipping_limiting_indicators"]["left"]
        keys = {
            "clipping_threshold_dbfs",
            "near_clipping_threshold_dbfs",
            "clipped_samples",
            "clipped_sample_percentage",
            "clipping_event_count",
            "positive_clipping_event_count",
            "negative_clipping_event_count",
            "first_clipping_time_seconds",
            "last_clipping_time_seconds",
            "longest_consecutive_clipping_run_samples",
            "longest_consecutive_clipping_run_duration_seconds",
            "near_clipping_samples",
            "has_repeated_identical_peak_values",
            "possible_flat_topped_regions",
            "heavy_limiting_warning",
        }
        self.assertEqual(set(values.keys()), keys)

    def test_clipping_and_near_clipping_counts(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 32767, 30000, 32767, 0, -32768, -32768, 0], dtype=np.int16)
            right = left.copy()
            self._write_stereo_wav(p, left, right, sample_rate=1000)

            report = analyze_clipping_limiting_indicators(
                p,
                clipping_threshold_dbfs=-0.1,
                near_clipping_threshold_dbfs=-2.0,
            )

        values = report["clipping_limiting_indicators"]["left"]
        self.assertGreater(values["clipped_samples"], 0)
        self.assertGreater(values["near_clipping_samples"], values["clipped_samples"])
        self.assertGreaterEqual(values["clipping_event_count"], 1)


if __name__ == "__main__":
    unittest.main()
