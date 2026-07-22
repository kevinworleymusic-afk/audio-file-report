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

## Run all tests (all versions)

From the repository root, run every test module:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## Run tests by version

Run the current implemented version tracks separately:

```bash
# Version 0.2.x diagnostics and CLI/plotting regressions
python3 -m unittest \
	tests/test_diagnostics.py \
	tests/test_cli_plotting_regressions.py \
	tests/test_cli_argument_matrix.py \
	tests/test_error_code_regressions.py -v

# Version 0.3.x level and dynamics regressions
python3 -m unittest \
	tests/test_v030_fundamental_amplitude_script.py \
	tests/test_v030_clipping_limiting_indicators_script.py \
	tests/test_v030_dc_waveform_center_measurements_script.py \
	tests/test_v030_dynamic_envelope_script.py \
	tests/test_v030_gain_normalization_information_script.py \
	tests/test_v030_level_distribution_script.py \
	tests/test_v030_rms_crest_factor_script.py \
	tests/test_v030_silence_dropout_analysis_script.py \
	tests/test_v030_level_metrics.py \
	tests/test_v030_regression_validation_track.py -v
```

## Run all diagnostics and regression tests (explicit module list)

From the repository root, run:

```bash
python3 -m unittest \
	tests/test_diagnostics.py \
	tests/test_cli_plotting_regressions.py \
	tests/test_cli_argument_matrix.py \
	tests/test_error_code_regressions.py \
	tests/test_v030_fundamental_amplitude_script.py \
	tests/test_v030_clipping_limiting_indicators_script.py \
	tests/test_v030_dc_waveform_center_measurements_script.py \
	tests/test_v030_dynamic_envelope_script.py \
	tests/test_v030_gain_normalization_information_script.py \
	tests/test_v030_level_distribution_script.py \
	tests/test_v030_rms_crest_factor_script.py \
	tests/test_v030_silence_dropout_analysis_script.py \
	tests/test_v030_regression_validation_track.py \
	tests/test_v030_level_metrics.py -v
```

## Code Organization by Version

Implementation is organized by roadmap workstream under [src/audio_file_report/](src/audio_file_report):

- [src/audio_file_report/v020_reliable_cli_file_handling/](src/audio_file_report/v020_reliable_cli_file_handling) — current production implementation (0.2.0)
- [src/audio_file_report/v030_levels_dynamics/](src/audio_file_report/v030_levels_dynamics) — planned 0.3.0 package
- [src/audio_file_report/v040_spectral_analysis/](src/audio_file_report/v040_spectral_analysis) — planned 0.4.0 package
- [src/audio_file_report/v050_stereo_phase_spatial/](src/audio_file_report/v050_stereo_phase_spatial) — planned 0.5.0 package
- [src/audio_file_report/v060_expanded_wav_support/](src/audio_file_report/v060_expanded_wav_support) — planned 0.6.0 package
- [src/audio_file_report/v070_visual_exploration/](src/audio_file_report/v070_visual_exploration) — planned 0.7.0 package
- [src/audio_file_report/v080_quality_control_profiles/](src/audio_file_report/v080_quality_control_profiles) — planned 0.8.0 package
- [src/audio_file_report/v090_reports_batch_processing/](src/audio_file_report/v090_reports_batch_processing) — planned 0.9.0 package
- [src/audio_file_report/v100_trusted_tested_installable/](src/audio_file_report/v100_trusted_tested_installable) — planned 1.0.0 package

Compatibility modules remain at top level (for example [src/audio_file_report/app.py](src/audio_file_report/app.py), [src/audio_file_report/cli.py](src/audio_file_report/cli.py)) and forward to the active implementation so existing imports continue to work.

Version-aligned script entrypoints are available in [scripts/](scripts), such as [scripts/run_020/run_020_reliable_cli_file_handling.py](scripts/run_020/run_020_reliable_cli_file_handling.py), [scripts/run_030/run_030_levels_dynamics.py](scripts/run_030/run_030_levels_dynamics.py), and [scripts/run_040_spectral_analysis.py](scripts/run_040_spectral_analysis.py). These wrappers forward arguments to [audio_report.py](audio_report.py).

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
