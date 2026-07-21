from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path
from typing import Any

import numpy as np

from .metrics import dbfs_from_linear


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


def _format_threshold_key(prefix: str, threshold_dbfs: float) -> str:
    return f"{prefix}_{threshold_dbfs:g}dbfs"


def analyze_level_distribution(
    audio_path: Path,
    above_thresholds_dbfs: list[float] | None = None,
    below_thresholds_dbfs: list[float] | None = None,
    active_threshold_dbfs: float = -60.0,
    histogram_floor_dbfs: float = -90.0,
    histogram_bin_width_db: float = 3.0,
) -> dict[str, Any]:
    if histogram_bin_width_db <= 0:
        raise ValueError("histogram_bin_width_db must be > 0")
    if histogram_floor_dbfs >= 0:
        raise ValueError("histogram_floor_dbfs must be < 0")

    if above_thresholds_dbfs is None:
        above_thresholds_dbfs = [-3.0, -6.0, -12.0]
    if below_thresholds_dbfs is None:
        below_thresholds_dbfs = [-40.0, -60.0]

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

    bins = np.arange(
        histogram_floor_dbfs,
        0.0 + histogram_bin_width_db,
        histogram_bin_width_db,
        dtype=np.float64,
    )
    if bins.size < 2:
        bins = np.array([histogram_floor_dbfs, 0.0], dtype=np.float64)

    per_channel: dict[str, dict[str, Any]] = {}
    for idx in range(channel_count):
        name = _channel_name(idx, channel_count)
        normalized = np.abs(samples_2d[:, idx].astype(np.float64) / full_scale)
        total_samples = float(max(normalized.size, 1))

        channel_result: dict[str, Any] = {
            "distribution_active_threshold_dbfs": float(active_threshold_dbfs),
            "histogram_floor_dbfs": float(histogram_floor_dbfs),
            "histogram_bin_width_db": float(histogram_bin_width_db),
        }

        for threshold_dbfs in above_thresholds_dbfs:
            threshold_lin = float(10.0 ** (threshold_dbfs / 20.0))
            mask = normalized >= threshold_lin
            count = int(np.sum(mask))
            crossings = int(np.sum(mask[1:] != mask[:-1])) if mask.size > 1 else 0
            channel_result[_format_threshold_key("seconds_above", threshold_dbfs)] = float(count / sample_rate)
            channel_result[_format_threshold_key("fraction_above", threshold_dbfs)] = float(count / total_samples)
            channel_result[_format_threshold_key("crossings", threshold_dbfs)] = crossings

        for threshold_dbfs in below_thresholds_dbfs:
            threshold_lin = float(10.0 ** (threshold_dbfs / 20.0))
            mask = normalized <= threshold_lin
            count = int(np.sum(mask))
            crossings = int(np.sum(mask[1:] != mask[:-1])) if mask.size > 1 else 0
            channel_result[_format_threshold_key("seconds_below", threshold_dbfs)] = float(count / sample_rate)
            channel_result[_format_threshold_key("fraction_below", threshold_dbfs)] = float(count / total_samples)
            channel_result[_format_threshold_key("crossings_below", threshold_dbfs)] = crossings

        active_lin = float(10.0 ** (active_threshold_dbfs / 20.0))
        active_count = int(np.sum(normalized > active_lin))
        channel_result["active_audio_fraction"] = float(active_count / total_samples)
        channel_result["active_audio_percentage"] = float((active_count / total_samples) * 100.0)

        db_values = np.array([dbfs_from_linear(v) for v in normalized], dtype=np.float64)
        db_values = np.maximum(db_values, histogram_floor_dbfs)
        hist_counts, bin_edges = np.histogram(db_values, bins=bins)

        if hist_counts.size:
            max_bin_idx = int(np.argmax(hist_counts))
            lo = float(bin_edges[max_bin_idx])
            hi = float(bin_edges[max_bin_idx + 1])
            most_common = {
                "range_dbfs": f"[{lo:.1f}, {hi:.1f})",
                "sample_count": int(hist_counts[max_bin_idx]),
                "fraction": float(hist_counts[max_bin_idx] / total_samples),
            }
        else:
            most_common = {"range_dbfs": "[0.0, 0.0)", "sample_count": 0, "fraction": 0.0}

        channel_result["most_commonly_occupied_level_range"] = most_common
        channel_result["level_histogram"] = {
            "bin_edges_dbfs": [float(v) for v in bin_edges.tolist()],
            "counts": [int(v) for v in hist_counts.tolist()],
        }

        per_channel[name] = channel_result

    return {
        "file": str(audio_path),
        "sample_rate_hz": sample_rate,
        "bit_depth": bit_depth,
        "channels": channel_count,
        "frames": frame_count,
        "level_distribution": per_channel,
    }


def _print_text_report(report: dict[str, Any]) -> None:
    print("LEVEL DISTRIBUTION REPORT (0.3.0 INITIAL)")
    print("----------------------------------------")
    print(f"File: {Path(report['file']).name}")
    print(f"Sample rate: {report['sample_rate_hz']} Hz")
    print(f"Bit depth: {report['bit_depth']}-bit")
    print(f"Channels: {report['channels']}")
    print(f"Frames: {report['frames']:,}")

    for channel, values in report["level_distribution"].items():
        print("")
        print(f"[{channel}]")
        print(
            "Above -6 dBFS: "
            f"{values.get('seconds_above_-6dbfs', 0.0):.6f} s "
            f"({values.get('fraction_above_-6dbfs', 0.0) * 100.0:.2f}%)"
        )
        print(
            "Below -60 dBFS: "
            f"{values.get('seconds_below_-60dbfs', 0.0):.6f} s "
            f"({values.get('fraction_below_-60dbfs', 0.0) * 100.0:.2f}%)"
        )
        print(f"Active audio: {values['active_audio_percentage']:.2f}%")
        print(
            "Most common level range: "
            f"{values['most_commonly_occupied_level_range']['range_dbfs']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute 0.3.0 level-distribution metrics for each WAV channel."
        )
    )
    parser.add_argument("audio_file", type=Path, help="Path to WAV file")
    parser.add_argument(
        "--above-threshold-dbfs",
        type=float,
        action="append",
        default=None,
        help="Threshold used for time-above and crossing calculations in dBFS (repeatable)",
    )
    parser.add_argument(
        "--below-threshold-dbfs",
        type=float,
        action="append",
        default=None,
        help="Threshold used for time-below and crossing calculations in dBFS (repeatable)",
    )
    parser.add_argument(
        "--active-threshold-dbfs",
        type=float,
        default=-60.0,
        help="Threshold that defines active audio percentage in dBFS",
    )
    parser.add_argument(
        "--histogram-floor-dbfs",
        type=float,
        default=-90.0,
        help="Lower floor for level histogram bins in dBFS",
    )
    parser.add_argument(
        "--histogram-bin-width-db",
        type=float,
        default=3.0,
        help="Histogram bin width in dB",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a human-readable text report",
    )

    args = parser.parse_args()
    audio_path = args.audio_file.expanduser()

    report = analyze_level_distribution(
        audio_path,
        above_thresholds_dbfs=args.above_threshold_dbfs,
        below_thresholds_dbfs=args.below_threshold_dbfs,
        active_threshold_dbfs=args.active_threshold_dbfs,
        histogram_floor_dbfs=args.histogram_floor_dbfs,
        histogram_bin_width_db=args.histogram_bin_width_db,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_text_report(report)


if __name__ == "__main__":
    main()
