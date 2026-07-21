from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


_EPSILON = 1e-12


@dataclass(frozen=True)
class LevelMetrics:
    peak_linear: float
    peak_dbfs: float
    headroom_db: float
    peak_to_peak: float
    mean_absolute: float
    min_sample: float
    max_sample: float
    positive_peak: float
    negative_peak: float
    peak_sample_index: int
    peak_time_seconds: float
    rms_linear: float
    rms_dbfs: float
    crest_factor_linear: float
    crest_factor_db: float


@dataclass(frozen=True)
class ClippingEvent:
    start_index: int
    end_index: int
    start_time_seconds: float
    end_time_seconds: float
    duration_seconds: float
    sample_count: int


@dataclass(frozen=True)
class SilenceRegion:
    start_index: int
    end_index: int
    start_time_seconds: float
    end_time_seconds: float
    duration_seconds: float
    sample_count: int


@dataclass(frozen=True)
class StereoLevelComparison:
    left_peak_dbfs: float
    right_peak_dbfs: float
    left_rms_dbfs: float
    right_rms_dbfs: float
    peak_difference_db: float
    rms_difference_db: float


@dataclass(frozen=True)
class GainPreview:
    target_dbfs: float
    current_peak_dbfs: float
    gain_db: float
    gain_linear: float
    preview_peak_dbfs: float


def _to_float_full_scale(samples: np.ndarray, bit_depth: Optional[int]) -> np.ndarray:
    if samples.size == 0:
        raise ValueError("samples must not be empty")

    if np.issubdtype(samples.dtype, np.integer):
        resolved_bit_depth = bit_depth or (samples.dtype.itemsize * 8)
        scale = float(2 ** (resolved_bit_depth - 1))
        return samples.astype(np.float64) / scale

    return samples.astype(np.float64)


def _to_dbfs(value: float) -> float:
    return 20.0 * np.log10(max(value, _EPSILON))


def normalize_to_full_scale(samples: np.ndarray, bit_depth: Optional[int] = None) -> np.ndarray:
    return _to_float_full_scale(samples, bit_depth)


def dbfs_from_linear(value: float) -> float:
    return float(_to_dbfs(value))


def compute_level_metrics(
    samples: np.ndarray,
    sample_rate: int,
    bit_depth: Optional[int] = None,
) -> LevelMetrics:
    """Compute fundamental 0.3.0 level metrics for one channel.

    Returns normalized metrics where full scale is 1.0 (dBFS reference).
    """
    if sample_rate <= 0:
        raise ValueError("sample_rate must be > 0")

    normalized = _to_float_full_scale(samples, bit_depth)

    abs_values = np.abs(normalized)
    peak_index = int(np.argmax(abs_values))
    peak_linear = float(abs_values[peak_index])
    peak_dbfs = float(_to_dbfs(peak_linear))
    headroom_db = float(-peak_dbfs)

    max_sample = float(np.max(normalized))
    min_sample = float(np.min(normalized))

    rms_linear = float(np.sqrt(np.mean(np.square(normalized))))
    rms_dbfs = float(_to_dbfs(rms_linear))

    crest_factor_linear = float(peak_linear / max(rms_linear, _EPSILON))
    crest_factor_db = float(peak_dbfs - rms_dbfs)

    return LevelMetrics(
        peak_linear=peak_linear,
        peak_dbfs=peak_dbfs,
        headroom_db=headroom_db,
        peak_to_peak=float(max_sample - min_sample),
        mean_absolute=float(np.mean(abs_values)),
        min_sample=min_sample,
        max_sample=max_sample,
        positive_peak=max_sample,
        negative_peak=min_sample,
        peak_sample_index=peak_index,
        peak_time_seconds=float(peak_index / sample_rate),
        rms_linear=rms_linear,
        rms_dbfs=rms_dbfs,
        crest_factor_linear=crest_factor_linear,
        crest_factor_db=crest_factor_db,
    )


def compute_gain_preview(
    samples: np.ndarray,
    sample_rate: int,
    target_dbfs: float = -1.0,
    bit_depth: Optional[int] = None,
) -> GainPreview:
    """Return gain needed to move current sample peak to target dBFS."""
    metrics = compute_level_metrics(samples, sample_rate=sample_rate, bit_depth=bit_depth)
    gain_db = float(target_dbfs - metrics.peak_dbfs)
    gain_linear = float(10.0 ** (gain_db / 20.0))
    preview_peak_linear = float(metrics.peak_linear * gain_linear)
    preview_peak_dbfs = float(_to_dbfs(preview_peak_linear))
    return GainPreview(
        target_dbfs=target_dbfs,
        current_peak_dbfs=metrics.peak_dbfs,
        gain_db=gain_db,
        gain_linear=gain_linear,
        preview_peak_dbfs=preview_peak_dbfs,
    )


def compute_windowed_rms(
    samples: np.ndarray,
    sample_rate: int,
    window_size: int,
    hop_size: int,
    bit_depth: Optional[int] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute RMS over overlapping windows.

    Returns `(start_indices, rms_values)` where both arrays are float64/int64.
    Tail handling is deterministic: a final shorter window is included if needed.
    """
    if sample_rate <= 0:
        raise ValueError("sample_rate must be > 0")
    if window_size <= 0:
        raise ValueError("window_size must be > 0")
    if hop_size <= 0:
        raise ValueError("hop_size must be > 0")

    normalized = _to_float_full_scale(samples, bit_depth)
    n = normalized.size
    starts: list[int] = []
    rms_values: list[float] = []

    start = 0
    while start < n:
        end = min(start + window_size, n)
        window = normalized[start:end]
        if window.size == 0:
            break
        rms = float(np.sqrt(np.mean(np.square(window))))
        starts.append(start)
        rms_values.append(rms)
        if end == n:
            break
        start += hop_size

    return np.array(starts, dtype=np.int64), np.array(rms_values, dtype=np.float64)


def compute_threshold_distribution(
    samples: np.ndarray,
    sample_rate: int,
    thresholds_dbfs: list[float],
    bit_depth: Optional[int] = None,
) -> dict[str, float]:
    """Return time-above and time-below metrics for threshold boundaries."""
    if sample_rate <= 0:
        raise ValueError("sample_rate must be > 0")
    normalized = _to_float_full_scale(samples, bit_depth)
    abs_values = np.abs(normalized)
    total = float(abs_values.size)

    result: dict[str, float] = {}
    for threshold_db in thresholds_dbfs:
        threshold_lin = float(10.0 ** (threshold_db / 20.0))
        above_count = float(np.sum(abs_values >= threshold_lin))
        below_count = float(np.sum(abs_values <= threshold_lin))
        result[f"seconds_above_{threshold_db:g}dbfs"] = above_count / sample_rate
        result[f"seconds_below_{threshold_db:g}dbfs"] = below_count / sample_rate
        result[f"fraction_above_{threshold_db:g}dbfs"] = above_count / max(total, 1.0)
    return result


def detect_clipping_events(
    samples: np.ndarray,
    sample_rate: int,
    threshold_dbfs: float = -0.1,
    bit_depth: Optional[int] = None,
) -> list[ClippingEvent]:
    """Detect contiguous clipping-like regions above threshold."""
    if sample_rate <= 0:
        raise ValueError("sample_rate must be > 0")
    normalized = _to_float_full_scale(samples, bit_depth)
    threshold_lin = float(10.0 ** (threshold_dbfs / 20.0))
    mask = np.abs(normalized) >= threshold_lin
    return _events_from_mask(mask, sample_rate, ClippingEvent)


def detect_silence_regions(
    samples: np.ndarray,
    sample_rate: int,
    threshold_dbfs: float = -60.0,
    min_duration_seconds: float = 0.0,
    bit_depth: Optional[int] = None,
) -> list[SilenceRegion]:
    """Detect contiguous low-level regions below threshold with minimum duration."""
    if sample_rate <= 0:
        raise ValueError("sample_rate must be > 0")
    normalized = _to_float_full_scale(samples, bit_depth)
    threshold_lin = float(10.0 ** (threshold_dbfs / 20.0))
    mask = np.abs(normalized) <= threshold_lin
    regions = _events_from_mask(mask, sample_rate, SilenceRegion)
    if min_duration_seconds <= 0:
        return regions
    return [r for r in regions if r.duration_seconds >= min_duration_seconds]


def _events_from_mask(mask: np.ndarray, sample_rate: int, cls):
    events = []
    n = mask.size
    i = 0
    while i < n:
        if not mask[i]:
            i += 1
            continue
        start = i
        while i + 1 < n and mask[i + 1]:
            i += 1
        end = i
        sample_count = end - start + 1
        start_time = start / sample_rate
        end_time = end / sample_rate
        duration = sample_count / sample_rate
        events.append(
            cls(
                start_index=start,
                end_index=end,
                start_time_seconds=float(start_time),
                end_time_seconds=float(end_time),
                duration_seconds=float(duration),
                sample_count=sample_count,
            )
        )
        i += 1
    return events


def compare_stereo_levels(
    left_samples: np.ndarray,
    right_samples: np.ndarray,
    sample_rate: int,
    bit_depth: Optional[int] = None,
) -> StereoLevelComparison:
    left = compute_level_metrics(left_samples, sample_rate=sample_rate, bit_depth=bit_depth)
    right = compute_level_metrics(right_samples, sample_rate=sample_rate, bit_depth=bit_depth)
    return StereoLevelComparison(
        left_peak_dbfs=left.peak_dbfs,
        right_peak_dbfs=right.peak_dbfs,
        left_rms_dbfs=left.rms_dbfs,
        right_rms_dbfs=right.rms_dbfs,
        peak_difference_db=left.peak_dbfs - right.peak_dbfs,
        rms_difference_db=left.rms_dbfs - right.rms_dbfs,
    )


def compute_linked_stereo_gain_preview(
    left_samples: np.ndarray,
    right_samples: np.ndarray,
    sample_rate: int,
    target_dbfs: float = -1.0,
    bit_depth: Optional[int] = None,
) -> GainPreview:
    left = compute_level_metrics(left_samples, sample_rate=sample_rate, bit_depth=bit_depth)
    right = compute_level_metrics(right_samples, sample_rate=sample_rate, bit_depth=bit_depth)
    controlling_peak_dbfs = max(left.peak_dbfs, right.peak_dbfs)
    gain_db = float(target_dbfs - controlling_peak_dbfs)
    gain_linear = float(10.0 ** (gain_db / 20.0))
    preview_peak_linear = float(max(left.peak_linear, right.peak_linear) * gain_linear)
    preview_peak_dbfs = float(_to_dbfs(preview_peak_linear))
    return GainPreview(
        target_dbfs=target_dbfs,
        current_peak_dbfs=controlling_peak_dbfs,
        gain_db=gain_db,
        gain_linear=gain_linear,
        preview_peak_dbfs=preview_peak_dbfs,
    )
