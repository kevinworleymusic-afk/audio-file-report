#1. Imports

from os import path
import os
import matplotlib as mpl
import wave
from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt
import gc
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
        default="save",
        help="Display or save the frequency spectrum plot."
    )
    
    display_group.add_argument(
        "--plot-file",
        type=Path,
        help="Create file name for saved file."
    )
    
    display_group.add_argument(
        "--output-dir",
        type=Path,
        help="Setting Folder Directory to save the file."
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing plot files. By default files are renamed to avoid overwrite."
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI (dots per inch) for saved plots. Higher values increase resolution."
    )

    parser.add_argument(
        "--dpi-choice",
        choices=["screen", "screen-high", "print"],
        help="Preset DPI choices: 'screen' (~150), 'screen-high' (~200), 'print' (300). Overrides --dpi.",
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="Request interactive display (overrides default save).",
    )

    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="When no graphical display is detected, do not prompt; act as save.",
    )

    args = parser.parse_args()

    args.audio_file = args.audio_file.expanduser()

    # Map preset choices to concrete DPI values (preset overrides numeric --dpi)
    if getattr(args, "dpi_choice", None):
        dpi_map = {
            "screen": 150,
            "screen-high": 200,
            "print": 300,
        }
        args.dpi = dpi_map[args.dpi_choice]

    # If --show is requested, override default plot action
    if getattr(args, "show", False):
        args.plot = "show"

    return args

def create_default_plot_filename(audio_path):
        return f"{audio_path.stem}_stereo_spectrum.png"


def validate_input_path(audio_path: Path) -> None:
    """Confirm the supplied input path exists, is a file, and is readable.

    Exits the program with a clear message on failure.
    """
    if not audio_path.exists():
        print(f"Error: input path '{audio_path}' does not exist.")
        sys.exit(2)

    if not audio_path.is_file():
        print(f"Error: input path '{audio_path}' is not a file.")
        sys.exit(2)

    try:
        with open(audio_path, "rb"):
            pass
    except PermissionError:
        print(f"Error: permission denied reading '{audio_path}'.")
        sys.exit(2)


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
    plot_mode,
    plot_path,
    dpi=300,
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
    
    try:
        if plot_mode in ("save", "both"):
            plt.savefig(
                plot_path,
                dpi=dpi,
                bbox_inches="tight"
            )

            print(f"Plot saved to: {plot_path.resolve()}")

        if plot_mode in ("show", "both"):
            plt.show()
    finally:
        try:
            plt.close("all")
        except Exception:
            pass

        try:
            gc.collect()
        except Exception:
            pass

# 10. Coordinate the entire program.
def main():
    args = parse_arguments()
    # Validate input path early
    validate_input_path(args.audio_file)
    # Detect graphical display availability and adjust backend/plot mode.
    def _display_available():
        backend = mpl.get_backend().lower()
        non_gui = {"agg", "pdf", "svg", "ps", "cairo"}

        # If Matplotlib is already using a non-GUI backend, no display.
        if any(b in backend for b in non_gui):
            return False

        # On Linux, require DISPLAY or WAYLAND_DISPLAY to be set.
        if sys.platform.startswith("linux"):
            if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
                return False

        # Otherwise assume a display is available (covers macOS, Windows typical cases).
        return True

    if not _display_available():
        try:
            import matplotlib.pyplot as _plt
            _plt.switch_backend("Agg")
        except Exception:
            pass

        if args.plot in ("show", "both"):
            # If user explicitly requested --show or asked to skip prompts, don't ask interactively.
            if getattr(args, "show", False) or getattr(args, "no_prompt", False):
                print("No display detected — saving plot to file.")
                args.plot = "save"
            else:
                try:
                    resp = input(
                        "No graphical display detected — save plot to file instead? [Y/n]: "
                    ).strip().lower()
                except EOFError:
                    # non-interactive stdin; assume yes
                    resp = "y"

                if resp in ("", "y", "yes"):
                    print("No display detected — saving plot to file.")
                    args.plot = "save"
                else:
                    print("Aborting: graphical display required for '--plot show'.")
                    sys.exit(0)
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
    plot_path = None

    # Handle plot saving/showing options
    if args.plot in ("save", "both"):
        # Determine filename
        if args.plot_file is None:
            plot_filename = Path(create_default_plot_filename(audio_path))
        else:
            plot_filename = Path(args.plot_file)

        # Determine output directory (default to current directory)
        output_dir = args.output_dir or Path('.')
        output_dir.mkdir(parents=True, exist_ok=True)

        plot_path = output_dir / plot_filename

        # Prevent accidental overwrites unless user explicitly allowed it.
        if not args.overwrite:
            final_plot_path = plot_path
            counter = 1
            while final_plot_path.exists():
                stem = plot_path.stem
                suffix = plot_path.suffix
                final_plot_path = plot_path.with_name(f"{stem}_{counter}{suffix}")
                counter += 1

            if final_plot_path != plot_path:
                print(f"Target exists; saving as: {final_plot_path.resolve()}")

            plot_path = final_plot_path

    if args.plot != "none":
        plot_stereo_spectrum(
            frequencies,
            left_db,
            right_db,
            args.plot,
            plot_path,
            dpi=args.dpi,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")


