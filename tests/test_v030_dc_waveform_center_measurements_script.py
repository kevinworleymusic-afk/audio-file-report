import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from src.audio_file_report.v030_levels_dynamics.dc_waveform_center_measurements import (
    analyze_dc_waveform_center_measurements,
)


class V030DcWaveformCenterMeasurementsScriptTests(unittest.TestCase):
    def _write_stereo_wav(self, path: Path, left: np.ndarray, right: np.ndarray, sample_rate: int = 1000):
        interleaved = np.column_stack((left, right)).astype(np.int16).ravel()
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(interleaved.tobytes())

    def test_report_contains_dc_fields(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([1000, 1000, -500, -500, 1000, -500], dtype=np.int16)
            right = left.copy()
            self._write_stereo_wav(p, left, right)

            report = analyze_dc_waveform_center_measurements(p, window_ms=2.0, hop_ms=1.0)

        values = report["dc_waveform_center_measurements"]["left"]
        keys = {
            "mean_sample_value",
            "dc_offset_normalized",
            "dc_offset_percentage",
            "dc_window_duration_ms",
            "dc_hop_duration_ms",
            "dc_offset_over_time_seconds",
            "dc_offset_over_time_normalized",
            "maximum_short_term_dc_offset_normalized",
            "time_of_maximum_short_term_dc_offset_seconds",
            "unusual_dc_threshold_percentage",
            "unusual_dc_offset_ranges",
            "positive_sample_count",
            "negative_sample_count",
            "positive_negative_sample_count_difference",
        }
        self.assertEqual(set(values.keys()), keys)

    def test_unusual_dc_ranges_detected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "stereo.wav"
            left = np.array([12000, 12000, 12000, -100, -100, -100], dtype=np.int16)
            right = left.copy()
            self._write_stereo_wav(p, left, right, sample_rate=1000)

            report = analyze_dc_waveform_center_measurements(
                p,
                window_ms=2.0,
                hop_ms=1.0,
                unusual_dc_threshold_percent=5.0,
            )

        values = report["dc_waveform_center_measurements"]["left"]
        self.assertGreaterEqual(len(values["unusual_dc_offset_ranges"]), 1)


if __name__ == "__main__":
    unittest.main()
