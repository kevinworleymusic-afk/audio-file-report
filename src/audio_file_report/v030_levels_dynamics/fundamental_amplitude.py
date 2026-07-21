from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path
from typing import Any

import numpy as np

from .metrics import compute_level_metrics


def _decode_pcm_frames(raw: bytes, sample_width: int) -> np.ndarray:
    if sample_width == 1:
        # WAV 8-bit PCM is unsigned; center around zero for analysis.
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


def analyze_fundamental_amplitude(audio_path: Path) -> dict[str, Any]:
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

    per_channel: dict[str, dict[str, float | int]] = {}
    for idx in range(channel_count):
        name = _channel_name(idx, channel_count)
        channel_samples = samples_2d[:, idx]
        m = compute_level_metrics(channel_samples, sample_rate=sample_rate, bit_depth=bit_depth)
        per_channel[name] = {
            "sample_peak_linear": m.peak_linear,
            "sample_peak_dbfs": m.peak_dbfs,
            "headroom_below_0dbfs": m.headroom_db,
            "peak_to_peak_amplitude": m.peak_to_peak,
            "mean_absolute_amplitude": m.mean_absolute,
            "minimum_sample_value": m.min_sample,
            "maximum_sample_value": m.max_sample,
            "positive_peak_value": m.positive_peak,
            "negative_peak_value": m.negative_peak,
            "positive_negative_peak_asymmetry": m.positive_negative_peak_asymmetry,
            "peak_sample_position": m.peak_sample_index,
            "peak_time_seconds": m.peak_time_seconds,
        }

    return {
        "file": str(audio_path),
        "sample_rate_hz": sample_rate,
        "bit_depth": bit_depth,
        "channels": channel_count,
        "frames": frame_count,
        "fundamental_amplitude": per_channel,
    }


def _print_text_report(report: dict[str, Any]) -> None:
    print("FUNDAMENTAL AMPLITUDE REPORT (0.3.0 INITIAL)")
    print("-------------------------------------------")
    print(f"File: {Path(report['file']).name}")
    print(f"Sample rate: {report['sample_rate_hz']} Hz")
    print(f"Bit depth: {report['bit_depth']}-bit")
    print(f"Channels: {report['channels']}")
    print(f"Frames: {report['frames']:,}")

    for channel, values in report["fundamental_amplitude"].items():
        print("")
        print(f"[{channel}]")
        print(f"Sample peak (linear): {values['sample_peak_linear']:.9f}")
        print(f"Sample peak (dBFS): {values['sample_peak_dbfs']:.6f}")
        print(f"Headroom below 0 dBFS: {values['headroom_below_0dbfs']:.6f} dB")
        print(f"Peak-to-peak amplitude: {values['peak_to_peak_amplitude']:.9f}")
        print(f"Mean absolute amplitude: {values['mean_absolute_amplitude']:.9f}")
        print(f"Minimum sample value: {values['minimum_sample_value']:.9f}")
        print(f"Maximum sample value: {values['maximum_sample_value']:.9f}")
        print(f"Positive peak value: {values['positive_peak_value']:.9f}")
        print(f"Negative peak value: {values['negative_peak_value']:.9f}")
        print(
            "Positive/negative peak asymmetry: "
            f"{values['positive_negative_peak_asymmetry']:.9f}"
        )
        print(f"Peak sample position: {values['peak_sample_position']}")
        print(f"Peak time (seconds): {values['peak_time_seconds']:.9f}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute 0.3.0 fundamental amplitude metrics for each WAV channel."
        )
    )
    parser.add_argument("audio_file", type=Path, help="Path to WAV file")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a human-readable text report",
    )

    args = parser.parse_args()
    audio_path = args.audio_file.expanduser()

    report = analyze_fundamental_amplitude(audio_path)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_text_report(report)


if __name__ == "__main__":
    main()
