from pathlib import Path

from cli import parse_arguments, display_available, get_final_plot_path
from fileio import validate_input_path, validate_wav_file, read_wav_file
from analysis import (
    validate_audio_format,
    calculate_duration,
    print_report,
    separate_stereo_channels,
    calculate_spectrum,
    convert_spectra_to_db,
)
from plotting import plot_stereo_spectrum


def main():
    args = parse_arguments()

    # Validate input path early
    validate_input_path(args.audio_file, debug=getattr(args, "debug", False))
    # Validate WAV structure and readable content
    validate_wav_file(args.audio_file, debug=getattr(args, "debug", False))

    # Detect graphical display availability and adjust backend/plot mode.
    if not display_available():
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
                    import sys

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
    plot_path = get_final_plot_path(audio_path, args)

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

# 10. Coordinate the entire program.
def main():
    args = parse_arguments()
    # Validate input path early
    validate_input_path(args.audio_file, debug=getattr(args, "debug", False))
    # Validate WAV structure and readable content
    validate_wav_file(args.audio_file, debug=getattr(args, "debug", False))
    # Detect graphical display availability and adjust backend/plot mode.
    if not display_available():
        try:
            plt.switch_backend("Agg")
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
    plot_path = get_final_plot_path(audio_path, args)

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


