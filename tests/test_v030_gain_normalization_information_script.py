import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from src.audio_file_report.v030_levels_dynamics.gain_normalization_information import (
    analyze_gain_normalization_information,
)


class V030GainNormalizationInformationScriptTests(unittest.TestCase):
    def _write_stereo_wav(self, path: Path, left: np.ndarray, right: np.ndarray, sample_rate: int = 1000):
        interleaved = np.column_stack((left, right)).astype(np.int16).ravel()
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(interleaved.tobytes())

    def test_report_contains_gain_fields(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 10000, -10000, 0], dtype=np.int16)
            right = np.array([0, 8000, -8000, 0], dtype=np.int16)
            self._write_stereo_wav(p, left, right)

            report = analyze_gain_normalization_information(p)

        info = report["gain_normalization_information"]
        self.assertIn("per_channel_gain_preview", info)
        self.assertIn("linked_stereo_gain_preview", info)
        self.assertFalse(info["normalization_applied_to_source_audio"])

        left_values = info["per_channel_gain_preview"]["left"]
        keys = {
            "target_peak_dbfs",
            "current_peak_dbfs",
            "gain_required_db",
            "gain_required_linear",
            "preview_resulting_peak_dbfs",
            "would_clip_after_gain",
        }
        self.assertEqual(set(left_values.keys()), keys)

    def test_custom_target_changes_gain_and_clip_warning(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([0, 20000, -20000, 0], dtype=np.int16)
            right = left.copy()
            self._write_stereo_wav(p, left, right)

            report_safe = analyze_gain_normalization_information(p, target_peak_dbfs=-1.0)
            report_hot = analyze_gain_normalization_information(p, target_peak_dbfs=1.0)

        left_safe = report_safe["gain_normalization_information"]["per_channel_gain_preview"]["left"]
        left_hot = report_hot["gain_normalization_information"]["per_channel_gain_preview"]["left"]

        self.assertNotEqual(left_safe["gain_required_db"], left_hot["gain_required_db"])
        self.assertFalse(left_safe["would_clip_after_gain"])
        self.assertTrue(left_hot["would_clip_after_gain"])


if __name__ == "__main__":
    unittest.main()
