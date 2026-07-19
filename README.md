# Audio File Report

A Python command-line tool that analyzes WAV-file metadata and produces left/right frequency spectra.

This workspace now organizes the code into small modules for easier maintenance:

- `audio_report.py` — thin entrypoint that wires the program
- `cli.py` — command-line parsing, display detection, and plot-path helpers
- `fileio.py` — input validation and WAV reading
- `analysis.py` — FFT and analysis helpers
- `plotting.py` — plotting and Matplotlib cleanup

## Quickstart

Install requirements:

```bash
python3 -m pip install numpy matplotlib
```

Run the help to see options:

```bash
python3 audio_report.py -h
```

Typical usage (save plot at ~150 DPI):

```bash
python3 audio_report.py test_audio.wav --plot save --dpi-choice screen
```

Show interactively (if a display is available):

```bash
python3 audio_report.py test_audio.wav --plot show
```

If your environment is headless (CI or remote), use `--no-prompt` to automatically save instead of prompting:

```bash
python3 audio_report.py test_audio.wav --plot show --no-prompt
```

## Important CLI options

- `--plot {show,save,both,none}` — control display vs saving (default: `save`)
- `--plot-file` — specify filename for saved PNG
- `--output-dir` — directory to save plot
- `--overwrite` — allow overwriting existing files; otherwise files are auto-renamed
- `--dpi` / `--dpi-choice` — set output DPI; presets: `screen` (150), `screen-high` (200), `print` (300)
- `--debug` — print validation diagnostics
- `--show` — request an interactive GUI display (overrides default `save`)
- `--no-prompt` — when no display is detected, do not prompt; save automatically

### Report formatting and metadata

- `--report-format {compact,verbose,timed}` — Choose the textual metadata layout. `compact` prints a true single-line summary for scanning and batch runs. `verbose` prints grouped, human-readable sections. `timed` prints a timing-focused report with minimal metadata and optional per-step timings. If omitted, `--brief` maps to `compact` and `--verbose` maps to `verbose`.
- `--brief` / `--verbose` / `--quiet` — legacy flags retained for backward compatibility; they map to the same presentation modes when `--report-format` is not supplied.

Metadata reported by the tool (displayed in `compact`, `verbose`, or `timed` view):

- Program version (when available)
- File name and resolved path (path shown in verbose/debug)
- File size (bytes and human-friendly KB/MB where appropriate)
- Encoding description (compression type and human-readable name when present)
- Channel layout (mono/stereo/multichannel and numeric channel count)
- Sample rate (Hz)
- Sample width (bytes) and bit depth (bits)
- Frame count (formatted with thousands separators)
- Duration in seconds and as HH:MM:SS
- Estimated uncompressed bitrate (human-friendly formatting — shown as "<X> kbps" when under 1000 kbps, and as "<Y.YY> Mbps (<X> kbps)" when >= 1000 kbps)
- Total analysis time (printed in `--verbose` or when `--report-format=verbose`)
- Per-step timing details in `timed` mode (read, FFT, and plot phases when available)

Notes:

- The `compact` view is a true single-line summary for faster scanning and batch use.
- The `verbose` view groups related fields (File / Audio Properties / Bitrate / Timing) and includes the full file path and analysis timing information.
- The `timed` view emphasizes duration and processing performance, including optional read/FFT/plot timings.
- For automated workflows or CI, consider redirecting output or adding a future `--format json|yaml` option (not yet implemented) for machine-readable output.

## Example outputs

Compact (quick scan):

```
test_audio.wav | 940.3 KB | stereo | 44100 Hz | 16-bit | 220,500 frames | 5.00 s (00:00:05) | 1.54 Mbps (1536 kbps)
```

Verbose (grouped details):

```
AUDIO FILE REPORT
-----------------
Program version: 0.1.0

File
	Name:        test_audio.wav
	Path:        /full/path/test_audio.wav
	Size:        940.3 KB
	Encoding:    NONE (uncompressed)

Audio Properties
	Channels:    2 (stereo)
	Sample rate: 44,100 Hz
	Sample width: 2 bytes (16-bit)
	Frames:      220,500
	Duration:    5.00 seconds (00:00:05)

Bitrate
	Estimated uncompressed bitrate: 1.54 Mbps (1536 kbps)

Timing
	Analysis time: 0.34 seconds
```

Timed (performance-focused):

```
Audio File Report — 0.1.0
----------------------------------------
File: test_audio.wav
File size: 940,300 bytes

Duration: 5.00 seconds (00:00:05)
Estimated uncompressed bitrate: 1.54 Mbps (1536 kbps)

Total analysis time: 0.34 seconds
(Read: 0.05 s, FFT: 0.18 s, Plot: 0.11 s)
```

## Logging and concise errors

By default the program prints short, user-friendly error messages to the console and writes full diagnostics (DEBUG messages and stack traces) to a log file when requested.

Examples:

```bash
# write detailed logs to debug.log, console remains concise
python3 audio_report.py test_audio.wav --log-file debug.log

# verbose console output + file logging
python3 audio_report.py test_audio.wav --log-file debug.log --debug
```

When reporting an issue, include the `debug.log` file (if you used `--log-file`) so developers can see full tracebacks and internal diagnostics.

## Notes

- The tool currently supports 16-bit stereo PCM WAV files for spectrum analysis.
- Validation is conservative: the program checks WAV headers, frame counts, and reads frames to ensure files are not truncated or corrupted.
- The code has been refactored into modules to make it easier to add unit tests and extend functionality.

If you want, I can add a `requirements.txt`, unit tests for `fileio.py` and `analysis.py`, or convert this into a proper package with `pyproject.toml`.