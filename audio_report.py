#1. Imports

from os import path
import wave
from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
# audio_path = Path("test_audio.wav")
__version__ = "0.1.0"

# 1. Get the WAV filename supplied in Terminal.
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Analyze a stereo WAV file and display its metadata"
        "and left/right frequency spectra."
        )
    
    parser.add_argument(
        "audio_file", 
        type=Path,
        help="Path to the Stereo WAV file to analyze.")
    
    parser.add_argument(
        "--version",
        action="version",
        version="Audio File Report (__version__)")
    
    display_group = parser.add_mutually_exclusive_group()

    display_group.add_argument(
        "--brief",
        action="store_true",
        help="Display a one line summary."
    )

    display_group.add_argument(
        "--verbose",
        action="store_true",
        help="Display additional technical details."
    )

    display_group.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress normal report output."
    )
   
    display_group.add_argument(
        "--plot",
        choices=["show", "save", "both" , "none"],
        default="show",
        help="Display or save the frequency spectrum plot."
    )
    
    display_group.add_argument(
        "--plot-file",
        type=path,
        help="Create file name for saved file."
    )
    
    display_group.add_argument(
        "--output-dir",
        type=Path,
        help="Setting Folder Directory to save the file."
    )

    args = parser.parse_args()

    args.audio_file = args.audio_file.expanduser()

    return args

def create_default_plot_filename(audio_path):
        return f"{audio_path.stem}_stereo_spectrum.png"

# 2. Read the WAV header and raw audio data.
def read_wav_file(audio_path):
    with wave.open(str(audio_path), "rb") as audio_file:
        channels = audio_file.getnchannels()
        sample_rate = audio_file.getframerate()
        sample_width = audio_file.getsampwidth()
        frame_count = audio_file.getnframes()
        audio_data = audio_file.readframes(frame_count)

    return (
        channels,
        sample_rate,
        sample_width,
        frame_count,
        audio_data,
    )


# 3. Confirm that the file is currently supported.
def validate_audio_format(sample_width, channels):
    if sample_width != 2:
        print(
            "Spectrum analysis currently only supports "
            "16-bit audio files."
        )
        sys.exit(1)

    if channels != 2:
        print(
            "A stereo WAV file is required "
            "for left/right comparison."
        )
        sys.exit(1)


# 4. Calculate duration in seconds.
def calculate_duration(frame_count, sample_rate):
    return frame_count / sample_rate


# 5. Print the technical file report.
def print_report(
    audio_path,
    channels,
    sample_rate,
    bit_depth,
    frame_count,
    duration,
):
    print("AUDIO FILE REPORT")
    print("-----------------")
    print(f"File: {audio_path.name}")
    print(f"Channels: {channels}")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Bit depth: {bit_depth}-bit")
    print(f"Frames: {frame_count}")
    print(f"Duration: {duration:.2f} seconds")


# 6. Decode and separate the stereo samples.
def separate_stereo_channels(audio_data, channels):
    samples = np.frombuffer(
        audio_data,
        dtype="<i2",
    )

    samples = samples.reshape(-1, channels)

    left_channel = samples[:, 0].astype(float)
    right_channel = samples[:, 1].astype(float)

    return left_channel, right_channel


# 7. Calculate the spectrum of one channel.
def calculate_spectrum(channel_data, sample_rate):
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


# 8. Normalize both spectra and convert them to dB.
def convert_spectra_to_db(
    left_magnitude,
    right_magnitude,
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


# 9. Plot the left and right spectra.
def plot_stereo_spectrum(
    frequencies,
    left_db,
    right_db,
):
    frequency_range = (
        (frequencies >= 20)
        & (frequencies <= 20_000)
    )

    plt.figure(figsize=(10, 6))

    plt.semilogx(
        frequencies[frequency_range],
        left_db[frequency_range],
        label="Left Channel",
    )

    plt.semilogx(
        frequencies[frequency_range],
        right_db[frequency_range],
        label="Right Channel",
    )

    plt.title(
        "Left and Right Channel Frequency Spectrum"
    )
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Relative magnitude (dB)")

    plt.xlim(20, 20_000)
    plt.ylim(-120, 5)

    frequency_ticks = [
        20,
        50,
        100,
        200,
        500,
        1_000,
        2_000,
        5_000,
        10_000,
        20_000,
    ]

    frequency_labels = [
        "20",
        "50",
        "100",
        "200",
        "500",
        "1k",
        "2k",
        "5k",
        "10k",
        "20k",
    ]

    plt.xticks(
        frequency_ticks,
        frequency_labels,
    )

    plt.grid(
        which="both",
        linestyle="--",
        alpha=0.4,
    )

    plt.legend()
    plt.tight_layout()
    plt.show()


# 10. Coordinate the entire program.
def main():
    args = parse_arguments()
    audio_path = args.audio_file

    (
        channels,
        sample_rate,
        sample_width,
        frame_count,
        audio_data,
    ) = read_wav_file(audio_path)

    bit_depth = sample_width * 8

    duration = calculate_duration(
        frame_count,
        sample_rate,
    )

    print_report(
        audio_path,
        channels,
        sample_rate,
        bit_depth,
        frame_count,
        duration,
    )

    validate_audio_format(
        sample_width,
        channels,
    )

    (
        left_channel,
        right_channel,
    ) = separate_stereo_channels(
        audio_data,
        channels,
    )

    (
        frequencies,
        left_magnitude,
    ) = calculate_spectrum(
        left_channel,
        sample_rate,
    )

    (
        _,
        right_magnitude,
    ) = calculate_spectrum(
        right_channel,
        sample_rate,
    )

    (
        left_db,
        right_db,
    ) = convert_spectra_to_db(
        left_magnitude,
        right_magnitude,
    )

    plot_stereo_spectrum(
        frequencies,
        left_db,
        right_db,
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")

