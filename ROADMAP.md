# Audio File Report Roadmap

Audio File Report is developing from a basic stereo WAV inspector into an explainable stereo-analysis and quality-control tool.

This roadmap gives an approachable overview of the planned releases. The current documented release is 0.2.0, and the full technical checklists, validation requirements, and implementation notes are available in the [Detailed Development Plan](docs/DEVELOPMENT_PLAN.md).

The roadmap is a working plan. Features may move between releases as the project develops and technical dependencies become clearer.

## Intended Differentiation

Audio File Report is intended to be more than a collection of meters and graphs. Its distinguishing workflow is:

```text
Inspect → Measure → Locate → Explain → Validate → Reproduce
```

Across the releases, the project aims to differentiate through:

- Evidence-linked findings tied to exact time and frequency regions
- Confidence and limitation indicators for heuristic conclusions
- Linked level, spectral, stereo, and event views
- Configurable QC rules with plain-language explanations
- Controlled test signals and documented numerical tolerances
- Reproducible analysis packages with settings, versions, and checksums
- Clear separation between measured facts, estimates, warnings, and unsupported claims
- Non-destructive analysis that never alters the source audio by default

See [Product Differentiation](docs/PRODUCT_DIFFERENTIATION.md) for the full strategy.

## 0.2.0 — Initial Stereo Analyzer

Status: **Complete**

- Read 16-bit stereo PCM WAV files
- Report basic file metadata and duration
- Separate left and right channels
- Apply a Hann window and calculate an FFT
- Plot left and right frequency spectra
- Organize the program into focused functions
- Publish the project and documentation on GitHub

## 0.2.0 — Reliable CLI and File Handling

Make the existing analyzer easier and safer to use.

- Replace manual argument handling with a proper command-line interface
- Add help, version, brief, verbose, and quiet modes
- Add clear graph display and saving controls
- Validate file paths and WAV structure
- Provide friendly errors and optional detailed diagnostics
- Improve metadata formatting and dependency documentation

**Differentiation focus:** Make technical analysis approachable without hiding diagnostic detail from advanced users.

## 0.3.0 — Levels and Dynamics

Measure how high, average, variable, silent, or potentially damaged each channel is over time.

- Peak, RMS, headroom, crest factor, and DC offset
- Windowed level and dynamic-envelope analysis
- Clipping, near-clipping, silence, and dropout detection
- Level distribution and left/right level comparison
- Peak-normalization previews without modifying the source audio
- Controlled test files with known expected measurements

**Differentiation focus:** Turn level statistics into time-located, testable events rather than presenting only whole-file meter values.

## 0.4.0 — Spectral Analysis

Describe which frequencies are present and how spectral content changes over time.

- Dominant frequencies and spectral peak detection
- Configurable FFT, window, smoothing, range, and normalization
- Averaged and peak-hold spectra
- Spectrogram, octave bands, spectral difference, and waterfall views
- Numeric band-energy tables and spectral-data export
- Optional chromagram and Constant-Q music-analysis views
- Controlled frequency-domain validation

**Differentiation focus:** Connect multiple spectral views to exact numeric data, shared channel normalization, selected regions, and exportable evidence.

## 0.5.0 — Stereo, Phase, and Spatial-Cue Analysis

Measure how the left and right channels relate and how the file behaves when combined to mono.

- Correlation, level difference, delay, polarity, and dual-mono checks
- Mono-cancellation and compatibility analysis
- Mid/side measurements
- Frequency-dependent correlation and stereo-width estimates
- Essential stereo-relationship and spatial-cue graphs
- Event detection with explicit interpretation limits

The tool will visualize measurable stereo cues without claiming exact physical source locations or definitive perceived width.

**Differentiation focus:** Combine frequency-dependent correlation, mono cancellation, mid/side evidence, event timestamps, and explicit interpretation limits.

## 0.6.0 — Expanded Stereo WAV Support

Make the stereo measurements work across realistic WAV encodings and large files.

- 8-, 16-, 24-, and 32-bit integer PCM
- 32-bit floating-point WAV and extensible WAV headers
- One normalized internal sample representation
- Correct mono and multichannel identification without non-stereo analysis
- Metadata-supported layout recognition without guessing
- Chunked large-file processing and cross-format validation
- Optional investigation of stereo AIFF and FLAC

**Differentiation focus:** Demonstrate measurement parity across encodings and identify non-stereo layouts honestly without guessing or silently analyzing the wrong channels.

## 0.7.0 — Visualization and Interactive Exploration

Connect the measurements through an accessible visual investigation workspace.

- Waveforms with level, clipping, silence, and event overlays
- Refined frequency and stereo-relationship displays
- Linked time selections across waveform, spectrum, and stereo views
- Chronological analysis-event navigator
- Basic visual evidence panels
- Comparison views, dashboards, and accessible exports
- Optional playback-synchronized and animated displays

**Differentiation focus:** Create a linked investigation workspace where one selected event updates every relevant measurement and visualization.

## 0.8.0 — Quality-Control Profiles

Apply explicit technical requirements and explain every result.

- Versioned JSON quality-control profiles
- Format, level, spectral, and stereo rules
- Rule applicability by channel, time, frequency, signal level, and duration
- Pass, information, warning, error, not-applicable, and insufficient-evidence states
- Confidence and limitation indicators
- “Why was this flagged?” evidence cards
- Profile validation, overrides, acknowledgments, and automation-friendly exit codes

The tool will report which implemented rules passed; it will not claim unsupported official certification.

**Differentiation focus:** Explain every finding with evidence, threshold, method, confidence, limitations, and applicability conditions.

## 0.9.0 — Reports and Batch Processing

Support practical stereo-delivery inspection across files and sessions.

- Terminal, JSON, CSV, HTML, and potential PDF reports
- Folder, recursive, and pattern-based batch input
- Progress, cancellation, recovery, and resumable analysis
- Batch summaries and folder/session consistency checks
- Two-file comparison
- Reproducible analysis packages
- Checksums, safe caching, versioned schemas, and privacy controls

**Differentiation focus:** Produce resumable session-level QC and self-contained, privacy-aware packages that another person can inspect and reproduce.

## 1.0.0 — Trusted, Tested, and Installable Release

Deliver a stable release that another person can install, understand, and verify.

- Installable `audio-report` command and modular package structure
- Stable CLI, schemas, exit codes, and supported-feature definitions
- Unit, integration, regression, and end-to-end tests
- Controlled test-signal laboratory with documented tolerances
- Automated GitHub checks and tested platform support
- Safe handling of malformed and untrusted input
- Performance benchmarks and complete documentation
- Accessible examples, reports, and visualizations
- Semantic versioning, changelog, license, release candidate, and GitHub release

Version 1.0.0 does not require every optional experiment to be complete. It means the declared core features are validated, documented, and stable.

**Differentiation focus:** Make trust auditable through controlled test signals, numerical tolerances, regression tests, stable schemas, and explicit boundaries.

## Future Research

Possible work after version 1.0.0 includes:

- True peak and standardized loudness measurements
- Advanced level, noise, transient, and dynamics analysis
- Broadcast Wave Format metadata inspection
- Additional interfaces and real-time input
- A separate multichannel and immersive-audio delivery validator

## Project Boundaries

- The project remains focused on stereo analysis.
- Mono and multichannel files may be identified and described but will not receive stereo analysis.
- A file spectrum is not automatically a system frequency response.
- Digital dBFS measurements are not acoustic SPL without a calibrated measurement chain.
- Heuristic findings will include confidence and limitations rather than being presented as facts.
- Unsupported formats and inconclusive measurements will produce clear explanations rather than unreliable results.
