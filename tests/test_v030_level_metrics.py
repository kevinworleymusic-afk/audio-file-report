import unittest

import numpy as np

from src.audio_file_report.v030_levels_dynamics.metrics import compute_level_metrics


class V030LevelMetricsTests(unittest.TestCase):
    def test_constant_full_scale_signal(self):
        samples = np.full(8, 32767, dtype=np.int16)

        m = compute_level_metrics(samples, sample_rate=48000)

        self.assertAlmostEqual(m.peak_linear, 32767 / 32768, places=8)
        self.assertAlmostEqual(m.rms_linear, 32767 / 32768, places=8)
        self.assertAlmostEqual(m.crest_factor_linear, 1.0, places=6)
        self.assertAlmostEqual(m.crest_factor_db, 0.0, places=5)
        self.assertEqual(m.peak_sample_index, 0)
        self.assertEqual(m.peak_time_seconds, 0.0)

    def test_symmetric_peak_to_peak_and_min_max(self):
        samples = np.array([-32768, 0, 32767], dtype=np.int16)

        m = compute_level_metrics(samples, sample_rate=3)

        self.assertAlmostEqual(m.min_sample, -1.0, places=8)
        self.assertAlmostEqual(m.max_sample, 32767 / 32768, places=8)
        self.assertAlmostEqual(m.peak_to_peak, (32767 / 32768) - (-1.0), places=8)
        self.assertEqual(m.peak_sample_index, 0)
        self.assertEqual(m.peak_time_seconds, 0.0)

    def test_peak_time_is_index_over_sample_rate(self):
        samples = np.array([0, 1000, -2000, 3000, -32000], dtype=np.int16)

        m = compute_level_metrics(samples, sample_rate=1000)

        self.assertEqual(m.peak_sample_index, 4)
        self.assertAlmostEqual(m.peak_time_seconds, 0.004, places=9)

    def test_float_input_uses_full_scale_directly(self):
        samples = np.array([0.0, -0.5, 0.25, 0.75], dtype=np.float64)

        m = compute_level_metrics(samples, sample_rate=4)

        self.assertAlmostEqual(m.peak_linear, 0.75, places=9)
        self.assertAlmostEqual(m.positive_peak, 0.75, places=9)
        self.assertAlmostEqual(m.negative_peak, -0.5, places=9)

    def test_empty_signal_raises(self):
        with self.assertRaises(ValueError):
            compute_level_metrics(np.array([], dtype=np.int16), sample_rate=48000)

    def test_invalid_sample_rate_raises(self):
        with self.assertRaises(ValueError):
            compute_level_metrics(np.array([1, 2, 3], dtype=np.int16), sample_rate=0)


if __name__ == "__main__":
    unittest.main()
