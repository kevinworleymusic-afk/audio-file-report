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
    file_size: int = None,
    encoding: str = None,
    program_version: str = None,
    report_format: str = None,
    total_time: float = None,
    read_time: float = None,
    spectrum_time: float = None,
    plot_time: float = None,
) -> None:
    layout = report_format or "verbose"

    if layout == "compact":
        size_kb = f"{file_size/1024:.1f} KB" if file_size is not None else "unknown"
        if channels == 1:
            layout_name = "mono"
        elif channels == 2:
            layout_name = "stereo"
        else:
            layout_name = f"{channels}-channel"

        bitrate_str = "unknown"
        try:
            bits_per_second = sample_rate * bit_depth * channels
            kbps = bits_per_second / 1000.0
            if kbps >= 1000:
                mbps = kbps / 1000.0
                bitrate_str = f"{mbps:.2f} Mbps ({kbps:.0f} kbps)"
            else:
                bitrate_str = f"{kbps:.0f} kbps"
        except Exception:
            pass

        hh = int(duration // 3600)
        mm = int((duration % 3600) // 60)
        ss = int(duration % 60)

        print(
            f"{audio_path.name} | {size_kb} | {layout_name} | {sample_rate} Hz | {bit_depth}-bit | {frame_count:,} frames | {duration:.2f} s ({hh:02d}:{mm:02d}:{ss:02d}) | {bitrate_str}"
        )
        return

    if layout == "timed":
        header = f"Audio File Report - {program_version or 'unknown'}"
        print(header)
        print(40 * "-")
        print(f"File: {audio_path.name}")
        if file_size is not None:
            print(f"File size: {file_size:,} bytes")

        print(f"Duration: {duration:.2f} seconds ({int(duration//3600):02d}:{int((duration%3600)//60):02d}:{int(duration%60):02d})")

        try:
            bits_per_second = sample_rate * bit_depth * channels
            kbps = bits_per_second / 1000.0
            if kbps >= 1000:
                mbps = kbps / 1000.0
                print(f"Estimated uncompressed bitrate: {mbps:.2f} Mbps ({kbps:.0f} kbps)")
            else:
                print(f"Estimated uncompressed bitrate: {kbps:.0f} kbps")
        except Exception:
            pass

        if total_time is not None:
            print(f"Total analysis time: {total_time:.2f} seconds")
        else:
            print("Total analysis time: (not available)")

        parts = []
        if read_time is not None:
            parts.append(f"Read: {read_time:.2f} s")
        if spectrum_time is not None:
            parts.append(f"FFT: {spectrum_time:.2f} s")
        if plot_time is not None:
            parts.append(f"Plot: {plot_time:.2f} s")
        if parts:
            print("(" + ", ".join(parts) + ")")

        return

    print("AUDIO FILE REPORT")
    print("-----------------")
    if program_version:
        print(f"Program version: {program_version}")
        print("")
    print(f"File: {audio_path.name}")
    if channels == 1:
        layout = "mono"
    elif channels == 2:
        layout = "stereo"
    else:
        layout = f"{channels}-channel"

    print(f"Channels: {channels} ({layout})")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Sample width: {bit_depth//8} bytes")
    print(f"Bit depth: {bit_depth}-bit")
    print(f"Frames: {frame_count:,}")
    print(f"Duration: {duration:.2f} seconds")
    hrs = int(duration // 3600)
    mins = int((duration % 3600) // 60)
    secs = int(duration % 60)
    print(f"Duration (HH:MM:SS): {hrs:02d}:{mins:02d}:{secs:02d}")

    if file_size is not None:
        print(f"File size: {file_size:,} bytes")

    if encoding:
        print(f"Encoding: {encoding}")

    try:
        bits_per_second = sample_rate * bit_depth * channels
        kbps = bits_per_second / 1000.0
        if kbps >= 1000:
            mbps = kbps / 1000.0
            print(f"Estimated uncompressed bitrate: {mbps:.2f} Mbps ({kbps:.0f} kbps)")
        else:
            print(f"Estimated uncompressed bitrate: {kbps:.0f} kbps")
    except Exception:
        pass


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
