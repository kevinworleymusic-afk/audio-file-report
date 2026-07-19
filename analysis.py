import sys
from pathlib import Path
import numpy as np


def validate_audio_format(sample_width: int, channels: int) -> None:
    logger = __import__("logging").getLogger(__name__)
    if sample_width != 2:
        logger.debug("Unsupported sample width for analysis: %s", sample_width)
        print(
            "Error: Spectrum analysis currently only supports 16-bit audio files."
        )
        sys.exit(1)

    if channels != 2:
        logger.debug("Unsupported channel count for analysis: %s", channels)
        print(
            "Error: A stereo WAV file is required for left/right comparison."
        )
        sys.exit(1)


def calculate_duration(frame_count: int, sample_rate: int) -> float:
    return frame_count / sample_rate


def print_report(
    audio_path: Path,
    channels: int,
    sample_rate: int,
    bit_depth: int,
    frame_count: int,
    duration: float,
) -> None:
    print("AUDIO FILE REPORT")
    print("-----------------")
    print(f"File: {audio_path.name}")
    print(f"Channels: {channels}")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Bit depth: {bit_depth}-bit")
    print(f"Frames: {frame_count}")
    print(f"Duration: {duration:.2f} seconds")


def separate_stereo_channels(audio_data: bytes, channels: int):
    samples = np.frombuffer(
        audio_data,
        dtype="<i2",
    )

    samples = samples.reshape(-1, channels)

    left_channel = samples[:, 0].astype(float)
    right_channel = samples[:, 1].astype(float)

    return left_channel, right_channel


def calculate_spectrum(channel_data: np.ndarray, sample_rate: int):
    frame_count = len(channel_data)

    window = np.hanning(frame_count)
    windowed_audio = channel_data * window

    channel_fft = np.fft.rfft(windowed_audio)

    frequencies = np.fft.rfftfreq(
        frame_count,
        d=1.0 / sample_rate,
    )

    magnitude = np.abs(channel_fft)

    return frequencies, magnitude


def convert_spectra_to_db(
    left_magnitude: np.ndarray,
    right_magnitude: np.ndarray,
):
    reference = max(
        np.max(left_magnitude),
        np.max(right_magnitude),
    )

    left_db = 20 * np.log10(
        np.maximum(
            left_magnitude / reference,
            1e-12,
        )
    )

    right_db = 20 * np.log10(
        np.maximum(
            right_magnitude / reference,
            1e-12,
        )
    )

    return left_db, right_db
