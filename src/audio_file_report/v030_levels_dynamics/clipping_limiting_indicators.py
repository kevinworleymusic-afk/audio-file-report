from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path
from typing import Any

import numpy as np

from .metrics import detect_clipping_events


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


def _count_contiguous_true(mask: np.ndarray) -> int:
    if mask.size == 0:
        return 0
    starts = np.where(mask & ~np.roll(mask, 1))[0]
    if starts.size and mask[0]:
        return int(starts.size)
    if starts.size:
        return int(starts.size)
    return 1 if np.any(mask) else 0


def _max_true_run(mask: np.ndarray) -> int:
    max_run = 0
    run = 0
    for v in mask.tolist():
        if v:
            run += 1
            if run > max_run:
                max_run = run
        else:
            run = 0
    return max_run


def analyze_clipping_limiting_indicators(
    audio_path: Path,
    clipping_threshold_dbfs: float = -0.1,
    near_clipping_threshold_dbfs: float = -1.0,
    repeated_peak_min_run: int = 3,
) -> dict[str, Any]:
    if near_clipping_threshold_dbfs > clipping_threshold_dbfs:
        raise ValueError("near_clipping_threshold_dbfs must be <= clipping_threshold_dbfs")
    if repeated_peak_min_run < 2:
        raise ValueError("repeated_peak_min_run must be >= 2")

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
    full_scale = float(2 ** (bit_depth - 1))

    clipping_threshold_linear = float(10.0 ** (clipping_threshold_dbfs / 20.0))
    near_clipping_threshold_linear = float(10.0 ** (near_clipping_threshold_dbfs / 20.0))

    per_channel: dict[str, dict[str, Any]] = {}
    for idx in range(channel_count):
        name = _channel_name(idx, channel_count)
        normalized = samples_2d[:, idx].astype(np.float64) / full_scale
        abs_values = np.abs(normalized)
        total_samples = int(abs_values.size)

        clipping_mask = abs_values >= clipping_threshold_linear
        near_clipping_mask = abs_values >= near_clipping_threshold_linear
        positive_clipping_mask = normalized >= clipping_threshold_linear
        negative_clipping_mask = normalized <= -clipping_threshold_linear

        clipped_samples = int(np.sum(clipping_mask))
        near_clipping_samples = int(np.sum(near_clipping_mask))

        clip_events = detect_clipping_events(
            samples_2d[:, idx],
            sample_rate=sample_rate,
            threshold_dbfs=clipping_threshold_dbfs,
            bit_depth=bit_depth,
        )
        clip_event_count = int(len(clip_events))

        if clip_events:
            first_clip_time = float(clip_events[0].start_time_seconds)
            last_clip_time = float(clip_events[-1].end_time_seconds)
            longest = max(clip_events, key=lambda e: e.sample_count)
            longest_run_samples = int(longest.sample_count)
            longest_run_duration = float(longest.duration_seconds)
        else:
            first_clip_time = 0.0
            last_clip_time = 0.0
            longest_run_samples = 0
            longest_run_duration = 0.0

        peak_abs = float(np.max(abs_values)) if abs_values.size else 0.0
        repeated_peak_mask = abs_values == peak_abs
        repeated_peak_run = _max_true_run(repeated_peak_mask)
        has_repeated_identical_peak_values = repeated_peak_run >= repeated_peak_min_run

        peak_plateau_mask = abs_values >= max(peak_abs * 0.999, clipping_threshold_linear)
        flat_top_run = _max_true_run(peak_plateau_mask)
        possible_flat_topped_regions = flat_top_run >= repeated_peak_min_run

        heavy_limiting_score = 0
        if total_samples > 0 and (clipped_samples / total_samples) >= 0.01:
            heavy_limiting_score += 1
        if near_clipping_samples > clipped_samples:
            heavy_limiting_score += 1
        if has_repeated_identical_peak_values:
            heavy_limiting_score += 1
        if possible_flat_topped_regions:
            heavy_limiting_score += 1

        limiting_warning = (
            "Possible heavy limiting detected (heuristic): substantial clipping/near-clipping "
            "or repeated peak plateaus were found."
            if heavy_limiting_score >= 2
            else "No strong heavy-limiting pattern detected by current heuristic."
        )

        per_channel[name] = {
            "clipping_threshold_dbfs": float(clipping_threshold_dbfs),
            "near_clipping_threshold_dbfs": float(near_clipping_threshold_dbfs),
            "clipped_samples": clipped_samples,
            "clipped_sample_percentage": float((clipped_samples / max(total_samples, 1)) * 100.0),
            "clipping_event_count": clip_event_count,
            "positive_clipping_event_count": _count_contiguous_true(positive_clipping_mask),
            "negative_clipping_event_count": _count_contiguous_true(negative_clipping_mask),
            "first_clipping_time_seconds": first_clip_time,
            "last_clipping_time_seconds": last_clip_time,
            "longest_consecutive_clipping_run_samples": longest_run_samples,
            "longest_consecutive_clipping_run_duration_seconds": longest_run_duration,
            "near_clipping_samples": near_clipping_samples,
            "has_repeated_identical_peak_values": bool(has_repeated_identical_peak_values),
            "possible_flat_topped_regions": bool(possible_flat_topped_regions),
            "heavy_limiting_warning": limiting_warning,
        }

    return {
        "file": str(audio_path),
        "sample_rate_hz": sample_rate,
        "bit_depth": bit_depth,
        "channels": channel_count,
        "frames": frame_count,
        "clipping_limiting_indicators": per_channel,
    }


def _print_text_report(report: dict[str, Any]) -> None:
    print("CLIPPING AND LIMITING REPORT (0.3.0 INITIAL)")
    print("-----------------------------------------")
    print(f"File: {Path(report['file']).name}")
    print(f"Sample rate: {report['sample_rate_hz']} Hz")
    print(f"Bit depth: {report['bit_depth']}-bit")
    print(f"Channels: {report['channels']}")
    print(f"Frames: {report['frames']:,}")

    for channel, values in report["clipping_limiting_indicators"].items():
        print("")
        print(f"[{channel}]")
        print(f"Clipped samples: {values['clipped_samples']}")
        print(f"Clipped percentage: {values['clipped_sample_percentage']:.6f}%")
        print(f"Clipping events: {values['clipping_event_count']}")
        print(f"Near-clipping samples: {values['near_clipping_samples']}")
        print(values["heavy_limiting_warning"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute 0.3.0 clipping and limiting indicators for each WAV channel."
        )
    )
    parser.add_argument("audio_file", type=Path, help="Path to WAV file")
    parser.add_argument(
        "--clipping-threshold-dbfs",
        type=float,
        default=-0.1,
        help="Threshold used to classify clipped samples in dBFS",
    )
    parser.add_argument(
        "--near-clipping-threshold-dbfs",
        type=float,
        default=-1.0,
        help="Threshold used to classify near-clipping samples in dBFS",
    )
    parser.add_argument(
        "--repeated-peak-min-run",
        type=int,
        default=3,
        help="Minimum contiguous run length for repeated-peak/flat-top heuristics",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a human-readable text report",
    )

    args = parser.parse_args()
    audio_path = args.audio_file.expanduser()

    report = analyze_clipping_limiting_indicators(
        audio_path,
        clipping_threshold_dbfs=args.clipping_threshold_dbfs,
        near_clipping_threshold_dbfs=args.near_clipping_threshold_dbfs,
        repeated_peak_min_run=args.repeated_peak_min_run,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_text_report(report)


if __name__ == "__main__":
    main()
