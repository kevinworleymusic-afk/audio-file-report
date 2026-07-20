# Setup Guide

This project is a small Python CLI for analyzing WAV files and generating spectrum plots. The runtime dependencies are intentionally lightweight:

- NumPy for FFT and numerical processing
- Matplotlib for rendering plots

## Requirements

- Python 3.9 or newer (Python 3.10+ is recommended)
- A terminal with network access to install dependencies

## 1. Create and activate a virtual environment

Using macOS or Linux:

```bash
cd /path/to/audio-file-report
python3 -m venv .venv
source .venv/bin/activate
```

Using Windows PowerShell:

```powershell
cd C:\path\to\audio-file-report
py -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2. Install the project dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

This installs the required packages from the repository's requirements file.

## 3. Verify that everything is installed correctly

```bash
python -m pip show numpy matplotlib
python audio_report.py -h
```

If the help output appears, the installation was successful.

## 4. Run the analyzer

Basic usage:

```bash
python audio_report.py test_audio.wav --plot save --dpi-choice screen
```

This analyzes the WAV file, prints a metadata report, and saves a spectrum plot by default.

### Example output modes

Here are the three common report styles you can choose from:

```text
Normal mode  -> standard report with core metadata
   │
   ├─ python audio_report.py test_audio.wav
   │
Brief mode   -> one-line summary for quick scanning
   │
   └─ python audio_report.py test_audio.wav --brief

Verbose mode -> detailed grouped report with more context
   └─ python audio_report.py test_audio.wav --verbose
```

```bash
# Default / normal output
python audio_report.py test_audio.wav

# Brief one-line summary
python audio_report.py test_audio.wav --brief

# Verbose grouped report
python audio_report.py test_audio.wav --verbose
```

The brief mode is useful for scanning lots of files quickly, while the verbose mode is better when you want more details about the file and analysis.

For a fuller guide to the available commands and usage patterns, see [USER_MANUAL.md](USER_MANUAL.md).

## 5. Headless and plotting notes

Matplotlib can behave differently in headless environments. If you hit backend-related issues, use:

```bash
MPLBACKEND=Agg python audio_report.py test_audio.wav --plot save
```

This is especially useful on remote servers, Docker containers, or CI systems.

## 6. Troubleshooting

- If Python is not found, install Python 3.10+ and use `python3` or `py` depending on your platform.
- If `pip` is missing, run `python -m ensurepip --upgrade`.
- If you see `No module named matplotlib` or `No module named numpy`, make sure your virtual environment is active and reinstall dependencies with `python -m pip install -r requirements.txt`.
- If the plot does not appear, try `--plot save` instead of `--plot show`.
- For full diagnostics, run the tool with logging enabled:

```bash
python audio_report.py test_audio.wav --log-file debug.log --debug
```

## 7. Recommended workflow

1. Create a virtual environment.
2. Install dependencies with the requirements file.
3. Run the CLI from the project root.
4. Start with `--plot save` for a simple workflow.
5. Use [USER_MANUAL.md](USER_MANUAL.md) for the full CLI reference and advanced examples.
