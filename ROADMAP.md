# Audio File Report Roadmap

This roadmap outlines the planned development of Audio File Report from a basic stereo WAV analyzer into a tested audio-analysis and quality-control tool.

## Current Version: 0.1.0

Current capabilities:

- Read 16-bit stereo PCM WAV files
- Report channel count
- Report sample rate
- Report bit depth
- Report frame count
- Calculate duration
- Separate left and right channels
- Apply a Hann window
- Calculate an FFT for each channel
- Plot left and right frequency spectra
- Display frequencies on a logarithmic axis
- Accept a WAV filename through Terminal
- Organize analysis into focused Python functions

## Version 0.2.0 — File Handling and Command-Line Interface

- [ ] Replace basic `sys.argv` handling with `argparse`
- [ ] Add a `--help` command
- [ ] Add a `--version` command
- [ ] Check whether the selected file exists
- [ ] Confirm that the selected file is a valid WAV
- [ ] Provide concise error messages
- [ ] Display duration as `HH:MM:SS`
- [ ] Report file size
- [ ] Report estimated bitrate
- [ ] Add `requirements.txt`

## Version 0.3.0 — Level Measurements

Calculate measurements independently for both channels:

- [ ] Sample peak in linear amplitude
- [ ] Sample peak in dBFS
- [ ] RMS in linear amplitude
- [ ] RMS in dBFS
- [ ] Crest factor
- [ ] DC offset
- [ ] Minimum and maximum sample values
- [ ] Clipped-sample count
- [ ] Percentage of clipped samples
- [ ] Near-clipping warning
- [ ] Leading silence duration
- [ ] Trailing silence duration
- [ ] Total silence percentage
- [ ] Average left/right level difference

## Version 0.4.0 — Spectral Analysis

- [ ] Detect the dominant frequency in each channel
- [ ] Report the strongest spectral peaks
- [ ] Add adjustable FFT size
- [ ] Add selectable window functions
- [ ] Add selectable frequency range
- [ ] Add spectral averaging
- [ ] Add peak-hold spectrum
- [ ] Add spectral centroid
- [ ] Add spectral bandwidth
- [ ] Measure energy in user-defined frequency bands
- [ ] Add octave or fractional-octave smoothing
- [ ] Add left and right spectrograms
- [ ] Save spectrum plots as PNG files

## Version 0.5.0 — Stereo and Phase Analysis

- [ ] Calculate left/right level balance
- [ ] Calculate channel correlation
- [ ] Detect possible polarity inversion
- [ ] Detect possible dual-mono files
- [ ] Detect possible duplicated channels
- [ ] Detect a silent or nearly silent channel
- [ ] Convert left/right audio to mid/side
- [ ] Compare mid and side energy
- [ ] Estimate stereo width
- [ ] Estimate mono compatibility
- [ ] Estimate interchannel time delay
- [ ] Calculate frequency-dependent correlation
- [ ] Plot mid and side spectra
- [ ] Add a goniometer or vectorscope display

## Version 0.6.0 — Expanded WAV Support

- [ ] Support mono WAV files
- [ ] Support 8-bit PCM
- [ ] Confirm complete 16-bit PCM support
- [ ] Support 24-bit PCM
- [ ] Support 32-bit PCM
- [ ] Support 32-bit floating-point WAV files
- [ ] Support WAV extensible headers
- [ ] Process large files without loading all samples into memory
- [ ] Investigate optional AIFF support
- [ ] Investigate optional FLAC support

## Version 0.7.0 — Visualization

- [ ] Plot left and right waveforms
- [ ] Add separate and overlaid channel views
- [ ] Plot peak envelopes
- [ ] Plot RMS envelopes
- [ ] Mark clipped regions
- [ ] Mark silence regions
- [ ] Display DC offset
- [ ] Add selected-time-range analysis
- [ ] Add phase and correlation plots
- [ ] Save all visualizations

## Version 0.8.0 — Quality-Control Profiles

- [ ] Load delivery requirements from a JSON profile
- [ ] Validate required sample rate
- [ ] Validate required bit depth
- [ ] Validate required channel count
- [ ] Validate maximum permitted peak
- [ ] Validate maximum permitted DC offset
- [ ] Validate permitted left/right imbalance
- [ ] Validate minimum and maximum duration
- [ ] Produce pass, warning, and error results
- [ ] Allow users to create custom profiles

## Version 0.9.0 — Reports and Batch Processing

- [ ] Export measurements as JSON
- [ ] Export measurements as CSV
- [ ] Generate an HTML report
- [ ] Save analysis settings with reports
- [ ] Analyze every supported file in a folder
- [ ] Produce a folder-level quality-control summary
- [ ] Compare two audio files
- [ ] Sort batch results by pass, warning, and error

## Version 1.0.0 — Tested Release

- [ ] Add automated unit tests
- [ ] Test known-frequency signals
- [ ] Test known-amplitude signals
- [ ] Test silent signals
- [ ] Test clipped signals
- [ ] Test dual-mono signals
- [ ] Test polarity-inverted signals
- [ ] Test every supported bit depth
- [ ] Add automated testing with GitHub Actions
- [ ] Complete project documentation
- [ ] Add example reports and screenshots
- [ ] Add a changelog
- [ ] Add a license
- [ ] Package the program as an installable command-line tool
- [ ] Publish a versioned GitHub release

## Future Research

Potential features after version 1.0:

- [ ] Integrated loudness
- [ ] Momentary loudness
- [ ] Short-term loudness
- [ ] Loudness range
- [ ] True-peak measurement
- [ ] BWF metadata inspection
- [ ] Interactive graphical interface
- [ ] Drag-and-drop file selection
- [ ] Real-time input analysis
- [ ] Multichannel and immersive-audio validation

## Measurement Terminology

- The current FFT graph represents the frequency spectrum of the selected audio file.
- It should not be described as a system frequency response unless a known test signal and measurement process are used.
- Digital level measurements in dBFS should not be described as acoustic SPL without a calibrated measurement chain.