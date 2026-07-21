from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path
from typing import Any

import numpy as np

from .metrics import detect_silence_regions


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


def analyze_silence_dropout_analysis(
    audio_path: Path,
    silence_threshold_dbfs: float = -60.0,
    min_silence_duration_ms: float = 5.0,
    dropout_min_duration_ms: float = 5.0,
    dropout_max_duration_ms: float = 250.0,
) -> dict[str, Any]:
    if min_silence_duration_ms < 0:
        raise ValueError("min_silence_duration_ms must be >= 0")
    if dropout_min_duration_ms < 0:
        raise ValueError("dropout_min_duration_ms must be >= 0")
    if dropout_max_duration_ms < dropout_min_duration_ms:
        raise ValueError("dropout_max_duration_ms must be >= dropout_min_duration_ms")

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

    min_silence_duration_seconds = min_silence_duration_ms / 1000.0
    dropout_min_seconds = dropout_min_duration_ms / 1000.0
    dropout_max_seconds = dropout_max_duration_ms / 1000.0

    per_channel: dict[str, dict[str, Any]] = {}
    for idx in range(channel_count):
        name = _channel_name(idx, channel_count)
        channel_samples = samples_2d[:, idx]
        normalized_abs = np.abs(channel_samples.astype(np.float64) / full_scale)

        exact_silence_mask = channel_samples == 0
        exact_digital_silence_samples = int(np.sum(exact_silence_mask))

        silence_regions = detect_silence_regions(
            channel_samples,
            sample_rate=sample_rate,
            threshold_dbfs=silence_threshold_dbfs,
            min_duration_seconds=min_silence_duration_seconds,
            bit_depth=bit_depth,
        )

        total_silence_samples = int(sum(r.sample_count for r in silence_regions))
        total_samples = int(channel_samples.size)
        total_duration_seconds = float(total_samples / sample_rate)
        total_silence_duration_seconds = float(total_silence_samples / sample_rate)
        silence_percentage = float((total_silence_samples / max(total_samples, 1)) * 100.0)
        active_percentage = float(100.0 - silence_percentage)

        leading_silence_duration_seconds = 0.0
        trailing_silence_duration_seconds = 0.0

        if silence_regions and silence_regions[0].start_index == 0:
            leading_silence_duration_seconds = float(silence_regions[0].duration_seconds)
        if silence_regions and silence_regions[-1].end_index == total_samples - 1:
            trailing_silence_duration_seconds = float(silence_regions[-1].duration_seconds)

        interior_regions = [
            r for r in silence_regions if r.start_index > 0 and r.end_index < total_samples - 1
        ]

        if silence_regions:
            longest_region = max(silence_regions, key=lambda r: r.sample_count)
            first_region = silence_regions[0]
            last_region = silence_regions[-1]
            longest_silence_duration_seconds = float(longest_region.duration_seconds)
            first_silent_region_time_seconds = float(first_region.start_time_seconds)
            last_silent_region_time_seconds = float(last_region.end_time_seconds)
        else:
            longest_silence_duration_seconds = 0.0
            first_silent_region_time_seconds = 0.0
            last_silent_region_time_seconds = 0.0

        dropouts = []
        for r in interior_regions:
            if dropout_min_seconds <= r.duration_seconds <= dropout_max_seconds:
                dropouts.append(
                    {
                        "start_time_seconds": float(r.start_time_seconds),
                        "end_time_seconds": float(r.end_time_seconds),
                        "duration_seconds": float(r.duration_seconds),
                        "sample_count": int(r.sample_count),
                    }
                )

        trim_start_seconds = float(leading_silence_duration_seconds)
        trim_end_seconds = float(max(total_duration_seconds - trailing_silence_duration_seconds, 0.0))

        per_channel[name] = {
            "silence_threshold_dbfs": float(silence_threshold_dbfs),
            "minimum_silence_duration_ms": float(min_silence_duration_ms),
            "exact_digital_silence_samples": exact_digital_silence_samples,
            "exact_digital_silence_seconds": float(exact_digital_silence_samples / sample_rate),
            "leading_silence_seconds": leading_silence_duration_seconds,
            "trailing_silence_seconds": trailing_silence_duration_seconds,
            "interior_silent_region_count": int(len(interior_regions)),
            "longest_silent_region_seconds": longest_silence_duration_seconds,
            "first_silent_region_time_seconds": first_silent_region_time_seconds,
            "last_silent_region_time_seconds": last_silent_region_time_seconds,
            "total_silence_duration_seconds": total_silence_duration_seconds,
            "silence_percentage": silence_percentage,
            "non_silent_active_percentage": active_percentage,
            "possible_audio_dropouts_count": int(len(dropouts)),
            "possible_audio_dropouts": dropouts,
            "suggested_trim_start_seconds": trim_start_seconds,
            "suggested_trim_end_seconds": trim_end_seconds,
        }

    return {
        "file": str(audio_path),
        "sample_rate_hz": sample_rate,
        "bit_depth": bit_depth,
        "channels": channel_count,
        "frames": frame_count,
        "silence_dropout_analysis": per_channel,
    }


def _print_text_report(report: dict[str, Any]) -> None:
    print("SILENCE AND DROPOUT REPORT (0.3.0 INITIAL)")
    print("----------------------------------------")
    print(f"File: {Path(report['file']).name}")
    print(f"Sample rate: {report['sample_rate_hz']} Hz")
    print(f"Bit depth: {report['bit_depth']}-bit")
    print(f"Channels: {report['channels']}")
    print(f"Frames: {report['frames']:,}")

    for channel, values in report["silence_dropout_analysis"].items():
        print("")
        print(f"[{channel}]")
        print(f"Total silence: {values['total_silence_duration_seconds']:.6f} s")
        print(f"Silence percentage: {values['silence_percentage']:.3f}%")
        print(f"Detected dropouts: {values['possible_audio_dropouts_count']}")
        print(
            "Suggested trim: "
            f"start={values['suggested_trim_start_seconds']:.6f}s, "
            f"end={values['suggested_trim_end_seconds']:.6f}s"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute 0.3.0 silence and dropout analysis for each WAV channel."
        )
    )
    parser.add_argument("audio_file", type=Path, help="Path to WAV file")
    parser.add_argument(
        "--silence-threshold-dbfs",
        type=float,
        default=-60.0,
        help="Threshold used to classify silence in dBFS",
    )
    parser.add_argument(
        "--min-silence-duration-ms",
        type=float,
        default=5.0,
        help="Minimum duration for a silent region in milliseconds",
    )
    parser.add_argument(
        "--dropout-min-duration-ms",
        type=float,
        default=5.0,
        help="Minimum duration for dropout candidates in milliseconds",
    )
    parser.add_argument(
        "--dropout-max-duration-ms",
        type=float,
        default=250.0,
        help="Maximum duration for dropout candidates in milliseconds",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a human-readable text report",
    )

    args = parser.parse_args()
    audio_path = args.audio_file.expanduser()

    report = analyze_silence_dropout_analysis(
        audio_path,
        silence_threshold_dbfs=args.silence_threshold_dbfs,
        min_silence_duration_ms=args.min_silence_duration_ms,
        dropout_min_duration_ms=args.dropout_min_duration_ms,
        dropout_max_duration_ms=args.dropout_max_duration_ms,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_text_report(report)


if __name__ == "__main__":
    main()
