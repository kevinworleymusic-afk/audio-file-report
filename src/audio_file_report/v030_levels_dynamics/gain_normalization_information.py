from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path
from typing import Any

import numpy as np

from .metrics import compute_gain_preview, compute_linked_stereo_gain_preview


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


def analyze_gain_normalization_information(
    audio_path: Path,
    target_peak_dbfs: float = -1.0,
) -> dict[str, Any]:
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

    per_channel: dict[str, dict[str, float | bool]] = {}
    channel_samples: list[np.ndarray] = []

    for idx in range(channel_count):
        name = _channel_name(idx, channel_count)
        samples = samples_2d[:, idx]
        channel_samples.append(samples)
        preview = compute_gain_preview(
            samples,
            sample_rate=sample_rate,
            target_dbfs=target_peak_dbfs,
            bit_depth=bit_depth,
        )
        per_channel[name] = {
            "target_peak_dbfs": float(target_peak_dbfs),
            "current_peak_dbfs": float(preview.current_peak_dbfs),
            "gain_required_db": float(preview.gain_db),
            "gain_required_linear": float(preview.gain_linear),
            "preview_resulting_peak_dbfs": float(preview.preview_peak_dbfs),
            "would_clip_after_gain": bool(preview.preview_peak_dbfs > 0.0),
        }

    if channel_count >= 2:
        linked_preview = compute_linked_stereo_gain_preview(
            channel_samples[0],
            channel_samples[1],
            sample_rate=sample_rate,
            target_dbfs=target_peak_dbfs,
            bit_depth=bit_depth,
        )
        linked = {
            "target_peak_dbfs": float(target_peak_dbfs),
            "controlling_channel_peak_dbfs": float(linked_preview.current_peak_dbfs),
            "linked_gain_required_db": float(linked_preview.gain_db),
            "linked_gain_required_linear": float(linked_preview.gain_linear),
            "linked_preview_resulting_peak_dbfs": float(linked_preview.preview_peak_dbfs),
            "would_clip_after_linked_gain": bool(linked_preview.preview_peak_dbfs > 0.0),
        }
    else:
        single = next(iter(per_channel.values()))
        linked = {
            "target_peak_dbfs": float(target_peak_dbfs),
            "controlling_channel_peak_dbfs": float(single["current_peak_dbfs"]),
            "linked_gain_required_db": float(single["gain_required_db"]),
            "linked_gain_required_linear": float(single["gain_required_linear"]),
            "linked_preview_resulting_peak_dbfs": float(single["preview_resulting_peak_dbfs"]),
            "would_clip_after_linked_gain": bool(single["would_clip_after_gain"]),
        }

    return {
        "file": str(audio_path),
        "sample_rate_hz": sample_rate,
        "bit_depth": bit_depth,
        "channels": channel_count,
        "frames": frame_count,
        "gain_normalization_information": {
            "per_channel_gain_preview": per_channel,
            "linked_stereo_gain_preview": linked,
            "normalization_applied_to_source_audio": False,
            "normalization_mode": "preview_only",
        },
    }


def _print_text_report(report: dict[str, Any]) -> None:
    print("GAIN AND NORMALIZATION REPORT (0.3.0 INITIAL)")
    print("--------------------------------------------")
    print(f"File: {Path(report['file']).name}")
    print(f"Sample rate: {report['sample_rate_hz']} Hz")
    print(f"Bit depth: {report['bit_depth']}-bit")
    print(f"Channels: {report['channels']}")
    print(f"Frames: {report['frames']:,}")

    info = report["gain_normalization_information"]
    for channel, values in info["per_channel_gain_preview"].items():
        print("")
        print(f"[{channel}]")
        print(f"Current peak (dBFS): {values['current_peak_dbfs']:.6f}")
        print(f"Required gain (dB): {values['gain_required_db']:.6f}")
        print(f"Preview resulting peak (dBFS): {values['preview_resulting_peak_dbfs']:.6f}")

    linked = info["linked_stereo_gain_preview"]
    print("")
    print("[linked_stereo]")
    print(f"Controlling peak (dBFS): {linked['controlling_channel_peak_dbfs']:.6f}")
    print(f"Linked gain (dB): {linked['linked_gain_required_db']:.6f}")
    print(f"Linked preview peak (dBFS): {linked['linked_preview_resulting_peak_dbfs']:.6f}")
    print("Normalization mode: preview only (source audio unchanged)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute 0.3.0 gain and normalization preview information for each WAV channel."
    )
    parser.add_argument("audio_file", type=Path, help="Path to WAV file")
    parser.add_argument(
        "--target-peak-dbfs",
        type=float,
        default=-1.0,
        help="Target sample-peak level in dBFS (default: -1.0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of a human-readable text report",
    )

    args = parser.parse_args()
    audio_path = args.audio_file.expanduser()

    report = analyze_gain_normalization_information(
        audio_path,
        target_peak_dbfs=args.target_peak_dbfs,
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_text_report(report)


if __name__ == "__main__":
    main()
