from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path
from typing import Any

import numpy as np


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


def _find_unusual_dc_ranges(
    dc_values: np.ndarray,
    starts: np.ndarray,
    sample_rate: int,
    window_size: int,
    threshold_normalized: float,
) -> list[dict[str, float | int]]:
    mask = np.abs(dc_values) >= threshold_normalized
    ranges: list[dict[str, float | int]] = []
    if not np.any(mask):
        return ranges

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
        region_vals = dc_values[start_i : end_i + 1]

        ranges.append(
            {
                "start_time_seconds": float(start_sample / sample_rate),
                "end_time_seconds": float(end_sample / sample_rate),
                "duration_seconds": float((end_sample - start_sample + 1) / sample_rate),
                "window_count": int(end_i - start_i + 1),
                "max_abs_dc_offset_normalized": float(np.max(np.abs(region_vals))),
            }
        )
        i += 1

    return ranges


def analyze_dc_waveform_center_measurements(
    audio_path: Path,
    window_ms: float = 50.0,
    hop_ms: float | None = None,
    unusual_dc_threshold_percent: float = 1.0,
) -> dict[str, Any]:
    if window_ms <= 0:
        raise ValueError("window_ms must be > 0")
    if hop_ms is not None and hop_ms <= 0:
        raise ValueError("hop_ms must be > 0 when provided")
    if unusual_dc_threshold_percent < 0:
        raise ValueError("unusual_dc_threshold_percent must be >= 0")

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

    window_size = max(1, int(round(sample_rate * (window_ms / 1000.0))))
    if hop_ms is None:
        hop_size = max(1, window_size // 2)
    else:
        hop_size = max(1, int(round(sample_rate * (hop_ms / 1000.0))))

    threshold_norm = unusual_dc_threshold_percent / 100.0

    per_channel: dict[str, dict[str, Any]] = {}
    for idx in range(channel_count):
        name = _channel_name(idx, channel_count)
        channel_samples = samples_2d[:, idx]
        normalized = channel_samples.astype(np.float64) / full_scale

        mean_sample_value = float(np.mean(channel_samples.astype(np.float64)))
        dc_offset_normalized = float(np.mean(normalized))
        dc_offset_percentage = float(dc_offset_normalized * 100.0)

        starts: list[int] = []
        dc_over_time: list[float] = []
        pos_counts: list[int] = []
        neg_counts: list[int] = []

        start = 0
        n = normalized.size
        while start < n:
            end = min(start + window_size, n)
            window = normalized[start:end]
            raw_window = channel_samples[start:end]
            if window.size == 0:
                break
            starts.append(start)
            dc_over_time.append(float(np.mean(window)))
            pos_counts.append(int(np.sum(raw_window > 0)))
            neg_counts.append(int(np.sum(raw_window < 0)))
            if end == n:
                break
            start += hop_size

        starts_arr = np.array(starts, dtype=np.int64)
        dc_arr = np.array(dc_over_time, dtype=np.float64)

        if dc_arr.size:
            max_short_term_dc = float(np.max(np.abs(dc_arr)))
            max_short_term_idx = int(np.argmax(np.abs(dc_arr)))
            max_short_term_time = float(starts_arr[max_short_term_idx] / sample_rate)
        else:
            max_short_term_dc = 0.0
            max_short_term_time = 0.0

        unusual_ranges = _find_unusual_dc_ranges(
            dc_arr,
            starts_arr,
            sample_rate,
            window_size,
            threshold_norm,
        )

        positive_count = int(np.sum(channel_samples > 0))
        negative_count = int(np.sum(channel_samples < 0))

        per_channel[name] = {
            "mean_sample_value": mean_sample_value,
            "dc_offset_normalized": dc_offset_normalized,
            "dc_offset_percentage": dc_offset_percentage,
            "dc_window_duration_ms": float(window_ms),
            "dc_hop_duration_ms": float((hop_size / sample_rate) * 1000.0),
            "dc_offset_over_time_seconds": [float(v / sample_rate) for v in starts],
            "dc_offset_over_time_normalized": [float(v) for v in dc_over_time],
            "maximum_short_term_dc_offset_normalized": max_short_term_dc,
            "time_of_maximum_short_term_dc_offset_seconds": max_short_term_time,
            "unusual_dc_threshold_percentage": float(unusual_dc_threshold_percent),
            "unusual_dc_offset_ranges": unusual_ranges,
            "positive_sample_count": positive_count,
            "negative_sample_count": negative_count,
            "positive_negative_sample_count_difference": int(positive_count - negative_count),
        }

    return {
        "file": str(audio_path),
        "sample_rate_hz": sample_rate,
        "bit_depth": bit_depth,
        "channels": channel_count,
        "frames": frame_count,
        "dc_waveform_center_measurements": per_channel,
    }


def _print_text_report(report: dict[str, Any]) -> None:
    print("DC AND WAVEFORM-CENTER REPORT (0.3.0 INITIAL)")
    print("--------------------------------------------")
    print(f"File: {Path(report['file']).name}")
    print(f"Sample rate: {report['sample_rate_hz']} Hz")
    print(f"Bit depth: {report['bit_depth']}-bit")
    print(f"Channels: {report['channels']}")
    print(f"Frames: {report['frames']:,}")

    for channel, values in report["dc_waveform_center_measurements"].items():
        print("")
        print(f"[{channel}]")
        print(f"DC offset (%): {values['dc_offset_percentage']:.6f}")
        print(
            "Max short-term DC offset: "
            f"{values['maximum_short_term_dc_offset_normalized']:.9f}"
        )
        print(f"Unusual DC ranges: {len(values['unusual_dc_offset_ranges'])}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute 0.3.0 DC and waveform-center measurements for each WAV channel."
    )
    parser.add_argument("audio_file", type=Path, help="Path to WAV file")
    parser.add_argument(
        "--window-ms",
        type=float,
        default=50.0,
        help="DC measurement window duration in milliseconds",
    )
    parser.add_argument(
        "--hop-ms",
        type=float,
        default=None,
        help="DC measurement hop duration in milliseconds (default: half-window)",
    )
    parser.add_argument(
        "--unusual-dc-threshold-percent",
        type=float,
        default=1.0,
        help="Threshold used to identify unusual DC regions, in percent full-scale",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a human-readable text report",
    )

    args = parser.parse_args()
    audio_path = args.audio_file.expanduser()

    report = analyze_dc_waveform_center_measurements(
        audio_path,
        window_ms=args.window_ms,
        hop_ms=args.hop_ms,
        unusual_dc_threshold_percent=args.unusual_dc_threshold_percent,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_text_report(report)


if __name__ == "__main__":
    main()
