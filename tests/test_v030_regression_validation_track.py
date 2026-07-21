import unittest

import numpy as np

from src.audio_file_report.v030_levels_dynamics.metrics import (
    compare_stereo_levels,
    compute_gain_preview,
    compute_level_metrics,
    compute_linked_stereo_gain_preview,
    compute_threshold_distribution,
    compute_windowed_rms,
    detect_clipping_events,
    detect_silence_regions,
)


class V030TruthFixtureRegressions(unittest.TestCase):
    def test_peak_rms_crest_headroom_fixture(self):
        samples = np.array([0, 16384, -16384, 0], dtype=np.int16)
        m = compute_level_metrics(samples, sample_rate=48000)

        self.assertAlmostEqual(m.peak_linear, 0.5, places=8)
        self.assertAlmostEqual(m.peak_dbfs, -6.020599913, places=6)
        self.assertAlmostEqual(m.headroom_db, 6.020599913, places=6)
        self.assertAlmostEqual(m.rms_linear, np.sqrt(0.125), places=8)
        self.assertAlmostEqual(m.rms_dbfs, -9.03089987, places=6)
        self.assertAlmostEqual(m.crest_factor_db, 3.010299956, places=6)

    def test_gain_preview_moves_peak_to_target(self):
        samples = np.array([16384, -16384], dtype=np.int16)
        preview = compute_gain_preview(samples, sample_rate=48000, target_dbfs=-1.0)

        self.assertAlmostEqual(preview.current_peak_dbfs, -6.020599913, places=6)
        self.assertAlmostEqual(preview.gain_db, 5.020599913, places=6)
        self.assertAlmostEqual(preview.preview_peak_dbfs, -1.0, places=5)


class V030ThresholdBoundaryRegressions(unittest.TestCase):
    def test_threshold_boundaries_around_minus_six_dbfs(self):
        thr = 10.0 ** (-6.0 / 20.0)
        samples = np.array([
            thr - 1e-5,
            thr,
            thr + 1e-5,
            0.0,
        ], dtype=np.float64)

        dist = compute_threshold_distribution(samples, sample_rate=4, thresholds_dbfs=[-6.0])

        self.assertAlmostEqual(dist["seconds_above_-6dbfs"], 0.5, places=8)
        self.assertAlmostEqual(dist["seconds_below_-6dbfs"], 0.75, places=8)
        self.assertAlmostEqual(dist["fraction_above_-6dbfs"], 0.5, places=8)

    def test_distribution_snapshot_fixture(self):
        samples = np.array([0, 32767, 0, -16384], dtype=np.int16)
        dist = compute_threshold_distribution(samples, sample_rate=4, thresholds_dbfs=[-6, -12])

        snapshot = {
            "seconds_above_-6dbfs": 0.25,
            "seconds_below_-6dbfs": 0.75,
            "fraction_above_-6dbfs": 0.25,
            "seconds_above_-12dbfs": 0.5,
            "seconds_below_-12dbfs": 0.5,
            "fraction_above_-12dbfs": 0.5,
        }

        for key, expected in snapshot.items():
            self.assertAlmostEqual(dist[key], expected, places=8)


class V030EventAndWindowRegressions(unittest.TestCase):
    def test_clipping_event_time_localization(self):
        samples = np.array([0, 32000, 32000, 0, -32768, -32768, 0], dtype=np.int16)
        events = detect_clipping_events(samples, sample_rate=1000, threshold_dbfs=-0.3)

        self.assertEqual(len(events), 2)

        self.assertEqual(events[0].start_index, 1)
        self.assertEqual(events[0].end_index, 2)
        self.assertAlmostEqual(events[0].start_time_seconds, 0.001, places=9)
        self.assertAlmostEqual(events[0].end_time_seconds, 0.002, places=9)
        self.assertAlmostEqual(events[0].duration_seconds, 0.002, places=9)

        self.assertEqual(events[1].start_index, 4)
        self.assertEqual(events[1].end_index, 5)

    def test_silence_region_localization_with_min_duration(self):
        samples = np.array([0.0, 0.0, 0.001, 0.2, 0.0, 0.0, 0.0], dtype=np.float64)
        events = detect_silence_regions(
            samples,
            sample_rate=1000,
            threshold_dbfs=-50.0,
            min_duration_seconds=0.002,
        )

        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].start_index, 0)
        self.assertEqual(events[0].end_index, 2)
        self.assertEqual(events[1].start_index, 4)
        self.assertEqual(events[1].end_index, 6)

    def test_windowed_rms_stable_tail_handling(self):
        samples = np.array([1, -1, 1, -1, 2, -2, 2, -2, 3, -3], dtype=np.float64)
        starts, rms = compute_windowed_rms(
            samples,
            sample_rate=1000,
            window_size=4,
            hop_size=3,
        )

        self.assertEqual(starts.tolist(), [0, 3, 6])
        self.assertEqual(len(rms), 3)
        self.assertAlmostEqual(rms[-1], np.sqrt((4 + 4 + 9 + 9) / 4), places=9)


class V030StereoComparisonRegressions(unittest.TestCase):
    def test_channel_relationship_and_linked_gain(self):
        left = np.array([32767, -32767, 0, 0], dtype=np.int16)
        right = np.array([16384, -16384, 0, 0], dtype=np.int16)

        cmp = compare_stereo_levels(left, right, sample_rate=48000)
        self.assertGreater(cmp.left_peak_dbfs, cmp.right_peak_dbfs)
        self.assertAlmostEqual(cmp.peak_difference_db, 6.0206, places=3)

        linked = compute_linked_stereo_gain_preview(
            left,
            right,
            sample_rate=48000,
            target_dbfs=-1.0,
        )
        self.assertAlmostEqual(linked.current_peak_dbfs, cmp.left_peak_dbfs, places=6)
        self.assertAlmostEqual(linked.preview_peak_dbfs, -1.0, places=5)


if __name__ == "__main__":
    unittest.main()
