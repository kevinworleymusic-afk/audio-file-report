from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path
from typing import Any

import numpy as np

from .metrics import compute_level_metrics, compute_windowed_rms, dbfs_from_linear


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


def analyze_rms_crest_factor(
    audio_path: Path,
    window_ms: float = 50.0,
    hop_ms: float | None = None,
    active_threshold_dbfs: float = -60.0,
) -> dict[str, Any]:
    if window_ms <= 0:
        raise ValueError("window_ms must be > 0")
    if hop_ms is not None and hop_ms <= 0:
        raise ValueError("hop_ms must be > 0 when provided")

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

    per_channel: dict[str, dict[str, Any]] = {}
    for idx in range(channel_count):
        name = _channel_name(idx, channel_count)
        channel_samples = samples_2d[:, idx]
        metrics = compute_level_metrics(channel_samples, sample_rate=sample_rate, bit_depth=bit_depth)

        starts, rms_linear = compute_windowed_rms(
            channel_samples,
            sample_rate=sample_rate,
            window_size=window_size,
            hop_size=hop_size,
            bit_depth=bit_depth,
        )
        rms_dbfs = np.array([dbfs_from_linear(v) for v in rms_linear], dtype=np.float64)

        if rms_linear.size:
            max_idx = int(np.argmax(rms_linear))
            max_rms_linear = float(rms_linear[max_idx])
            max_rms_dbfs = float(rms_dbfs[max_idx])
            time_of_max = float(starts[max_idx] / sample_rate)
            median_rms_linear = float(np.median(rms_linear))
            median_rms_dbfs = float(dbfs_from_linear(median_rms_linear))
            rms_range_linear = float(np.max(rms_linear) - np.min(rms_linear))
            rms_variability_linear_std = float(np.std(rms_linear))
        else:
            max_rms_linear = 0.0
            max_rms_dbfs = float(dbfs_from_linear(0.0))
            time_of_max = 0.0
            median_rms_linear = 0.0
            median_rms_dbfs = float(dbfs_from_linear(0.0))
            rms_range_linear = 0.0
            rms_variability_linear_std = 0.0

        active_mask = rms_dbfs > active_threshold_dbfs
        if np.any(active_mask):
            min_active_rms_linear = float(np.min(rms_linear[active_mask]))
            min_active_rms_dbfs = float(dbfs_from_linear(min_active_rms_linear))
        else:
            min_active_rms_linear = 0.0
            min_active_rms_dbfs = float(dbfs_from_linear(0.0))

        per_channel[name] = {
            "whole_file_rms_linear": metrics.rms_linear,
            "whole_file_rms_dbfs": metrics.rms_dbfs,
            "crest_factor_linear": metrics.crest_factor_linear,
            "crest_factor_db": metrics.crest_factor_db,
            "rms_window_duration_ms": window_ms,
            "rms_hop_duration_ms": float((hop_size / sample_rate) * 1000.0),
            "max_windowed_rms_linear": max_rms_linear,
            "max_windowed_rms_dbfs": max_rms_dbfs,
            "min_active_windowed_rms_linear": min_active_rms_linear,
            "min_active_windowed_rms_dbfs": min_active_rms_dbfs,
            "median_windowed_rms_linear": median_rms_linear,
            "median_windowed_rms_dbfs": median_rms_dbfs,
            "time_of_max_windowed_rms_seconds": time_of_max,
            "windowed_rms_range_linear": rms_range_linear,
            "rms_variability_linear_std": rms_variability_linear_std,
            "windowed_rms_time_seconds": [float(i / sample_rate) for i in starts.tolist()],
            "windowed_rms_linear": [float(v) for v in rms_linear.tolist()],
            "windowed_rms_dbfs": [float(v) for v in rms_dbfs.tolist()],
        }

    return {
        "file": str(audio_path),
        "sample_rate_hz": sample_rate,
        "bit_depth": bit_depth,
        "channels": channel_count,
        "frames": frame_count,
        "rms_crest_factor": per_channel,
    }


def _print_text_report(report: dict[str, Any]) -> None:
    print("RMS AND CREST FACTOR REPORT (0.3.0 INITIAL)")
    print("------------------------------------------")
    print(f"File: {Path(report['file']).name}")
    print(f"Sample rate: {report['sample_rate_hz']} Hz")
    print(f"Bit depth: {report['bit_depth']}-bit")
    print(f"Channels: {report['channels']}")
    print(f"Frames: {report['frames']:,}")

    for channel, values in report["rms_crest_factor"].items():
        print("")
        print(f"[{channel}]")
        print(f"Whole-file RMS (linear): {values['whole_file_rms_linear']:.9f}")
        print(f"Whole-file RMS (dBFS): {values['whole_file_rms_dbfs']:.6f}")
        print(f"Crest factor (linear): {values['crest_factor_linear']:.9f}")
        print(f"Crest factor (dB): {values['crest_factor_db']:.6f}")
        print(f"RMS window duration: {values['rms_window_duration_ms']:.3f} ms")
        print(f"RMS hop duration: {values['rms_hop_duration_ms']:.3f} ms")
        print(f"Max windowed RMS (linear): {values['max_windowed_rms_linear']:.9f}")
        print(f"Min active windowed RMS (linear): {values['min_active_windowed_rms_linear']:.9f}")
        print(f"Median windowed RMS (linear): {values['median_windowed_rms_linear']:.9f}")
        print(
            "Time of max windowed RMS (seconds): "
            f"{values['time_of_max_windowed_rms_seconds']:.9f}"
        )
        print(f"Windowed RMS range (linear): {values['windowed_rms_range_linear']:.9f}")
        print(f"RMS variability (std, linear): {values['rms_variability_linear_std']:.9f}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute 0.3.0 RMS and crest-factor metrics for each WAV channel."
        )
    )
    parser.add_argument("audio_file", type=Path, help="Path to WAV file")
    parser.add_argument(
        "--window-ms",
        type=float,
        default=50.0,
        help="RMS window duration in milliseconds",
    )
    parser.add_argument(
        "--hop-ms",
        type=float,
        default=None,
        help="RMS hop duration in milliseconds (default: half-window)",
    )
    parser.add_argument(
        "--active-threshold-dbfs",
        type=float,
        default=-60.0,
        help="Threshold for active-window RMS statistics in dBFS",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a human-readable text report",
    )

    args = parser.parse_args()
    audio_path = args.audio_file.expanduser()

    report = analyze_rms_crest_factor(
        audio_path,
        window_ms=args.window_ms,
        hop_ms=args.hop_ms,
        active_threshold_dbfs=args.active_threshold_dbfs,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_text_report(report)


if __name__ == "__main__":
    main()
