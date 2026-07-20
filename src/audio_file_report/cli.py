import argparse
import os
import sys
from pathlib import Path
from typing import Optional

import matplotlib as mpl
import matplotlib.pyplot as plt

from .common import __version__


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a stereo WAV file and display its metadata "
            "and left/right frequency spectra."
        )
    )

    parser.add_argument(
        "audio_file",
        type=Path,
        help="Path to the Stereo WAV file to analyze.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Audio File Report {__version__}",
    )

    display_group = parser.add_mutually_exclusive_group()

    display_group.add_argument(
        "--brief",
        action="store_true",
        help="Display a one line summary.",
    )

    display_group.add_argument(
        "--verbose",
        action="store_true",
        help="Display additional technical details.",
    )

    display_group.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress normal report output.",
    )

    display_group.add_argument(
        "--plot",
        choices=["show", "save", "both", "none"],
        default="save",
        help="Display or save the frequency spectrum plot.",
    )

    display_group.add_argument(
        "--plot-file",
        type=Path,
        help="Create file name for saved file.",
    )

    display_group.add_argument(
        "--output-dir",
        type=Path,
        help="Setting Folder Directory to save the file.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Allow overwriting existing plot files. By default files are renamed "
            "to avoid overwrite."
        ),
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI (dots per inch) for saved plots. Higher values increase resolution.",
    )

    parser.add_argument(
        "--dpi-choice",
        choices=["screen", "screen-high", "print"],
        help=(
            "Preset DPI choices: 'screen' (~150), 'screen-high' (~200), 'print' (300). "
            "Overrides --dpi."
        ),
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug information (including validation diagnostics).",
    )

    parser.add_argument(
        "--report-format",
        choices=["compact", "verbose", "timed"],
        help=(
            "Choose the metadata report layout: 'compact' for a one-line/compact "
            "summary, 'verbose' for grouped details, or 'timed' to emphasize timing "
            "information. If omitted, `--brief`/`--verbose` flags control output."
        ),
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

    parser.add_argument(
        "--log-file",
        type=Path,
        help="Path to a file to write detailed logs (debug + tracebacks).",
    )

    args = parser.parse_args()

    args.audio_file = args.audio_file.expanduser()

    # Map preset choices to concrete DPI values (preset overrides numeric --dpi)
    if getattr(args, "dpi_choice", None):
        dpi_map = {"screen": 150, "screen-high": 200, "print": 300}
        args.dpi = dpi_map[args.dpi_choice]

    # If --show is requested, override default plot action
    if getattr(args, "show", False):
        args.plot = "show"

    # Map brief/verbose flags into a consistent report_format value when not explicitly set
    if getattr(args, "report_format", None) is None:
        if getattr(args, "brief", False):
            args.report_format = "compact"
        elif getattr(args, "verbose", False):
            args.report_format = "verbose"
        else:
            args.report_format = None

    return args


def create_default_plot_filename(audio_path: Path) -> str:
    return f"{audio_path.stem}_stereo_spectrum.png"


def display_available() -> bool:
    backend = mpl.get_backend().lower()
    non_gui = {"agg", "pdf", "svg", "ps", "cairo"}

    if any(b in backend for b in non_gui):
        return False

    if sys.platform.startswith("linux"):
        if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            return False

    return True


def get_final_plot_path(audio_path: Path, args) -> Optional[Path]:
    if args.plot not in ("save", "both"):
        return None

    if args.plot_file is None:
        plot_filename = Path(create_default_plot_filename(audio_path))
    else:
        plot_filename = Path(args.plot_file)

    output_dir = args.output_dir or Path('.')
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_path = output_dir / plot_filename

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

    return plot_path
