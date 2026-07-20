# User Manual

This manual documents how to use the Audio File Report command-line tool once it is installed.

## Running the tool

The program expects one positional argument: the path to a WAV file.

```bash
python audio_report.py /path/to/your_file.wav
```

## Command reference by release

### Version 0.2.0

The current CLI includes the core file-analysis workflow, explicit reporting formats, and logging controls.

#### Core commands

```bash
# Basic run
python audio_report.py test_audio.wav

# Show version information
python audio_report.py --version
```

#### Output and report controls

```bash
# One-line summary
python audio_report.py test_audio.wav --brief

# Detailed report
python audio_report.py test_audio.wav --verbose

# Suppress normal output
python audio_report.py test_audio.wav --quiet
```

#### Plotting and output controls

```bash
# Show the plot interactively
python audio_report.py test_audio.wav --plot show

# Save the plot to disk
python audio_report.py test_audio.wav --plot save

# Show and save the plot
python audio_report.py test_audio.wav --plot both

# Do not create or show a plot
python audio_report.py test_audio.wav --plot none
```

```bash
# Save the plot to a custom file name
python audio_report.py test_audio.wav --plot save --plot-file my_report.png

# Save the plot into a specific directory
python audio_report.py test_audio.wav --plot save --output-dir plots

# Allow overwriting an existing output file
python audio_report.py test_audio.wav --plot save --overwrite
```

```bash
# Use a specific DPI value
python audio_report.py test_audio.wav --plot save --dpi 300

# Use a preset DPI value
python audio_report.py test_audio.wav --plot save --dpi-choice screen
python audio_report.py test_audio.wav --plot save --dpi-choice print
```

#### Interaction and diagnostics

```bash
# Prefer showing the plot interactively
python audio_report.py test_audio.wav --show

# Avoid prompting in headless environments
python audio_report.py test_audio.wav --plot show --no-prompt

# Enable debugging output
python audio_report.py test_audio.wav --debug
```

### Version 0.2.0

Version 0.2.0 added explicit reporting formats and logging support.

#### Report format commands

```bash
# Normal output (default behavior)
python audio_report.py test_audio.wav

# One-line summary
python audio_report.py test_audio.wav --brief

# Grouped, detailed report
python audio_report.py test_audio.wav --verbose

# Quiet mode
python audio_report.py test_audio.wav --quiet
```

```bash
# Use the explicit report format selector
python audio_report.py test_audio.wav --report-format compact
python audio_report.py test_audio.wav --report-format verbose
python audio_report.py test_audio.wav --report-format timed
```

#### Logging commands

```bash
# Write detailed logs to a file
python audio_report.py test_audio.wav --log-file debug.log

# Write logs and enable debug output
python audio_report.py test_audio.wav --log-file debug.log --debug
```

### Full-feature example

A practical end-to-end example combining multiple features:

```bash
python audio_report.py test_audio.wav \
  --plot both \
  --plot-file spectrum.png \
  --output-dir output \
  --dpi-choice print \
  --report-format verbose \
  --debug \
  --log-file debug.log
```

### Headless plotting note

If Matplotlib causes backend issues in a headless environment, try:

```bash
MPLBACKEND=Agg python audio_report.py test_audio.wav --plot save
```
