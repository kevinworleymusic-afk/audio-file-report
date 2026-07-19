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