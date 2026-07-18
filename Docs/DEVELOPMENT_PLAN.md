# Audio File Report Detailed Development Plan

This document contains the detailed technical checklist for developing Audio File Report from a basic stereo WAV analyzer into a tested audio-analysis and quality-control tool.

For an approachable release overview, see [`ROADMAP.md`](../ROADMAP.md). For the product-level rationale behind the differentiators, see [`PRODUCT_DIFFERENTIATION.md`](PRODUCT_DIFFERENTIATION.md). This detailed plan is a working document rather than a fixed promise. Features may move between releases as the project develops and technical dependencies become clearer.

## Current Version: 0.1.0 

Current capabilities:

- [x] Read 16-bit stereo PCM WAV files
- [x] Accept a WAV filename through Terminal
- [x] Report the filename
- [x] Report channel count
- [x] Report sample rate
- [x] Report bit depth
- [x] Report frame count
- [x] Calculate duration
- [x] Decode interleaved PCM samples
- [x] Separate left and right channels
- [x] Apply a Hann window
- [x] Calculate an FFT for each channel
- [x] Convert spectral magnitude to relative decibels
- [x] Plot left and right frequency spectra
- [x] Display frequency on a logarithmic axis
- [x] Organize the analysis into focused Python functions
- [x] Publish the project and documentation on GitHub

## Version 0.2.0 — Reliable CLI and File Handling

### Differentiation Goals

- Make advanced diagnostic detail available without making ordinary use intimidating
- Preserve a clear path from friendly error messages to complete debug evidence
- Make graph and output behavior explicit, predictable, and safe

The purpose of version 0.2.0 is to make the existing analyzer easy, controllable, and reliable before adding more audio measurements.

### Command-Line Interface

- [ ] Replace manual `sys.argv` handling with `argparse`
- [ ] Add automatically generated `--help` instructions
- [ ] Add a `--version` option
- [ ] Accept relative and absolute file paths
- [ ] Accept paths containing spaces
- [ ] Expand `~` in file paths
- [ ] Handle Unicode characters in filenames
- [ ] Handle keyboard interruption with Control-C cleanly

### Display Modes

- [ ] Add a normal default report
- [ ] Add `--brief` for a one-line summary
- [ ] Add `--verbose` for detailed technical output
- [ ] Add `--quiet` to suppress normal output
- [ ] Make brief, verbose, and quiet modes mutually exclusive

### Graph Control

- [ ] Add `--plot show`
- [ ] Add `--plot save`
- [ ] Add `--plot both`
- [ ] Add `--plot none`
- [ ] Keep `show` as the default plot behavior
- [ ] Add `--plot-file` to select the output filename
- [ ] Add `--output-dir` to select an output folder
- [ ] Generate a readable default PNG filename
- [ ] Confirm where saved plots are located
- [ ] Prevent accidental file overwriting
- [ ] Add `--overwrite` to permit intentional replacement
- [ ] Save graphs at a useful resolution
- [ ] Close Matplotlib cleanly
- [ ] Detect when a graphical display is unavailable

### File Validation

- [ ] Confirm that the supplied path exists
- [ ] Confirm that the path points to a file rather than a folder
- [ ] Detect permission errors
- [ ] Detect empty files
- [ ] Detect WAV files containing zero frames
- [ ] Confirm that the file contains readable WAV data
- [ ] Validate WAV structure rather than trusting only the extension
- [ ] Detect unreadable or corrupted WAV headers
- [ ] Explain unsupported encoding types
- [ ] Explain unsupported bit depths
- [ ] Explain unsupported channel counts
- [ ] Distinguish missing-file, permission, format, and analysis errors

### Diagnostics

- [ ] Show concise errors by default
- [ ] Add `--debug`
- [ ] Show full tracebacks only in debug mode
- [ ] Add `--log-file`
- [ ] Include the program version in debug logs
- [ ] Include Python and dependency versions in debug logs
- [ ] Include the operating system in debug logs
- [ ] Include the resolved input path in debug logs
- [ ] Include active command-line options in debug logs
- [ ] Provide actionable suggestions for correctable errors
- [ ] Use clear operating-system exit codes

### Improved Metadata

- [ ] Display the program version
- [ ] Display file size
- [ ] Display the encoding type
- [ ] Describe channel layout as mono, stereo, or multichannel
- [ ] Format sample rate clearly
- [ ] Display sample width in bytes
- [ ] Display bit depth in bits
- [ ] Format frame count clearly
- [ ] Display duration in seconds
- [ ] Display duration as `HH:MM:SS`
- [ ] Display estimated uncompressed bitrate
- [ ] Display total analysis time in verbose mode

### Project Setup and Documentation

- [ ] Add `requirements.txt`
- [ ] Provide actionable missing-dependency messages
- [ ] Document supported Python versions
- [ ] Update README installation instructions
- [ ] Document all version 0.2.0 command-line options
- [ ] Add normal, brief, verbose, and debug examples
- [ ] Update `__version__` to `0.2.0` only when the release is complete

## Version 0.3.0 — Level and Dynamics Measurements

### Differentiation Goals

- Turn whole-file statistics into time-located events and evidence
- Connect level findings to controlled signals with known expected results
- Provide non-destructive gain previews rather than silently changing source audio

The purpose of version 0.3.0 is to measure how high, how average, how variable, how silent, and how potentially damaged the left and right signals are over time.

### Fundamental Amplitude

- [ ] Calculate sample peak in linear amplitude
- [ ] Calculate sample peak in dBFS
- [ ] Calculate headroom below 0 dBFS
- [ ] Calculate peak-to-peak amplitude
- [ ] Calculate mean absolute amplitude
- [ ] Report minimum and maximum sample values
- [ ] Report positive and negative peak values
- [ ] Measure positive/negative peak asymmetry
- [ ] Report the peak sample position
- [ ] Report the peak time in seconds

### RMS and Crest Factor

- [ ] Calculate whole-file RMS in linear amplitude
- [ ] Calculate whole-file RMS in dBFS
- [ ] Calculate crest factor
- [ ] Add a configurable RMS-window duration
- [ ] Calculate windowed RMS over time
- [ ] Report maximum windowed RMS
- [ ] Report minimum active windowed RMS
- [ ] Report median windowed RMS
- [ ] Report the time of maximum windowed RMS
- [ ] Calculate windowed RMS range
- [ ] Calculate RMS variability over time

### Dynamic Envelope

- [ ] Calculate a peak envelope
- [ ] Calculate an RMS envelope
- [ ] Calculate crest factor over time
- [ ] Identify the loudest continuous region
- [ ] Identify the quietest active region
- [ ] Report the times of the loudest and quietest regions
- [ ] Measure the difference between loudest and quietest active regions
- [ ] Detect large level changes
- [ ] Report the largest upward level change
- [ ] Report the largest downward level change
- [ ] Identify sustained high-level regions
- [ ] Identify sustained low-level regions

### Level Distribution

- [ ] Report time spent above -3 dBFS
- [ ] Report time spent above -6 dBFS
- [ ] Report time spent above -12 dBFS
- [ ] Report time spent below -40 dBFS
- [ ] Report time spent below -60 dBFS
- [ ] Allow configurable level thresholds
- [ ] Calculate active-audio percentage
- [ ] Count threshold crossings
- [ ] Identify the most commonly occupied level range

### Clipping and Limiting Indicators

- [ ] Count clipped samples
- [ ] Calculate clipped-sample percentage
- [ ] Count separate clipping events
- [ ] Count positive clipping events
- [ ] Count negative clipping events
- [ ] Report the first and last clipping times
- [ ] Report the longest consecutive clipping run
- [ ] Report the duration of the longest clipping run
- [ ] Add a configurable near-clipping threshold
- [ ] Count near-clipping samples
- [ ] Detect repeated identical peak values
- [ ] Detect possible flat-topped regions
- [ ] Report possible heavy limiting as a warning rather than a definitive diagnosis

### Silence and Dropout Analysis

- [ ] Measure exact digital silence
- [ ] Add configurable threshold-based silence
- [ ] Add a minimum duration required for a silent region
- [ ] Measure leading silence
- [ ] Measure trailing silence
- [ ] Count interior silent regions
- [ ] Measure the longest silent region
- [ ] Report the first and last silent-region times
- [ ] Calculate total silence duration
- [ ] Calculate silence percentage
- [ ] Calculate active-audio percentage
- [ ] Detect possible audio dropouts
- [ ] Suggest leading and trailing trim points

### DC and Waveform-Center Measurements

- [ ] Calculate mean sample value
- [ ] Calculate DC offset in normalized amplitude
- [ ] Calculate DC offset as a percentage
- [ ] Calculate DC offset over time
- [ ] Report maximum short-term DC offset
- [ ] Identify time ranges with unusual DC offset
- [ ] Compare positive and negative sample counts

### Gain and Normalization Information

- [ ] Calculate gain required to reach a selected sample-peak target
- [ ] Preview the resulting sample peak after gain adjustment
- [ ] Warn if requested gain would clip
- [ ] Add a default sample-peak target such as -1 dBFS
- [ ] Allow a custom sample-peak target
- [ ] Report gain independently for each channel
- [ ] Report linked stereo gain based on the higher channel peak
- [ ] Keep normalization as a calculation preview without modifying the source file

### Left/Right Level Comparison

- [ ] Compare left and right sample peaks
- [ ] Compare left and right RMS
- [ ] Compare left and right crest factors
- [ ] Calculate average left/right level difference
- [ ] Calculate maximum short-term level difference
- [ ] Identify the time of maximum imbalance
- [ ] Warn about a substantially quieter channel

### Optional and Experimental Level Features

- [ ] Add percentile-based windowed RMS measurements
- [ ] Calculate high-to-low percentile RMS range
- [ ] Estimate the low-level floor without claiming a definitive noise floor
- [ ] Add a sample-value distribution histogram
- [ ] Calculate percentage of samples near zero
- [ ] Calculate zero-crossing rate
- [ ] Detect possible clicks or pops
- [ ] Detect abrupt starts and endings
- [ ] Detect probable fade-in regions
- [ ] Detect probable fade-out regions
- [ ] Detect possible sudden gain changes
- [ ] Estimate transient density
- [ ] Detect repeated peak ceilings as a possible limiting indicator
- [ ] Estimate effective use of the available digital amplitude range

### Level Documentation and Validation

- [ ] Document every level formula
- [ ] State the dBFS reference used by each calculation
- [ ] Document every window duration and threshold
- [ ] Generate test files with known amplitude
- [ ] Generate digital-silence test files
- [ ] Generate deliberately clipped test files
- [ ] Generate files with known DC offset
- [ ] Generate left/right level-imbalance test files
- [ ] Generate files with known leading, trailing, and interior silence
- [ ] Verify peak and RMS results against analytical values
- [ ] Verify event times against planted test conditions
- [ ] Explain that dBFS is not acoustic SPL

## Version 0.4.0 — Spectral Analysis

### Differentiation Goals

- Preserve meaningful left/right comparison through shared normalization and explicit settings
- Connect graphs to numeric band tables, selected regions, and exportable data
- Treat music-oriented chromagram and Constant-Q views as optional rather than confusing them with engineering measurements

### Frequency Measurements

- [ ] Detect the dominant frequency in each channel
- [ ] Report several strongest spectral peaks
- [ ] Label important spectral peaks on graphs
- [ ] Allow the number of displayed peak labels to be configured
- [ ] Require a configurable minimum separation between reported peaks
- [ ] Add adjustable FFT size
- [ ] Display the resulting frequency resolution
- [ ] Add selectable window functions
- [ ] Add a selectable frequency range
- [ ] Add spectral averaging
- [ ] Add a peak-hold spectrum
- [ ] Calculate spectral centroid
- [ ] Calculate spectral bandwidth
- [ ] Measure energy in user-defined frequency bands
- [ ] Add octave or fractional-octave smoothing
- [ ] Add left and right spectrograms
- [ ] Save spectrum and spectrogram plots

### Frequency Visualizations

- [ ] Refine the left/right frequency-spectrum graph
- [ ] Add separate left and right spectrum views
- [ ] Add an overlaid left/right spectrum view
- [ ] Show averaged and peak-hold spectra together when requested
- [ ] Add left and right spectrograms
- [ ] Add adjustable spectrogram time resolution
- [ ] Add adjustable spectrogram frequency resolution
- [ ] Add an adjustable spectrogram dynamic range
- [ ] Add an adjustable spectrogram color scale
- [ ] Add octave-band graphs
- [ ] Add one-third-octave-band graphs
- [ ] Allow additional fractional-octave resolutions
- [ ] Display paired left/right band levels
- [ ] Add a numeric band-energy table
- [ ] Add a left/right spectral-difference graph
- [ ] Display spectral difference in decibels
- [ ] Identify frequency regions with major channel differences
- [ ] Add an audio-spectrum waterfall plot over time
- [ ] Allow adjustable spacing between waterfall slices
- [ ] Allow the number of waterfall slices to be configured
- [ ] Save each visualization as a PNG file
- [ ] Record analysis settings with each saved graph

### Spectrum Display and Selection Controls

- [ ] Add no smoothing
- [ ] Add one-octave smoothing
- [ ] Add one-third-octave smoothing
- [ ] Add one-sixth-octave smoothing
- [ ] Add one-twelfth-octave smoothing
- [ ] State that smoothing changes the display rather than the source audio
- [ ] Add shared left/right normalization
- [ ] Add independent left/right normalization
- [ ] Keep shared normalization as the default
- [ ] Add full-range, low-frequency, midrange, and high-frequency presets
- [ ] Allow a custom frequency range
- [ ] Allow whole-file analysis
- [ ] Allow selection of a start time
- [ ] Allow selection of an analysis duration
- [ ] Allow comparison of a selected region with the whole file

### Spectral Data Export

- [ ] Export frequency, left magnitude, right magnitude, and difference values as CSV
- [ ] Export octave and fractional-octave band values as CSV
- [ ] Record FFT, window, smoothing, normalization, and range settings with exported data
- [ ] Use stable column names and units

### Optional Music-Analysis Features

- [ ] Add a chromagram
- [ ] Display the twelve musical pitch classes over time
- [ ] Add a Constant-Q Transform
- [ ] Display frequency using musically spaced bins
- [ ] Allow note-name labels
- [ ] Allow octave labels
- [ ] Compare left and right chromagrams
- [ ] Compare left and right Constant-Q displays
- [ ] Document the difference between FFT and Constant-Q analysis
- [ ] State that pitch-class energy does not automatically identify a definitive chord or musical key

### Spectral Command and Explanation Features

- [ ] Add `--spectrum-only`
- [ ] Record the selected FFT size
- [ ] Record the selected window function
- [ ] Record the selected frequency range
- [ ] Record the selected smoothing mode
- [ ] Record the selected normalization mode
- [ ] Record the selected time range
- [ ] Add plain-language FFT spectrum explanations
- [ ] Explain the purpose of the Hann window
- [ ] Explain relative decibel normalization
- [ ] State that a file spectrum is not automatically a system frequency response
- [ ] Save spectral settings with exported spectrum plots

### Spectral Validation

- [ ] Generate known-frequency test signals
- [ ] Confirm detection of the 440 Hz left-channel tone
- [ ] Confirm detection of the 660 Hz right-channel tone
- [ ] Test frequencies that do not align exactly with an FFT bin
- [ ] Test silence and very-low-level signals
- [ ] Document frequency resolution and windowing tradeoffs

## Version 0.5.0 — Stereo, Phase, and Spatial-Cue Analysis

### Differentiation Goals

- Connect full-band and frequency-dependent stereo evidence
- Locate mono-cancellation, correlation, delay, and width findings in time and frequency
- State interpretation limits instead of presenting estimates as physical source locations

The purpose of version 0.5.0 is to measure how the left and right channels relate, how they behave when combined to mono, and which measurable cues contribute to the stereo presentation. It does not claim to identify exact physical source locations or definitive perceived width.

### Basic Stereo Measurements

- [ ] Calculate left/right sample-peak difference
- [ ] Calculate left/right RMS difference
- [ ] Calculate full-band channel correlation
- [ ] Estimate interchannel level difference
- [ ] Estimate interchannel time delay
- [ ] Report delay in samples
- [ ] Report delay in milliseconds
- [ ] Detect a one-sided or nearly silent channel
- [ ] Detect possible exact dual mono
- [ ] Detect possible duplicated channels
- [ ] Detect possible left/right channel swaps when a controlled reference permits it
- [ ] Document the limits of interpreting arbitrary stereo program material

### Polarity and Mono Compatibility

- [ ] Detect possible polarity inversion
- [ ] Calculate mono-sum peak
- [ ] Calculate mono-sum RMS
- [ ] Compare stereo level with mono-sum level
- [ ] Measure cancellation when folded to mono
- [ ] Identify frequency regions most affected by mono summing
- [ ] Identify time regions most affected by mono summing
- [ ] Warn when substantial content disappears in mono
- [ ] Create a documented mono-compatibility classification
- [ ] Keep an optional mono-downmix preview file as a later output feature

### Mid/Side Analysis

- [ ] Convert left/right audio to mid/side
- [ ] Calculate mid peak and RMS
- [ ] Calculate side peak and RMS
- [ ] Calculate mid and side crest factors
- [ ] Calculate mid energy
- [ ] Calculate side energy
- [ ] Calculate the mid/side energy ratio
- [ ] Calculate the percentage of energy in mid and side
- [ ] Estimate stereo width using a documented metric
- [ ] Calculate mid/side balance over time
- [ ] Calculate mid/side balance by frequency band
- [ ] Identify a possibly narrow signal
- [ ] Identify a possibly side-heavy signal
- [ ] Plot mid and side spectra
- [ ] Document thresholds used for narrow, moderate, and wide classifications

### Frequency-Dependent Correlation

- [ ] Divide the stereo signal into frequency bands
- [ ] Calculate left/right correlation within each band
- [ ] Plot correlation against frequency
- [ ] Support octave-band correlation
- [ ] Support one-third-octave-band correlation
- [ ] Identify bands with negative correlation
- [ ] Identify bands with low mono compatibility
- [ ] Allow configurable correlation warning thresholds
- [ ] Compare full-band correlation with frequency-dependent correlation
- [ ] Record correlation settings with saved graphs

### Frequency-Dependent Stereo Width

- [ ] Calculate side-to-mid ratio by frequency band
- [ ] Plot estimated width against frequency
- [ ] Support octave-band width analysis
- [ ] Support one-third-octave-band width analysis
- [ ] Identify unusually side-heavy low-frequency regions
- [ ] Identify nearly mono frequency regions
- [ ] Compare width between selected time regions
- [ ] Allow configurable width-warning thresholds

### Interchannel Timing

- [ ] Estimate overall left/right delay
- [ ] Identify the lag of maximum cross-correlation
- [ ] Estimate delay by frequency band when technically reliable
- [ ] Detect changing delay over time
- [ ] Warn when delay may contribute to mono comb filtering
- [ ] Distinguish likely delay from simple polarity inversion
- [ ] Document limitations when channels contain unrelated material

### Phase-Relationship Analysis

- [ ] Add a phase-difference-by-frequency graph
- [ ] Calculate a phase-difference distribution
- [ ] Add frequency-band phase summaries
- [ ] Identify possible frequency-dependent phase rotation
- [ ] Display mono-sum cancellation by frequency
- [ ] Analyze time-varying phase relationships
- [ ] Add configurable phase-warning thresholds
- [ ] Prefer correlation and mono-sum evidence over unsupported phase claims

### Stereo Relationship and Spatial-Cue Visualizations

- [ ] Add an essential static goniometer or vectorscope view
- [ ] Add a full-band correlation meter
- [ ] Add a mid/side energy graph
- [ ] Add a frequency-dependent correlation graph
- [ ] Add a frequency-dependent width graph
- [ ] Add a mono-cancellation-by-frequency graph
- [ ] Add a left/right level-difference graph over time
- [ ] Add an estimated interchannel-delay graph over time
- [ ] Label these as measured stereo relationships rather than exact source-location maps

### Stereo-Event Detection

- [ ] Detect regions that become abruptly narrower or wider
- [ ] Detect sudden channel imbalance
- [ ] Detect possible sudden polarity changes
- [ ] Detect one-channel dropouts
- [ ] Detect possible abrupt channel swaps when evidence permits
- [ ] Detect regions that substantially collapse in mono
- [ ] Detect side-heavy low-frequency regions
- [ ] Report the start time, end time, and duration of each event

### Stereo Validation

- [ ] Generate exact dual-mono test files
- [ ] Generate files with known left/right level differences
- [ ] Generate polarity-inverted test files
- [ ] Generate delayed-channel test files
- [ ] Generate files with known frequency-dependent correlation
- [ ] Generate side-heavy low-frequency test files
- [ ] Generate files with a planted one-channel dropout
- [ ] Generate files with a planted channel swap
- [ ] Verify each measurement and warning against known test conditions
- [ ] State numeric tolerances for delay, correlation, and level estimates

### Interpretation Boundaries

- [ ] Avoid exact physical source-location claims
- [ ] Avoid definitive listener-distance claims
- [ ] Avoid loudspeaker-position estimation
- [ ] Avoid room-acoustics conclusions from arbitrary program material
- [ ] Avoid definitive perceived-width claims
- [ ] Avoid immersive-object coordinate claims

## Version 0.6.0 — Expanded Format and Large-File Support

### Differentiation Goals

- Demonstrate equivalent normalized measurements across supported encodings
- Identify non-stereo inputs and metadata-supported layouts without guessing
- Verify that chunked processing does not change results or create boundary artifacts

This remains a stereo-analysis project. Version 0.6.0 expands the encodings that can be analyzed when a file is stereo, while recognizing and clearly reporting mono or multichannel input without attempting to perform stereo analysis on it.

### WAV Format Support

- [ ] Confirm complete 16-bit PCM support
- [ ] Support 8-bit PCM
- [ ] Support 24-bit PCM
- [ ] Support 32-bit integer PCM
- [ ] Support 32-bit floating-point WAV files
- [ ] Support WAV extensible headers
- [ ] Require exactly two channels before running stereo analysis
- [ ] Identify one-channel input as mono
- [ ] Identify input containing more than two channels as multichannel
- [ ] Report the exact channel count for non-stereo input
- [ ] Inspect a WAV extensible channel mask when present
- [ ] Report a recognized layout only when supported by metadata
- [ ] Report the layout as unknown or unspecified when metadata is absent
- [ ] Never infer an immersive format from channel count alone
- [ ] Never silently analyze only the first two channels of a multichannel file
- [ ] Report filename, encoding, sample rate, bit depth, channel count, duration, and available layout metadata before stopping on non-stereo input
- [ ] Explain that stereo analysis is unavailable for non-stereo input
- [ ] Exit cleanly after reporting non-stereo input
- [ ] Provide clear behavior for unsupported encodings

### Sample-Decoding Architecture

- [ ] Create one decoding layer for every supported WAV encoding
- [ ] Convert supported integer and floating-point inputs to a consistent normalized internal representation
- [ ] Use a documented normalized range such as -1.0 through +1.0
- [ ] Preserve the original encoding and bit-depth metadata for reporting
- [ ] Handle 8-bit PCM unsigned sample values correctly
- [ ] Handle 16-bit PCM signed sample values correctly
- [ ] Handle 24-bit PCM byte assembly and sign extension correctly
- [ ] Handle 32-bit PCM signed sample values correctly
- [ ] Handle 32-bit floating-point values correctly
- [ ] Keep level, dynamics, spectral, and stereo-analysis functions independent of the original bit depth
- [ ] Prevent format-specific scaling assumptions from leaking into measurement functions
- [ ] Document how full scale is defined for each supported encoding

### Optional Additional Formats

- [ ] Investigate AIFF support
- [ ] Investigate FLAC support
- [ ] Limit any additional-format analysis to stereo files
- [ ] Document which stereo features work with each format

### Large-File Reliability

- [ ] Estimate memory requirements before processing
- [ ] Warn before loading unusually large files
- [ ] Process large files in chunks
- [ ] Use cumulative calculations for measurements that do not require the complete file in memory
- [ ] Preserve appropriate overlap between chunks for windowed and spectral measurements
- [ ] Confirm that chunk boundaries do not create false events, silence gaps, or spectral artifacts
- [ ] Allow visualization data to be reduced or summarized without retaining every original sample
- [ ] Add progress reporting for long analyses
- [ ] Report the number of frames processed
- [ ] Measure WAV-reading time
- [ ] Measure sample-decoding time
- [ ] Measure analysis-stage performance
- [ ] Cancel long-running analysis cleanly
- [ ] Avoid leaving incomplete temporary files after cancellation

### Format Validation

- [ ] Generate test files for every supported bit depth
- [ ] Verify correct numeric decoding for each format
- [ ] Test zero-valued samples in every encoding
- [ ] Test half-scale positive and negative samples in every encoding
- [ ] Test maximum positive samples in every encoding
- [ ] Test maximum negative samples in every encoding
- [ ] Test known sine-wave amplitude in every encoding
- [ ] Confirm equivalent normalized results across supported encodings
- [ ] Confirm equivalent peak and RMS measurements across supported encodings
- [ ] Test correct identification of mono input
- [ ] Test correct identification of stereo input
- [ ] Test correct identification of multichannel input
- [ ] Test files with valid channel-mask metadata
- [ ] Test files with absent or ambiguous layout metadata
- [ ] Test malformed and truncated files
- [ ] Test unusual but valid WAV chunks
- [ ] Document limitations of Python's built-in WAV support

## Version 0.7.0 — Visualization and Interactive Exploration

### Differentiation Goals

- Build one linked investigation workspace rather than a collection of disconnected plots
- Use a chronological event navigator to move every relevant view to the same evidence
- Make technical comparisons accessible through shared scales, synchronized selections, and readable exports

The purpose of version 0.7.0 is to display the measurements developed in earlier versions so users can locate, compare, and understand what is happening in the audio. It focuses on presentation, interaction, and connections between measurements rather than creating unsupported new interpretations.

### Waveform Displays

- [ ] Plot left and right waveforms
- [ ] Add separate channel views
- [ ] Add an overlaid channel view
- [ ] Add normalized or shared amplitude scales
- [ ] Keep the shared amplitude scale as the default
- [ ] Display time in seconds or `HH:MM:SS`
- [ ] Add configurable waveform colors
- [ ] Add horizontal zoom and navigation
- [ ] Add selected-time-range highlighting
- [ ] Add sample-level zoom
- [ ] Add a whole-file overview beneath a zoomed view

### Level and Dynamics Overlays

- [ ] Plot the peak envelope
- [ ] Plot the RMS envelope
- [ ] Plot crest factor over time
- [ ] Mark clipped samples and clipping events
- [ ] Mark near-clipping regions
- [ ] Mark silence regions
- [ ] Mark possible dropout regions
- [ ] Display DC offset over time
- [ ] Mark sustained high- and low-level regions
- [ ] Mark sudden gain changes
- [ ] Mark the loudest and quietest active regions
- [ ] Display suggested leading and trailing trim points
- [ ] Allow event markers to be selected
- [ ] Allow users to jump directly to a selected event

### Frequency Visualizations

- [ ] Refine the standard spectrum
- [ ] Refine averaged and peak-hold spectra
- [ ] Refine spectrograms
- [ ] Refine octave and fractional-octave graphs
- [ ] Refine the spectral-difference graph
- [ ] Refine the audio-spectrum waterfall
- [ ] Refine the optional chromagram
- [ ] Refine the optional Constant-Q display
- [ ] Apply consistent frequency, level, and color scales
- [ ] Preserve the technical meanings established in version 0.4.0

### Stereo Relationship and Spatial-Cue Displays

- [ ] Refine the static goniometer or vectorscope
- [ ] Add an optional animated vectorscope
- [ ] Refine the correlation meter
- [ ] Refine the mid/side balance meter
- [ ] Refine the mid/side energy graph
- [ ] Refine frequency-dependent correlation
- [ ] Refine frequency-dependent width
- [ ] Refine the mono-cancellation-by-frequency graph
- [ ] Refine the left/right level-difference graph
- [ ] Refine the estimated interchannel-delay graph
- [ ] Refine the phase-difference graph
- [ ] Keep displays labeled as stereo relationships and spatial cues rather than exact source locations

### Linked Visualizations

- [ ] Allow waveform selection to update the spectrum
- [ ] Highlight the selected waveform range in the spectrogram
- [ ] Recalculate level measurements for the selected range
- [ ] Recalculate correlation for the selected range
- [ ] Recalculate mid/side balance for the selected range
- [ ] Update the goniometer from the selected range
- [ ] List events contained in the selected range
- [ ] Allow a selected clipping or silence event to move every relevant view to that time
- [ ] Keep linked selections synchronized across all active views

### Analysis-Event Navigator

- [ ] Create one chronological timeline of detected analysis events
- [ ] Include clipping, near-clipping, silence, dropout, level-change, spectral, correlation, phase, and mono-compatibility events when available
- [ ] Display the event type, start time, end time, duration, channel, and severity
- [ ] Allow events to be filtered by category
- [ ] Allow events to be filtered by information, warning, or error status
- [ ] Allow events to be sorted by time, severity, or measurement type
- [ ] Allow selection of an event to update every relevant visualization
- [ ] Jump the waveform and spectrogram to the selected event
- [ ] Recalculate local level, spectral, and stereo measurements for the selected event
- [ ] Allow users to move to the previous or next event
- [ ] Allow event markers to be shown or hidden on visualizations
- [ ] Preserve event identifiers for later report and export features

### Visual Evidence Panels

- [ ] Add a basic evidence panel for selected events
- [ ] Display the observed measurement
- [ ] Display the relevant time and frequency range
- [ ] Display the graph or marker supporting the finding
- [ ] Link the evidence panel to the event navigator
- [ ] State important interpretation limitations beside the evidence
- [ ] Prepare evidence data for complete `Why was this flagged?` cards in version 0.8.0

### Optional Playback-Synchronized Displays

- [ ] Add audio playback
- [ ] Add play, pause, stop, and seek controls
- [ ] Add selected-region looping
- [ ] Add a waveform playhead
- [ ] Add a moving spectrogram cursor
- [ ] Synchronize the animated vectorscope with playback
- [ ] Synchronize the correlation meter with playback
- [ ] Synchronize level and mid/side meters with playback
- [ ] Display a current short-time spectrum during playback
- [ ] Allow the live analysis-window duration to be adjusted
- [ ] Document playback and display synchronization tolerances

### Dashboard Layouts

- [ ] Add an overview dashboard
- [ ] Add a levels-and-dynamics dashboard
- [ ] Add a spectrum dashboard
- [ ] Add a stereo-relationship dashboard
- [ ] Add a custom dashboard
- [ ] Allow users to choose which panels are visible
- [ ] Add multiple goniometer and meter layout styles
- [ ] Add linked waveform and stereo-relationship layouts
- [ ] Save dashboard configurations

### Interactive Controls

- [ ] Add zoom, pan, and reset-view controls
- [ ] Allow time-range selection
- [ ] Allow frequency-range selection
- [ ] Show exact values on hover
- [ ] Allow graph points and event markers to be selected
- [ ] Enable or disable individual channels
- [ ] Switch between linear and logarithmic axes when appropriate
- [ ] Change FFT and smoothing settings from the visualization interface
- [ ] Change graph dynamic range
- [ ] Show or hide event markers and annotations
- [ ] Restore default visualization settings

### Comparison Views

- [ ] Compare left with right
- [ ] Compare the full file with a selected region
- [ ] Compare an earlier region with a later region
- [ ] Compare stereo with the mono sum
- [ ] Compare mid with side
- [ ] Compare raw with smoothed spectra
- [ ] Compare averaged with peak-hold spectra
- [ ] Use shared scales by default for technical comparisons
- [ ] Keep two-file visual comparison as an optional later extension

### Saving and Exporting Visualizations

- [ ] Save an individual plot
- [ ] Save all active plots
- [ ] Save the current dashboard
- [ ] Support PNG output
- [ ] Support SVG output for scalable graphs
- [ ] Investigate PDF output where technically appropriate
- [ ] Allow image-resolution selection
- [ ] Allow light or dark presentation styles
- [ ] Allow annotations to be included or excluded
- [ ] Include the source filename
- [ ] Include the program version
- [ ] Include analysis settings
- [ ] Record the represented frequency or time range
- [ ] Use consistent output filenames
- [ ] Prevent unintended overwriting

### Accessibility and Readability

- [ ] Use colorblind-safe palettes
- [ ] Avoid communicating warnings through color alone
- [ ] Add adjustable font size
- [ ] Add a high-contrast mode
- [ ] Add keyboard-accessible controls
- [ ] Use readable labels and units
- [ ] Use consistent channel colors
- [ ] Add text descriptions for important saved visualizations and reports
- [ ] Avoid overcrowded graphs
- [ ] Allow labels and annotations to be hidden

### Visualization Performance

- [ ] Downsample waveform display data without changing measurement calculations
- [ ] Limit displayed spectrogram resolution when necessary
- [ ] Retain full-resolution measurement results separately
- [ ] Avoid recalculating unchanged measurements
- [ ] Cache selected analysis results
- [ ] Show progress for expensive visualization generation
- [ ] Cancel graph generation safely
- [ ] Avoid freezing the interface on long files

### Visualization Validation

- [ ] Confirm plotted peaks match numerical measurements
- [ ] Confirm time markers align with planted events
- [ ] Confirm shared scales preserve channel differences
- [ ] Confirm selection boundaries produce the correct calculations
- [ ] Confirm linked views remain synchronized
- [ ] Confirm saved plots match displayed plots
- [ ] Confirm SVG and PDF exports preserve labels where supported
- [ ] Test large files
- [ ] Test different screen sizes
- [ ] Test light and dark themes
- [ ] Test colorblind-safe palettes
- [ ] Test keyboard navigation

### Core Version 0.7.0 Scope

- [ ] Complete waveform displays
- [ ] Complete level and event overlays
- [ ] Complete linked time selection
- [ ] Complete refined frequency views
- [ ] Complete refined stereo-relationship views
- [ ] Complete hover-value inspection
- [ ] Complete shared-scale comparisons
- [ ] Complete PNG and SVG export
- [ ] Complete consistent accessible styling

### Optional Version 0.7.0 Scope

- [ ] Complete audio playback
- [ ] Complete animated vectorscope behavior
- [ ] Complete fully customizable dashboards
- [ ] Complete light and dark themes
- [ ] Complete PDF visualization export
- [ ] Complete two-file visual comparison

## Version 0.8.0 — Quality-Control Profiles

### Differentiation Goals

- Make rule applicability, evidence, confidence, and limitations part of every meaningful QC conclusion
- Preserve the difference between exact facts, deterministic detections, estimates, and heuristics
- Explain reviewed or overridden findings without deleting the original automated evidence

The purpose of version 0.8.0 is to apply explicit, configurable technical requirements to the measurements created in earlier releases and explain every pass, warning, failure, and inconclusive result. It evaluates documented technical rules rather than artistic quality.

### Quality-Control Profile Structure

- [ ] Load technical delivery requirements from a JSON profile
- [ ] Require a profile name
- [ ] Require a profile version
- [ ] Allow a profile description
- [ ] Record the intended use
- [ ] Record the profile author or source
- [ ] Record profile creation and modification dates
- [ ] Record units with every configurable measurement
- [ ] Allow explanatory notes
- [ ] Allow users to create custom profiles
- [ ] Preserve the exact profile and version used for each analysis

### Format Requirements

- [ ] Validate the required stereo channel count
- [ ] Validate an exact sample rate
- [ ] Validate a list of permitted sample rates
- [ ] Validate minimum or exact bit depth
- [ ] Validate permitted encoding types
- [ ] Validate minimum and maximum duration
- [ ] Validate required WAV structure when applicable
- [ ] Validate whether floating-point WAV is permitted
- [ ] Validate whether absent or unspecified layout metadata is permitted

### Level and Dynamics Requirements

- [ ] Validate maximum permitted sample peak
- [ ] Validate minimum required headroom
- [ ] Validate clipped-sample tolerance
- [ ] Validate near-clipping tolerance
- [ ] Validate maximum DC offset
- [ ] Validate maximum left/right peak difference
- [ ] Validate maximum left/right RMS difference
- [ ] Validate a permitted crest-factor range
- [ ] Validate a permitted windowed-RMS range
- [ ] Validate maximum leading silence
- [ ] Validate maximum trailing silence
- [ ] Validate maximum interior silence
- [ ] Validate minimum active-audio percentage
- [ ] Validate dropout tolerance
- [ ] Validate sudden gain-change thresholds

### Spectral Requirements

- [ ] Validate permitted low-frequency energy
- [ ] Validate permitted near-Nyquist energy
- [ ] Validate required frequency-band energy ranges
- [ ] Validate maximum left/right spectral difference by band
- [ ] Validate the presence or absence of specific tones
- [ ] Validate maximum narrowband peak level
- [ ] Allow profile-defined frequency regions to be ignored
- [ ] Require a minimum event duration before a spectral condition is flagged
- [ ] Avoid applying subjective spectral rules unless a profile explicitly defines them

### Stereo Requirements

- [ ] Validate maximum left/right level imbalance
- [ ] Validate minimum full-band correlation
- [ ] Validate minimum low-frequency correlation
- [ ] Validate maximum side-to-mid ratio
- [ ] Validate maximum side-heavy low-frequency content
- [ ] Validate maximum estimated interchannel delay
- [ ] Validate maximum mono-sum cancellation
- [ ] Add profile-controlled dual-mono warnings
- [ ] Add profile-controlled duplicated-channel errors
- [ ] Add profile-controlled polarity-inversion warnings
- [ ] Add profile-controlled one-channel-dropout errors

### Rule Applicability

- [ ] Allow each rule to specify applicable channels
- [ ] Allow each rule to specify a time range
- [ ] Allow each rule to specify a frequency range
- [ ] Allow each rule to require a minimum active signal level
- [ ] Allow each rule to require a minimum event duration
- [ ] Allow separate warning and error thresholds
- [ ] Allow a minimum confidence requirement
- [ ] Define disabled-rule behavior
- [ ] Define not-applicable behavior
- [ ] Avoid evaluating correlation and phase rules during silence or negligible signal

### Finding States and Overall Status

- [ ] Support `PASS`
- [ ] Support `INFORMATION`
- [ ] Support `WARNING`
- [ ] Support `ERROR`
- [ ] Support `NOT APPLICABLE`
- [ ] Support `INSUFFICIENT EVIDENCE`
- [ ] Define overall `PASS` behavior
- [ ] Define overall `PASS WITH WARNINGS` behavior
- [ ] Define overall `FAIL` behavior
- [ ] Define overall `INCOMPLETE` behavior
- [ ] Prevent low-confidence heuristic warnings from being treated like exact format failures
- [ ] Display finding, warning, and error totals
- [ ] Summarize findings at the end of the report
- [ ] Keep warnings and errors visible in quiet mode
- [ ] Add color-coded results without relying on color alone
- [ ] Add `--color auto`
- [ ] Add `--color always`
- [ ] Add `--color never`

### Confidence and Limitation Indicators

- [ ] Assign an evidence-based confidence level to applicable detections
- [ ] Support high, moderate, low, and insufficient-evidence classifications
- [ ] Document how confidence is determined for each detection type
- [ ] Distinguish exact tests from heuristic warnings
- [ ] Treat exact duplicated-channel detection as different from inferred channel-swap detection
- [ ] Reduce confidence when the selected region is too short or contains insufficient related content
- [ ] Display confidence without implying statistical certainty unless a statistical method is actually used
- [ ] Display the known limitations of each measurement
- [ ] Prevent low-confidence findings from being presented as definitive errors
- [ ] Record confidence and limitation information in exported results

### Why-Was-This-Flagged Evidence Cards

- [ ] Generate an evidence card for each warning and error
- [ ] Display the finding name and severity
- [ ] Display the observed value
- [ ] Display the configured threshold or comparison rule
- [ ] Display the formula or method used
- [ ] Display the relevant channel
- [ ] Display the relevant time range
- [ ] Display the relevant frequency range when applicable
- [ ] Display supporting graph excerpts or event markers
- [ ] Display the confidence level
- [ ] Display interpretation limitations
- [ ] Explain what the finding may indicate
- [ ] Explain what the finding does not prove
- [ ] Link each evidence card back to the event navigator
- [ ] Preserve evidence cards in later HTML reports

### Profile Validation

- [ ] Confirm required profile fields exist
- [ ] Confirm every value uses the expected data type
- [ ] Confirm units are recognized
- [ ] Confirm warning and error thresholds are logically ordered
- [ ] Confirm minimum values do not exceed maximum values
- [ ] Confirm frequency ranges are valid
- [ ] Report unknown rules
- [ ] Reject duplicate rule identifiers
- [ ] Confirm the profile version is supported
- [ ] Provide precise profile-validation errors

### Profile Discovery and Management

- [ ] Add `--list-profiles`
- [ ] Add `--show-profile`
- [ ] Add `--validate-profile`
- [ ] Allow a profile to be referenced by file path
- [ ] Allow users to inspect every rule before analysis
- [ ] Allow users to copy a profile as a custom starting point
- [ ] Compare two profile versions
- [ ] Display which profile and version produced a result

### Suppressions, Acknowledgments, and Overrides

- [ ] Allow a rule to be suppressed for one run
- [ ] Allow a rule to be suppressed for a selected time range
- [ ] Allow an explanatory note to be attached to a finding
- [ ] Allow a warning to be marked as reviewed
- [ ] Preserve the original finding after acknowledgment
- [ ] Record the source of an override
- [ ] Record the reason for an override
- [ ] Never silently hide overridden or suppressed results
- [ ] Preserve overrides in later reports and reproducible packages

### Exit Status Codes

- [ ] Return a documented exit code for pass
- [ ] Return a documented exit code for pass with warnings
- [ ] Return a documented exit code for QC failure
- [ ] Return a documented exit code for incomplete analysis
- [ ] Return a documented exit code for an invalid profile
- [ ] Return a documented exit code for file or program failure
- [ ] Allow batch tools and other programs to use the QC result automatically

### Quality-Control Validation

- [ ] Test a file that passes every rule
- [ ] Test files exactly on each threshold
- [ ] Test files just inside each threshold
- [ ] Test files just outside each threshold
- [ ] Test one planted warning
- [ ] Test multiple simultaneous warnings
- [ ] Test multiple simultaneous errors
- [ ] Test not-applicable rules
- [ ] Test insufficient-evidence conditions
- [ ] Test invalid profiles
- [ ] Test conflicting thresholds
- [ ] Test suppressions and acknowledged findings
- [ ] Test exact and heuristic detections
- [ ] Confirm that every evidence card matches its underlying calculation
- [ ] Record which profile and version produced each result

### Interpretation and Certification Boundaries

- [ ] State that the program evaluates only the rules implemented in the selected profile
- [ ] Avoid claiming broadcast certification without exact validated authority
- [ ] Avoid claiming Dolby approval
- [ ] Avoid claiming mastering approval
- [ ] Avoid claiming general industry compliance
- [ ] Distinguish passing implemented checks from official certification

## Version 0.9.0 — Reports and Batch Processing

### Differentiation Goals

- Treat a folder as a delivery session with consistency checks rather than merely looping over files
- Make batch work resumable, content-aware, privacy-conscious, and reproducible
- Distinguish exact identity, equivalent decoded audio, and similar measurements

The purpose of version 0.9.0 is to process many stereo files efficiently and produce results that people and software can review, archive, compare, sanitize, and reproduce.

### Individual Report Formats

- [ ] Preserve a readable Terminal report
- [ ] Export complete machine-readable results as JSON
- [ ] Export tabular summaries as CSV
- [ ] Export detected events as CSV
- [ ] Export spectral and frequency-band data as CSV when requested
- [ ] Generate a self-contained HTML report
- [ ] Include metadata, levels, spectra, stereo measurements, QC status, events, evidence cards, plots, settings, and limitations in HTML
- [ ] Investigate PDF generation from the validated HTML report
- [ ] Clearly identify unavailable, skipped, and not-applicable measurements

### Report Customization

- [ ] Allow report-format selection
- [ ] Allow a custom report title
- [ ] Allow organization, project, or session names
- [ ] Allow analyst notes
- [ ] Allow users to choose included measurement sections
- [ ] Allow users to choose included graphs
- [ ] Allow brief or detailed evidence
- [ ] Allow light or dark report styles
- [ ] Allow a custom footer
- [ ] Allow full paths to be included or hidden
- [ ] Allow diagnostic information to be included or excluded

### Batch Input Selection

- [ ] Analyze every supported stereo file in a folder
- [ ] Add recursive subfolder analysis as an option
- [ ] Accept multiple explicitly selected files
- [ ] Accept a supplied file list
- [ ] Add filename include patterns
- [ ] Add filename exclude patterns
- [ ] Add ignored-folder rules
- [ ] Use a stable file-processing order
- [ ] Report mono, multichannel, and unsupported files separately without attempting stereo analysis

### Batch Progress and Control

- [ ] Display the current file and file count
- [ ] Display overall progress
- [ ] Display current pass, warning, failure, and unsupported counts
- [ ] Continue processing after one file fails
- [ ] Record every failure
- [ ] Allow clean cancellation
- [ ] Preserve completed results after cancellation
- [ ] Resume an interrupted batch
- [ ] Skip safely completed files when appropriate
- [ ] Reanalyze files whose contents or settings changed
- [ ] Limit parallel processing
- [ ] Avoid exhausting available memory
- [ ] Estimate remaining time cautiously
- [ ] Summarize total batch-processing time

### Batch Summary

- [ ] Create one summary row per discovered file
- [ ] Include file format, duration, peak, QC status, warning count, and error count
- [ ] Sort by filename
- [ ] Sort by QC status
- [ ] Sort by sample rate
- [ ] Sort by bit depth
- [ ] Sort by duration
- [ ] Sort by peak
- [ ] Sort by warning or error count
- [ ] Export the batch summary as CSV and HTML

### Folder and Session Consistency Checks

- [ ] Detect mismatched sample rates
- [ ] Detect mismatched bit depths
- [ ] Detect mismatched channel counts
- [ ] Detect unexpected duration differences
- [ ] Detect missing expected filenames
- [ ] Detect duplicate filenames in different folders
- [ ] Detect byte-for-byte duplicate files
- [ ] Detect files with identical decoded audio but different containers or metadata
- [ ] Identify suspiciously similar files without calling them identical
- [ ] Validate filename conventions
- [ ] Detect missing expected left/right pairs when a workflow defines them
- [ ] Detect inconsistent leading or trailing silence
- [ ] Identify files that differ from the dominant session format
- [ ] Explain how the expected session format was determined

### Two-File Comparison

- [ ] Compare original and processed files
- [ ] Compare mix version A with version B
- [ ] Compare metadata
- [ ] Compare duration
- [ ] Compare peak and RMS
- [ ] Compare spectra
- [ ] Compare stereo correlation and width
- [ ] Compare mid/side measurements
- [ ] Compare detected events
- [ ] Compare QC status changes
- [ ] Distinguish exact identity from similarity
- [ ] Require a checksum or sample comparison before calling files identical

### Reproducible Analysis Packages

- [ ] Export one self-contained analysis-package folder
- [ ] Include an HTML report
- [ ] Include machine-readable measurements as JSON
- [ ] Include detected events as CSV
- [ ] Include spectral data as CSV when requested
- [ ] Include saved plots and dashboards
- [ ] Include active analysis settings as JSON
- [ ] Include the command used to create the analysis
- [ ] Include the program, Python, and dependency versions
- [ ] Include the QC profile and profile version
- [ ] Include input-file identity information without duplicating copyrighted source audio by default
- [ ] Include diagnostic logs when requested
- [ ] Include confidence and limitation information
- [ ] Include `Why was this flagged?` evidence cards
- [ ] Add a manifest listing every package file
- [ ] Add checksums for package contents and the analyzed source file
- [ ] Allow another user to reproduce the analysis with the same settings
- [ ] Document which results may vary across software or dependency versions

### Checksums and File Identity

- [ ] Calculate SHA-256 for analyzed source files
- [ ] Calculate checksums for generated package files
- [ ] Detect whether a source file changed after analysis
- [ ] Distinguish same filename from same checksum
- [ ] Distinguish same checksum from equivalent decoded audio
- [ ] Distinguish exact identity from similar measurements
- [ ] Use identity information to support safe resume and caching

### Analysis Caching

- [ ] Build cache keys from source checksum, program version, profile version, and analysis settings
- [ ] Reuse results only when all relevant cache inputs match
- [ ] Reanalyze after source, software, profile, or setting changes
- [ ] Allow reports to be regenerated from cached measurements
- [ ] Allow users to disable caching
- [ ] Allow users to inspect and clear the cache
- [ ] Detect and recover from corrupted cache entries

### Report and Data Schema Versioning

- [ ] Add a schema version to JSON output
- [ ] Add a schema version to CSV output definitions
- [ ] Add a schema version to reproducible packages
- [ ] Keep schema version separate from program version
- [ ] Recognize older supported report schemas
- [ ] Document migration behavior for future schemas
- [ ] Use stable field and column names with explicit units

### Privacy and Sanitization

- [ ] Allow reports to show only filenames
- [ ] Allow full paths to be redacted
- [ ] Remove usernames from paths when requested
- [ ] Allow selected metadata to be excluded
- [ ] Allow diagnostic logs to be excluded
- [ ] Generate a sanitized shareable analysis package
- [ ] Preview information that will be exported
- [ ] Avoid copying source audio into packages by default
- [ ] Document possible privacy exposure from filenames, metadata, paths, and analyst notes

### Batch Logs and Failure Recovery

- [ ] Record batch start and end times
- [ ] Record files discovered
- [ ] Record files skipped
- [ ] Record files analyzed
- [ ] Record files reused from cache
- [ ] Record mono, multichannel, and unsupported files
- [ ] Record errors and optional tracebacks
- [ ] Record cancellation state
- [ ] Save resume information
- [ ] Support per-file diagnostic logs
- [ ] Support one complete batch log
- [ ] Expand quiet-mode behavior for automated batch processing

### Report Accessibility

- [ ] Use semantic HTML headings
- [ ] Use readable and responsive tables
- [ ] Add text descriptions for important graphs
- [ ] Use colorblind-safe status indicators
- [ ] Use written status labels in addition to color
- [ ] Support keyboard navigation
- [ ] Add a printable layout
- [ ] Support different screen sizes

### Version 0.9.0 Validation

- [ ] Test individual reports
- [ ] Test large batches
- [ ] Test empty folders
- [ ] Test nested folders
- [ ] Test unsupported files mixed with valid files
- [ ] Test duplicate files
- [ ] Test changed files with unchanged names
- [ ] Test interrupted and resumed batches
- [ ] Test corrupted cache entries
- [ ] Test profile changes
- [ ] Test program-version changes
- [ ] Test redacted and sanitized reports
- [ ] Test deterministic JSON and CSV schemas
- [ ] Test reports containing unavailable measurements
- [ ] Test HTML accessibility

## Version 1.0.0 — Tested and Installable Release

### Differentiation Goals

- Make trust auditable through controlled signals, justified tolerances, regression tests, and stable schemas
- Publish explicit supported environments, limitations, and interpretation boundaries
- Demonstrate that every core claim has a documented validation path

### Automated Testing

- [ ] Add unit tests for every major calculation
- [ ] Add integration tests for complete file analysis
- [ ] Test known-frequency signals
- [ ] Test known-amplitude signals
- [ ] Test silent signals
- [ ] Test clipped signals
- [ ] Test dual-mono signals
- [ ] Test polarity-inverted signals
- [ ] Test delayed-channel signals
- [ ] Test every supported bit depth
- [ ] Test invalid and corrupted inputs
- [ ] Add automated testing with GitHub Actions

### Code Quality

- [ ] Add type hints to public functions
- [ ] Add docstrings to public functions
- [ ] Apply consistent formatting
- [ ] Add linting
- [ ] Separate major responsibilities into modules
- [ ] Document important formulas and references
- [ ] Review memory and performance behavior

### Packaging and Releases

- [ ] Package the program as an installable command-line tool
- [ ] Support an `audio-report` command
- [ ] Add a changelog
- [ ] Add a license
- [ ] Add release notes
- [ ] Create versioned GitHub releases
- [ ] Publish version 1.0.0

### User Guidance and Capability Information

- [ ] Add a command that lists supported capabilities
- [ ] List supported file types
- [ ] List supported encodings and bit depths
- [ ] List supported channel layouts
- [ ] List available analysis modes
- [ ] List available visualization types
- [ ] List known limitations
- [ ] Keep capability information synchronized with the README
- [ ] Add a system-information command for troubleshooting
- [ ] Complete plain-language explanations of every measurement
- [ ] Add example reports and screenshots

### Stable Product Definition and CLI

- [ ] Define supported operating systems and Python versions
- [ ] Define supported file formats and WAV encodings
- [ ] Define the stereo-only scope and non-stereo behavior
- [ ] Define the core measurement, visualization, QC, and export features included in 1.0.0
- [ ] Stabilize option names, defaults, exit codes, output locations, and error behavior
- [ ] Stabilize report and QC-profile schemas or document compatibility rules
- [ ] Add `audio-report --capabilities`
- [ ] Add `audio-report --version`

### Package Architecture

- [ ] Adopt a `pyproject.toml` package configuration
- [ ] Use a `src/` package layout
- [ ] Separate CLI, decoding, metadata, levels, spectrum, stereo, visualization, QC, reports, batch, models, and errors into focused modules
- [ ] Keep measurement logic independent from presentation logic
- [ ] Keep file decoding independent from measurement logic
- [ ] Keep QC decisions independent from raw measurements
- [ ] Keep optional visualization features from breaking text-only analysis

### Controlled Test-Signal Laboratory

- [ ] Generate silence and known-amplitude sine waves
- [ ] Generate multiple simultaneous tones
- [ ] Generate white and pink noise
- [ ] Generate clipping and DC-offset conditions
- [ ] Generate leading, trailing, and interior silence
- [ ] Generate level imbalance, dual mono, polarity inversion, and known channel delay
- [ ] Generate frequency-dependent correlation and side-heavy low-frequency conditions
- [ ] Preserve planted conditions and expected results as test metadata

### Numerical Tolerances and Regression Testing

- [ ] Define justified tolerances for frequency, level, delay, correlation, and timing results
- [ ] Base tolerances on FFT resolution, window choice, sample rate, window duration, and floating-point precision
- [ ] Add a permanent regression test for every corrected defect
- [ ] Add stable reference outputs for JSON, CSV, HTML, and plot metadata
- [ ] Review unexpected reference-output changes before acceptance

### Continuous Integration and Cross-Platform Testing

- [ ] Run required checks on pull requests and pushes to `main`
- [ ] Run tests, formatting, linting, type checking, package building, installation checks, CLI smoke tests, and schema validation
- [ ] Prevent merging when required checks fail
- [ ] Test supported macOS, Windows, and Linux environments
- [ ] Test every supported Python version
- [ ] Test path, permission, terminal, font, and headless-display differences
- [ ] Claim support only for environments that are actually tested

### Input Safety and Resilience

- [ ] Treat WAV files, profile JSON, filenames, paths, and metadata as untrusted input
- [ ] Test malformed headers, impossible sizes, truncated chunks, invalid text, and unexpected metadata
- [ ] Reject dangerous generated paths and path traversal
- [ ] Escape untrusted metadata in HTML output
- [ ] Limit resource use for unreasonable declared file sizes or nested profile data
- [ ] Fail cleanly without leaving misleading partial outputs

### Performance and Benchmarks

- [ ] Define expected memory behavior and large-file limits
- [ ] Benchmark decoding, peak/RMS, FFT, spectrogram, stereo correlation, reporting, and batch throughput
- [ ] Detect significant performance regressions
- [ ] Document performance expectations without promising unsupported real-time behavior

### Complete Documentation and Examples

- [ ] Add installation, quick-start, command, measurement, formula, units, format, QC, report, batch, visualization, troubleshooting, privacy, and limitation documentation
- [ ] Keep the README approachable and move detailed material into `docs/`
- [ ] Include small project-created or legally redistributable test WAV files
- [ ] Include example Terminal output, plots, HTML reports, QC profiles, batch summaries, and reproducible packages

### Accessibility and Dependency Review

- [ ] Complete an accessibility review of interactive and exported content
- [ ] Declare dependency version ranges in `pyproject.toml`
- [ ] Separate optional visualization or playback dependencies when practical
- [ ] Test minimum and current supported dependency versions
- [ ] Review dependency licenses
- [ ] Document reproducible development-environment setup

### Project Maintenance Files

- [ ] Add `CONTRIBUTING.md`
- [ ] Add bug-report and feature-request templates
- [ ] Add a pull-request template
- [ ] Document development and testing setup
- [ ] Decide whether a code of conduct is appropriate

### Release Candidate and Definition of Done

- [ ] Publish alpha, beta, or release-candidate versions when useful
- [ ] Test a release candidate before publishing 1.0.0
- [ ] Require controlled tests for every core measurement
- [ ] Require correct decoding for every supported format
- [ ] Require complete end-to-end tests for major workflows
- [ ] Require stable CLI behavior and versioned report schemas
- [ ] Require recoverable batch processing
- [ ] Require safe escaping of untrusted report content
- [ ] Require documentation to match actual behavior
- [ ] Require all supported-platform checks to pass
- [ ] Require explicit known limitations
- [ ] Publish release notes, installation instructions, supported features, known limitations, documentation links, and release-asset checksums

## Future Research and Expansion

Potential features after version 1.0:

### Loudness

- [ ] Integrated loudness
- [ ] Momentary loudness
- [ ] Short-term loudness
- [ ] Loudness range
- [ ] True-peak measurement
- [ ] Peak-to-loudness ratio
- [ ] Loudness-normalization preview
- [ ] Standard-specific loudness profiles

### Future Advanced Level and Dynamics Analysis

- [ ] Calculate definitive signal-to-noise ratio when reference regions are known
- [ ] Allow user-defined signal and noise region selection
- [ ] Estimate compressor attack and release behavior
- [ ] Add detailed transient classification
- [ ] Add advanced click and pop analysis
- [ ] Add long-term program-dynamics classification

### Metadata

- [ ] Broadcast Wave Format metadata inspection
- [ ] Time-reference inspection
- [ ] Origination metadata inspection
- [ ] Metadata consistency checks

### Interfaces

- [ ] Interactive graphical interface
- [ ] Drag-and-drop file selection
- [ ] Interactive zoom and time-range selection
- [ ] Real-time audio-input analysis

### Multichannel and Immersive Audio

- [ ] Generalize channel handling beyond stereo
- [ ] Validate common multichannel layouts
- [ ] Detect silent or duplicated multichannel assignments
- [ ] Inspect LFE-band content
- [ ] Inspect multichannel metadata
- [ ] Research ADM/BWF metadata parsing
- [ ] Develop a separate immersive-audio delivery validator

## Measurement Terminology and Boundaries

- The FFT graph represents the frequency spectrum of the selected audio file.
- It should not be called a system frequency response unless a known test signal and measurement process are used.
- Digital measurements in dBFS should not be described as acoustic SPL without a calibrated measurement chain.
- Relative spectral magnitudes should not be presented as absolute calibrated levels.
- Unsupported formats should produce a clear limitation message rather than an unreliable result.
- Every measurement should be documented and verified against controlled test data before being treated as production-ready.
