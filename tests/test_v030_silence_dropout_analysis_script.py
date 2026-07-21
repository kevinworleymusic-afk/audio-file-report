import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from src.audio_file_report.v030_levels_dynamics.silence_dropout_analysis import (
    analyze_silence_dropout_analysis,
)


class V030SilenceDropoutAnalysisScriptTests(unittest.TestCase):
    def _write_stereo_wav(self, path: Path, left: np.ndarray, right: np.ndarray, sample_rate: int = 1000):
        interleaved = np.column_stack((left, right)).astype(np.int16).ravel()
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(interleaved.tobytes())

    def test_report_contains_silence_fields(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 0, 10000, 10000, 0, 0, 10000, 10000, 0, 0], dtype=np.int16)
            right = left.copy()
            self._write_stereo_wav(p, left, right)

            report = analyze_silence_dropout_analysis(
                p,
                silence_threshold_dbfs=-40.0,
                min_silence_duration_ms=1.0,
            )

        values = report["silence_dropout_analysis"]["left"]
        keys = {
            "silence_threshold_dbfs",
            "minimum_silence_duration_ms",
            "exact_digital_silence_samples",
            "exact_digital_silence_seconds",
            "leading_silence_seconds",
            "trailing_silence_seconds",
            "interior_silent_region_count",
            "longest_silent_region_seconds",
            "first_silent_region_time_seconds",
            "last_silent_region_time_seconds",
            "total_silence_duration_seconds",
            "silence_percentage",
            "non_silent_active_percentage",
            "possible_audio_dropouts_count",
            "possible_audio_dropouts",
            "suggested_trim_start_seconds",
            "suggested_trim_end_seconds",
        }
        self.assertEqual(set(values.keys()), keys)

    def test_leading_trailing_and_dropout_detection(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([
                0,
                0,
                0,
                10000,
                10000,
                0,
                0,
                10000,
                10000,
                0,
                0,
                0,
            ], dtype=np.int16)
            right = left.copy()
            self._write_stereo_wav(p, left, right, sample_rate=1000)

            report = analyze_silence_dropout_analysis(
                p,
                silence_threshold_dbfs=-40.0,
                min_silence_duration_ms=1.0,
                dropout_min_duration_ms=1.0,
                dropout_max_duration_ms=10.0,
            )

        values = report["silence_dropout_analysis"]["left"]
        self.assertGreater(values["leading_silence_seconds"], 0.0)
        self.assertGreater(values["trailing_silence_seconds"], 0.0)
        self.assertGreaterEqual(values["interior_silent_region_count"], 1)
        self.assertGreaterEqual(values["possible_audio_dropouts_count"], 1)


if __name__ == "__main__":
    unittest.main()
