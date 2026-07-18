# Audio File Report

A Python command-line tool that analyzes WAV-file metadata and plots the frequency spectra of the left and right channels.

## Current Features

- Reports the filename
- Reports mono or stereo channel count
- Reports sample rate
- Reports bit depth
- Reports frame count
- Calculates duration
- Separates left and right audio channels
- Applies a Hann window before spectrum analysis
- Calculates an FFT for each channel
- Plots both spectra on a logarithmic frequency axis

## Requirements

- Python 3
- NumPy
- Matplotlib

Install the required packages with:

```bash
python3 -m pip install numpy matplotlib
```