from pathlib import Path
import logging
import traceback
import sys
import os
import platform


def _ensure_runtime_dependencies() -> None:
    """Ensure required runtime dependencies are available before proceeding."""
    missing = []

    for module_name in ("numpy", "matplotlib"):
        try:
            __import__(module_name)
        except Exception:
            missing.append(module_name)

    if missing:
        missing_list = ", ".join(missing)
        raise RuntimeError(
            "Missing required dependency(s): "
            f"{missing_list}. Install them with: python -m pip install -r requirements.txt"
        )


try:
    _ensure_runtime_dependencies()
except RuntimeError as exc:
    print(f"Error: {exc}", file=sys.stderr)
    sys.exit(1)

from .cli import parse_arguments, display_available, get_final_plot_path
from .fileio import validate_input_path, validate_wav_file, read_wav_file
from .analysis import (
    validate_audio_format,
    calculate_duration,
    print_report,
    separate_stereo_channels,
    calculate_spectrum,
    convert_spectra_to_db,
)
from .plotting import plot_stereo_spectrum


def _log_startup_environment(args):
    """Write detailed environment and dependency info to the debug log.

    This includes program version, resolved command-line options, Python
    executable and version, OS/platform details, working directory, PID,
    and key dependency versions (numpy, matplotlib)."""
    logger = logging.getLogger(__name__)
    try:
        from .common import __version__ as prog_version
    except Exception:
        prog_version = "unknown"

    logger.debug("Program version: %s", prog_version)
    try:
        logger.debug("Command-line args: %s", vars(args))
    except Exception:
        logger.debug("Command-line args: (unavailable)")

    logger.debug("Python executable: %s", sys.executable)
    logger.debug("Python version: %s", sys.version.replace("\n", " "))
    logger.debug("Platform: %s", platform.platform())
    logger.debug("Machine: %s", platform.machine())
    logger.debug("Processor: %s", platform.processor())
    logger.debug("Hostname: %s", platform.node())
    logger.debug("Working dir: %s", os.getcwd())
    logger.debug("Process id: %s", os.getpid())

    # Dependency versions
    for mod in ("numpy", "matplotlib", "scipy"):
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", str(m))
            logger.debug("Dependency %s: %s", mod, ver)
        except Exception:
            logger.debug("Dependency %s: not installed", mod)

    try:
        import matplotlib

        logger.debug("matplotlib backend: %s", matplotlib.get_backend())
    except Exception:
        logger.debug("matplotlib not available to report backend")



def main():
    args = parse_arguments()
    import time

    try:
        from .common import __version__ as prog_version
    except Exception:
        prog_version = "unknown"

    # Configure logging early based on CLI options.
    log_file = getattr(args, "log_file", None)
    root_logger = logging.getLogger()
    root_logger.handlers[:] = []
    # If a log file is requested, capture detailed debug logs there regardless
    # of the `--debug` console verbosity flag. Console remains concise by default.
    if log_file:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_level = logging.DEBUG if getattr(args, "debug", False) else logging.INFO
        root_logger.setLevel(root_level)

    if log_file:
        fh = logging.FileHandler(str(log_file), encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        root_logger.addHandler(fh)
        # Reduce extremely verbose matplotlib and related loggers in the debug file
        try:
            for mod in (
                "matplotlib",
                "matplotlib.pyplot",
                "matplotlib.backends",
                "matplotlib.font_manager",
                "matplotlib.ft2font",
            ):
                logging.getLogger(mod).setLevel(logging.WARNING)
        except Exception:
            pass

    # Log environment and dependency details to the debug log if present.
    if log_file or getattr(args, "debug", False):
        try:
            _log_startup_environment(args)
        except Exception:
            logging.getLogger(__name__).exception("Failed to log startup environment")

    # Keep console output concise by default (warnings/errors only unless --debug)
    ch = logging.StreamHandler()
    ch_level = logging.DEBUG if getattr(args, "debug", False) else logging.WARNING
    ch.setLevel(ch_level)
    ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    # By default strip exception tracebacks from console output so users see
    # concise error lines; keep full tracebacks in the file log. When `--debug`
    # is set, allow exception info to be printed to the console.
    class _StripExceptionInfoFilter(logging.Filter):
        def __init__(self, show_exc: bool = False):
            super().__init__()
            self.show_exc = show_exc

        def filter(self, record: logging.LogRecord) -> bool:
            if not self.show_exc:
                record.exc_info = None
                record.exc_text = None
            return True

    ch.addFilter(_StripExceptionInfoFilter(show_exc=getattr(args, "debug", False)))
    root_logger.addHandler(ch)

    # Validate input path early
    try:
        validate_input_path(args.audio_file, debug=getattr(args, "debug", False))
        # Validate WAV structure and readable content
        validate_wav_file(args.audio_file, debug=getattr(args, "debug", False))
    except Exception as exc:
        logger = logging.getLogger(__name__)
        # Log full traceback to log file when configured
        logger.exception("Validation failed")
        # Concise message to user
        print(f"Error: {exc}", file=sys.stderr)
        if getattr(args, "debug", False):
            traceback.print_exc()
        sys.exit(1)

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
                    sys.exit(0)
    audio_path = args.audio_file

    # capture a small set of file metadata efficiently
    try:
        file_size = audio_path.stat().st_size
    except Exception:
        file_size = None

    start_time = time.perf_counter()

    (
        channels,
        sample_rate,
        sample_width,
        frame_count,
        audio_data,
        comptype,
        compname,
    ) = read_wav_file(audio_path)

    bit_depth = sample_width * 8

    duration = calculate_duration(
        frame_count,
        sample_rate,
    )

    # Compose a simple encoding description
    encoding = None
    if comptype and compname:
        encoding = f"{comptype} ({compname})"

    # Log duration in both seconds and HH:MM:SS for debug traces
    hrs = int(duration // 3600)
    mins = int((duration % 3600) // 60)
    secs = int(duration % 60)
    logger = logging.getLogger(__name__)
    logger.debug("Duration: %.2f seconds (%02d:%02d:%02d)", duration, hrs, mins, secs)
    if file_size is not None:
        logger.debug("File size: %d bytes", file_size)
    if encoding:
        logger.debug("Encoding: %s", encoding)
    try:
        bits_per_second = sample_rate * bit_depth * channels
        kbps = bits_per_second / 1000.0
        if kbps >= 1000:
            mbps = kbps / 1000.0
            logger.debug(
                "Estimated uncompressed bitrate: %.2f Mbps (%.0f kbps)", mbps, kbps
            )
        else:
            logger.debug("Estimated uncompressed bitrate: %.0f kbps", kbps)
    except Exception:
        pass

    from .analysis import print_report as _print_report

    _print_report(
        audio_path,
        channels,
        sample_rate,
        bit_depth,
        frame_count,
        duration,
        file_size=file_size,
        encoding=encoding,
        program_version=prog_version,
        report_format=getattr(args, "report_format", None),
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
        try:
            plot_stereo_spectrum(
                frequencies,
                left_db,
                right_db,
                args.plot,
                plot_path,
                dpi=args.dpi,
                report_format=getattr(args, "report_format", None),
            )
        except Exception as exc:
            logger = logging.getLogger(__name__)
            logger.exception("Plotting failed")
            print(f"Error: plotting failed: {exc}", file=sys.stderr)
            if getattr(args, "debug", False):
                traceback.print_exc()
            sys.exit(1)

    total_time = time.perf_counter() - start_time
    # Log total analysis time to debug log and optionally print in verbose mode
    logging.getLogger(__name__).debug("Total analysis time: %.2f seconds", total_time)
    if getattr(args, "verbose", False):
        print(f"Total analysis time: {total_time:.2f} seconds")

    # If the user selected the timing-focused report, print it now with the total analysis time
    if getattr(args, "report_format", None) == "timed":
        try:
            _print_report(
                audio_path,
                channels,
                sample_rate,
                bit_depth,
                frame_count,
                duration,
                file_size=file_size,
                encoding=encoding,
                program_version=prog_version,
                report_format="timed",
                total_time=total_time,
            )
        except Exception:
            logging.getLogger(__name__).exception("Failed to print timed report")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")


