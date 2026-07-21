# Audio File Report

Current release: 0.2.0

Audio File Report is a Python command-line tool for analyzing WAV files and generating left/right frequency spectrum plots. It reports metadata such as file size, encoding, channel layout, sample rate, bit depth, duration, and bitrate estimates, then optionally saves or displays a spectrum chart.

## What the project currently does

- Reads and validates WAV files before analysis
- Reports audio metadata in compact, verbose, or timed formats
- Generates stereo spectrum plots for the left and right channels
- Supports interactive display or file-based output
- Writes detailed diagnostics to a log file when requested
- Includes conservative validation to detect truncated or corrupted files

## Project structure

The repository is organized by purpose:

- [audio_report.py](audio_report.py) — compatibility entrypoint for running from repo root
- [src/audio_file_report/](src/audio_file_report) — application package
- [scripts/generate_test_audio.py](scripts/generate_test_audio.py) — test-audio generator utility
- [assets/audio/](assets/audio) — sample WAV inputs
- [assets/plots/](assets/plots) — sample generated plots
- [docs/reference/](docs/reference) — setup, user manual, roadmap, and development plan
- [docs/product/](docs/product) — product differentiation notes
- [tests/](tests) — diagnostics tests

## Requirements

- Python 3.9 or newer (Python 3.10+ is recommended)
- A terminal with network access for installing dependencies
- The runtime dependencies listed in [requirements.txt](requirements.txt)

Current runtime dependencies:

- NumPy for FFT and numerical processing
- Matplotlib for spectrum plot rendering

## Installation

From the project root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, use:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Verify the installation:

```bash
python -m pip show numpy matplotlib
python audio_report.py -h
```

If the help output appears, the setup is working.

## Quick start

Run the tool on the sample WAV file included in the repository:

```bash
python audio_report.py assets/audio/test_audio.wav --plot save --dpi-choice screen
```

This will print a metadata report and save a spectrum plot by default.

## Usage overview

The tool expects one positional argument: the path to a WAV file.

```bash
python audio_report.py /path/to/your_file.wav
```

### Common commands

```bash
# One-line summary
python audio_report.py assets/audio/test_audio.wav --brief

# Grouped, detailed report
python audio_report.py assets/audio/test_audio.wav --verbose

# Save a plot to a specific file (save mode is implied)
python audio_report.py assets/audio/test_audio.wav --plot-file spectrum.png

# Write diagnostics to a log file
python audio_report.py assets/audio/test_audio.wav --log-file debug.log --debug
```

For the complete option list and all valid command combinations, see [docs/reference/USER_MANUAL.md](docs/reference/USER_MANUAL.md).

## Run all diagnostics and regression tests

From the repository root, run:

```bash
python3 -m unittest \
	tests/test_diagnostics.py \
	tests/test_cli_plotting_regressions.py \
	tests/test_cli_argument_matrix.py \
	tests/test_error_code_regressions.py -v
```

## Headless environments

If you are running in CI, Docker, or another headless environment, use save mode rather than interactive display:

```bash
python audio_report.py assets/audio/test_audio.wav --plot save --no-prompt
```

If Matplotlib backend issues appear, try:

```bash
MPLBACKEND=Agg python audio_report.py assets/audio/test_audio.wav --plot save
```

## Notes and limitations

- The tool currently focuses on 16-bit stereo PCM WAV files for spectrum analysis
- Validation is conservative and checks headers, frame counts, and frame reads
- The program will auto-rename output files if a target already exists unless `--overwrite` is used

## Documentation

For more detail, see:

- [docs/reference/SETUP.md](docs/reference/SETUP.md) — installation and environment setup
- [docs/reference/USER_MANUAL.md](docs/reference/USER_MANUAL.md) — full CLI usage guide
- [docs/reference/DEVELOPMENT_PLAN.md](docs/reference/DEVELOPMENT_PLAN.md) — development roadmap and planned features
