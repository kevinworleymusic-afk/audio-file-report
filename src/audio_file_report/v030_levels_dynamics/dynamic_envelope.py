from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path
from typing import Any

import numpy as np

from .metrics import compute_windowed_rms, dbfs_from_linear


def _decode_pcm_frames(raw: bytes, sample_width: int) -> np.ndarray:
    if sample_width == 1:
        return np.frombuffer(raw, dtype=np.uint8).astype(np.int16) - 128

    if sample_width == 2:
        return np.frombuffer(raw, dtype="<i2")

    if sample_width == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3)
        vals = (
            b[:, 0].astype(np.int32)
            | (b[:, 1].astype(np.int32) << 8)
            | (b[:, 2].astype(np.int32) << 16)
        )
        sign_bit = 1 << 23
        return (vals ^ sign_bit) - sign_bit

    if sample_width == 4:
        return np.frombuffer(raw, dtype="<i4")

    raise ValueError(f"Unsupported PCM sample width: {sample_width} bytes")


def _channel_name(index: int, channel_count: int) -> str:
    if channel_count == 1:
        return "mono"
    if channel_count == 2:
        return "left" if index == 0 else "right"
    return f"channel_{index + 1}"


def _find_contiguous_regions(mask: np.ndarray, sample_rate: int, starts: np.ndarray, window_size: int) -> list[dict[str, float | int]]:
    regions: list[dict[str, float | int]] = []
    if mask.size == 0:
        return regions

    i = 0
    while i < mask.size:
        if not mask[i]:
            i += 1
            continue

        start_i = i
        while i + 1 < mask.size and mask[i + 1]:
            i += 1
        end_i = i

        start_sample = int(starts[start_i])
        end_sample = int(starts[end_i] + window_size - 1)

        regions.append(
            {
                "start_window_index": int(start_i),
                "end_window_index": int(end_i),
                "start_time_seconds": float(start_sample / sample_rate),
                "end_time_seconds": float(end_sample / sample_rate),
                "duration_seconds": float((end_sample - start_sample + 1) / sample_rate),
                "window_count": int(end_i - start_i + 1),
            }
        )
        i += 1

    return regions


def _windowed_peak_envelope(channel_samples: np.ndarray, starts: np.ndarray, window_size: int, bit_depth: int) -> np.ndarray:
    scale = float(2 ** (bit_depth - 1))
    peaks: list[float] = []
    for start in starts.tolist():
        s = int(start)
        e = min(s + window_size, channel_samples.size)
        window = channel_samples[s:e]
        if window.size == 0:
            peaks.append(0.0)
        else:
            peaks.append(float(np.max(np.abs(window.astype(np.float64) / scale))))
    return np.array(peaks, dtype=np.float64)


def analyze_dynamic_envelope(
    audio_path: Path,
    window_ms: float = 50.0,
    hop_ms: float | None = None,
    active_threshold_dbfs: float = -60.0,
    level_change_threshold_db: float = 6.0,
    sustained_high_threshold_dbfs: float = -6.0,
    sustained_low_threshold_dbfs: float = -40.0,
    sustained_min_duration_ms: float = 200.0,
) -> dict[str, Any]:
    if window_ms <= 0:
        raise ValueError("window_ms must be > 0")
    if hop_ms is not None and hop_ms <= 0:
        raise ValueError("hop_ms must be > 0 when provided")
    if sustained_min_duration_ms < 0:
        raise ValueError("sustained_min_duration_ms must be >= 0")

    with wave.open(str(audio_path), "rb") as wf:
        channel_count = wf.getnchannels()
        sample_rate = wf.getframerate()
        sample_width = wf.getsampwidth()
        frame_count = wf.getnframes()
        comptype = wf.getcomptype()
        compname = wf.getcompname()

        if comptype != "NONE":
            raise ValueError(
                f"Unsupported WAV compression type: {comptype} ({compname}). "
                "Only uncompressed PCM is supported in this initial 0.3.0 script."
            )

        raw = wf.readframes(frame_count)

    interleaved = _decode_pcm_frames(raw, sample_width)
    if interleaved.size % channel_count != 0:
        raise ValueError("Decoded sample count does not align with channel count")

    samples_2d = interleaved.reshape(-1, channel_count)
    bit_depth = sample_width * 8

    window_size = max(1, int(round(sample_rate * (window_ms / 1000.0))))
    if hop_ms is None:
        hop_size = max(1, window_size // 2)
    else:
        hop_size = max(1, int(round(sample_rate * (hop_ms / 1000.0))))

    min_windows_for_sustained = max(
        1,
        int(np.ceil((sustained_min_duration_ms / 1000.0) * sample_rate / hop_size)),
    )

    per_channel: dict[str, dict[str, Any]] = {}
    for idx in range(channel_count):
        name = _channel_name(idx, channel_count)
        channel_samples = samples_2d[:, idx]

        starts, rms_linear = compute_windowed_rms(
            channel_samples,
            sample_rate=sample_rate,
            window_size=window_size,
            hop_size=hop_size,
            bit_depth=bit_depth,
        )
        rms_dbfs = np.array([dbfs_from_linear(v) for v in rms_linear], dtype=np.float64)
        peak_linear = _windowed_peak_envelope(channel_samples, starts, window_size, bit_depth)
        peak_dbfs = np.array([dbfs_from_linear(v) for v in peak_linear], dtype=np.float64)

        crest_linear = np.divide(
            peak_linear,
            np.maximum(rms_linear, 1e-12),
            out=np.zeros_like(peak_linear),
            where=np.ones_like(peak_linear, dtype=bool),
        )
        crest_db = np.array(
            [dbfs_from_linear(max(v, 1e-12)) for v in crest_linear],
            dtype=np.float64,
        )

        if rms_dbfs.size:
            loudest_idx = int(np.argmax(rms_dbfs))
            loudest_time = float(starts[loudest_idx] / sample_rate)
        else:
            loudest_idx = 0
            loudest_time = 0.0

        active_mask = rms_dbfs > active_threshold_dbfs
        if np.any(active_mask):
            active_indices = np.where(active_mask)[0]
            quietest_active_idx = int(active_indices[np.argmin(rms_dbfs[active_mask])])
            quietest_active_time = float(starts[quietest_active_idx] / sample_rate)
            loudest_quietest_diff = float(rms_dbfs[loudest_idx] - rms_dbfs[quietest_active_idx])
        else:
            quietest_active_idx = 0
            quietest_active_time = 0.0
            loudest_quietest_diff = 0.0

        delta_db = np.diff(rms_dbfs) if rms_dbfs.size > 1 else np.array([], dtype=np.float64)
        change_indices = np.where(np.abs(delta_db) >= level_change_threshold_db)[0]
        large_changes: list[dict[str, float | str]] = []
        for i_change in change_indices.tolist():
            d = float(delta_db[i_change])
            large_changes.append(
                {
                    "from_time_seconds": float(starts[i_change] / sample_rate),
                    "to_time_seconds": float(starts[i_change + 1] / sample_rate),
                    "delta_db": d,
                    "direction": "up" if d > 0 else "down",
                }
            )

        if delta_db.size:
            largest_up_idx = int(np.argmax(delta_db))
            largest_down_idx = int(np.argmin(delta_db))
            largest_up = {
                "from_time_seconds": float(starts[largest_up_idx] / sample_rate),
                "to_time_seconds": float(starts[largest_up_idx + 1] / sample_rate),
                "delta_db": float(delta_db[largest_up_idx]),
            }
            largest_down = {
                "from_time_seconds": float(starts[largest_down_idx] / sample_rate),
                "to_time_seconds": float(starts[largest_down_idx + 1] / sample_rate),
                "delta_db": float(delta_db[largest_down_idx]),
            }
        else:
            largest_up = {"from_time_seconds": 0.0, "to_time_seconds": 0.0, "delta_db": 0.0}
            largest_down = {"from_time_seconds": 0.0, "to_time_seconds": 0.0, "delta_db": 0.0}

        sustained_high = _find_contiguous_regions(rms_dbfs >= sustained_high_threshold_dbfs, sample_rate, starts, window_size)
        sustained_low = _find_contiguous_regions(rms_dbfs <= sustained_low_threshold_dbfs, sample_rate, starts, window_size)
        sustained_high = [r for r in sustained_high if int(r["window_count"]) >= min_windows_for_sustained]
        sustained_low = [r for r in sustained_low if int(r["window_count"]) >= min_windows_for_sustained]

        loudest_region = {
            "start_time_seconds": loudest_time,
            "end_time_seconds": float((starts[loudest_idx] + window_size - 1) / sample_rate) if rms_dbfs.size else 0.0,
            "duration_seconds": float(window_size / sample_rate) if rms_dbfs.size else 0.0,
            "window_index": loudest_idx,
            "rms_dbfs": float(rms_dbfs[loudest_idx]) if rms_dbfs.size else float(dbfs_from_linear(0.0)),
        }

        quietest_active_region = {
            "start_time_seconds": quietest_active_time,
            "end_time_seconds": float((starts[quietest_active_idx] + window_size - 1) / sample_rate) if np.any(active_mask) else 0.0,
            "duration_seconds": float(window_size / sample_rate) if np.any(active_mask) else 0.0,
            "window_index": quietest_active_idx,
            "rms_dbfs": float(rms_dbfs[quietest_active_idx]) if np.any(active_mask) else float(dbfs_from_linear(0.0)),
        }

        per_channel[name] = {
            "envelope_window_duration_ms": float(window_ms),
            "envelope_hop_duration_ms": float((hop_size / sample_rate) * 1000.0),
            "peak_envelope_linear": [float(v) for v in peak_linear.tolist()],
            "peak_envelope_dbfs": [float(v) for v in peak_dbfs.tolist()],
            "rms_envelope_linear": [float(v) for v in rms_linear.tolist()],
            "rms_envelope_dbfs": [float(v) for v in rms_dbfs.tolist()],
            "crest_factor_over_time_linear": [float(v) for v in crest_linear.tolist()],
            "crest_factor_over_time_db": [float(v) for v in crest_db.tolist()],
            "envelope_time_seconds": [float(i / sample_rate) for i in starts.tolist()],
            "loudest_continuous_region": loudest_region,
            "quietest_active_region": quietest_active_region,
            "loudest_quietest_active_difference_db": loudest_quietest_diff,
            "large_level_changes_count": int(len(large_changes)),
            "large_level_changes": large_changes,
            "largest_upward_level_change": largest_up,
            "largest_downward_level_change": largest_down,
            "sustained_high_level_regions": sustained_high,
            "sustained_low_level_regions": sustained_low,
        }

    return {
        "file": str(audio_path),
        "sample_rate_hz": sample_rate,
        "bit_depth": bit_depth,
        "channels": channel_count,
        "frames": frame_count,
        "dynamic_envelope": per_channel,
    }


def _print_text_report(report: dict[str, Any]) -> None:
    print("DYNAMIC ENVELOPE REPORT (0.3.0 INITIAL)")
    print("-------------------------------------")
    print(f"File: {Path(report['file']).name}")
    print(f"Sample rate: {report['sample_rate_hz']} Hz")
    print(f"Bit depth: {report['bit_depth']}-bit")
    print(f"Channels: {report['channels']}")
    print(f"Frames: {report['frames']:,}")

    for channel, values in report["dynamic_envelope"].items():
        print("")
        print(f"[{channel}]")
        print(f"Envelope windows: {len(values['envelope_time_seconds'])}")
        print(
            "Loudest active difference (dB): "
            f"{values['loudest_quietest_active_difference_db']:.6f}"
        )
        print(f"Large level changes: {values['large_level_changes_count']}")
        print(
            "Sustained high/low regions: "
            f"{len(values['sustained_high_level_regions'])}/"
            f"{len(values['sustained_low_level_regions'])}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute 0.3.0 dynamic-envelope metrics for each WAV channel."
        )
    )
    parser.add_argument("audio_file", type=Path, help="Path to WAV file")
    parser.add_argument(
        "--window-ms",
        type=float,
        default=50.0,
        help="Envelope window duration in milliseconds",
    )
    parser.add_argument(
        "--hop-ms",
        type=float,
        default=None,
        help="Envelope hop duration in milliseconds (default: half-window)",
    )
    parser.add_argument(
        "--active-threshold-dbfs",
        type=float,
        default=-60.0,
        help="Threshold that defines active audio in dBFS",
    )
    parser.add_argument(
        "--level-change-threshold-db",
        type=float,
        default=6.0,
        help="Threshold used to count large level changes in dB",
    )
    parser.add_argument(
        "--sustained-high-threshold-dbfs",
        type=float,
        default=-6.0,
        help="Threshold for sustained high-level regions in dBFS",
    )
    parser.add_argument(
        "--sustained-low-threshold-dbfs",
        type=float,
        default=-40.0,
        help="Threshold for sustained low-level regions in dBFS",
    )
    parser.add_argument(
        "--sustained-min-duration-ms",
        type=float,
        default=200.0,
        help="Minimum duration for sustained high/low regions in milliseconds",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a human-readable text report",
    )

    args = parser.parse_args()
    audio_path = args.audio_file.expanduser()

    report = analyze_dynamic_envelope(
        audio_path,
        window_ms=args.window_ms,
        hop_ms=args.hop_ms,
        active_threshold_dbfs=args.active_threshold_dbfs,
        level_change_threshold_db=args.level_change_threshold_db,
        sustained_high_threshold_dbfs=args.sustained_high_threshold_dbfs,
        sustained_low_threshold_dbfs=args.sustained_low_threshold_dbfs,
        sustained_min_duration_ms=args.sustained_min_duration_ms,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_text_report(report)


if __name__ == "__main__":
    main()
