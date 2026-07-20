# User Manual

This manual documents how to use the Audio File Report command-line tool once it is installed.

## Running the tool

The program expects one positional argument: the path to a WAV file.

```bash
python audio_report.py /path/to/your_file.wav
```

## Command reference

### Legacy Version 0.1.0 (historical)

Version 0.1.0 was the initial stereo WAV analyzer before the expanded CLI options added in 0.2.0.

Use these examples as historical reference for early usage patterns:

```bash
# Basic analysis run on a stereo WAV file
python audio_report.py assets/audio/test_audio.wav

# Analyze a WAV file from any path
python audio_report.py /path/to/your_file.wav
```

Notes:

- 0.1.0 focused on core analysis and plotting behavior.
- Many convenience flags and diagnostics options documented below were introduced in 0.2.0.

### Version 0.2.0 (current)

The current CLI includes the core file-analysis workflow, explicit reporting formats, and logging controls.

Complete 0.2.0 option list:

- Positional: `audio_file`
- Flags: `--version`, `--brief`, `--verbose`, `--quiet`, `--overwrite`, `--debug`, `--show`, `--no-prompt`
- Value options: `--plot {show,save,both,none}`, `--plot-file PATH`, `--output-dir PATH`, `--dpi INT`, `--dpi-choice {screen,screen-high,print}`, `--report-format {compact,verbose,timed}`, `--log-file PATH`

#### Core commands

```bash
# Basic run
python audio_report.py assets/audio/test_audio.wav

# Show version information
python audio_report.py --version
```

#### Output and report controls

```bash
# One-line summary
python audio_report.py assets/audio/test_audio.wav --brief

# Detailed report
python audio_report.py assets/audio/test_audio.wav --verbose

# Suppress normal output
python audio_report.py assets/audio/test_audio.wav --quiet
```

#### Plotting and output controls

```bash
# Show the plot interactively
python audio_report.py assets/audio/test_audio.wav --plot show

# Save the plot to disk
python audio_report.py assets/audio/test_audio.wav --plot save

# Show and save the plot
python audio_report.py assets/audio/test_audio.wav --plot both

# Do not create or show a plot
python audio_report.py assets/audio/test_audio.wav --plot none
```

```bash
# Save the plot to a custom file name (save mode is implied)
python audio_report.py assets/audio/test_audio.wav --plot-file my_report.png

# Save the plot into a specific directory (save mode is implied)
python audio_report.py assets/audio/test_audio.wav --output-dir plots

# Allow overwriting an existing output file (used with save behavior)
python audio_report.py assets/audio/test_audio.wav --plot-file my_report.png --overwrite
```

Note: In the current CLI parser, `--brief`, `--verbose`, `--quiet`, `--plot`, `--plot-file`, and `--output-dir` are mutually exclusive.

```bash
# Use a specific DPI value
python audio_report.py assets/audio/test_audio.wav --plot save --dpi 300

# Use a preset DPI value
python audio_report.py assets/audio/test_audio.wav --plot save --dpi-choice screen
python audio_report.py assets/audio/test_audio.wav --plot save --dpi-choice screen-high
python audio_report.py assets/audio/test_audio.wav --plot save --dpi-choice print
```

#### Interaction and diagnostics

```bash
# Prefer showing the plot interactively
python audio_report.py assets/audio/test_audio.wav --show

# Avoid prompting in headless environments
python audio_report.py assets/audio/test_audio.wav --plot show --no-prompt

# Write detailed logs without console debug spam
python audio_report.py assets/audio/test_audio.wav --log-file debug.log

# Enable debugging output
python audio_report.py assets/audio/test_audio.wav --debug
```

Version 0.2.0 also added explicit reporting formats and logging support.

#### Report format commands

```bash
# Normal output (default behavior)
python audio_report.py assets/audio/test_audio.wav

# One-line summary
python audio_report.py assets/audio/test_audio.wav --brief

# Grouped, detailed report
python audio_report.py assets/audio/test_audio.wav --verbose

# Quiet mode
python audio_report.py assets/audio/test_audio.wav --quiet
```

```bash
# Use the explicit report format selector
python audio_report.py assets/audio/test_audio.wav --report-format compact
python audio_report.py assets/audio/test_audio.wav --report-format verbose
python audio_report.py assets/audio/test_audio.wav --report-format timed
```

#### Logging commands

```bash
# Write detailed logs to a file
python audio_report.py assets/audio/test_audio.wav --log-file debug.log

# Write logs and enable debug output
python audio_report.py assets/audio/test_audio.wav --log-file debug.log --debug
```

#### Path handling commands

```bash
# Relative path
python audio_report.py assets/audio/test_audio.wav

# Absolute path
python audio_report.py /absolute/path/to/file.wav

# Home directory expansion
python audio_report.py ~/audio/file.wav
```

### Full-featured example

A practical end-to-end example combining multiple features:

```bash
python audio_report.py assets/audio/test_audio.wav \
  --plot both \
  --dpi-choice print \
  --report-format timed \
  --debug \
  --log-file debug.log
```

### Headless plotting note

If Matplotlib causes backend issues in a headless environment, try:

```bash
MPLBACKEND=Agg python audio_report.py assets/audio/test_audio.wav --plot save
```
