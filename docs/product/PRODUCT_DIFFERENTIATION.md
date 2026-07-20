# Product Differentiation Strategy

## Purpose 

Audio File Report is not intended to compete by displaying the largest possible number of meters. Its intended distinction is an explainable, evidence-first workflow for offline stereo-file analysis and quality control.

The product concept is:

```text
Inspect → Measure → Locate → Explain → Validate → Reproduce
```

The tool should help a user move from a broad question—“Is anything technically unusual in this file?”—to a precise, reviewable answer tied to measurements, time ranges, frequency ranges, settings, confidence, and known limitations.

## Position Relative to Existing Tool Categories

Existing tools already demonstrate strong capabilities in several adjacent categories:

- [`ffprobe`](https://ffmpeg.org/ffprobe.html) extracts media-container and stream information in human- and machine-readable forms.
- [NUGEN Visualizer](https://nugenaudio.com/visualizer/) provides professional spectrum and stereo-analysis views, including stereo-differential FFT visualization.
- Professional audio applications commonly provide real-time meters, spectrograms, correlation views, and repair workflows.

Audio File Report should not claim that ordinary metadata, FFT graphs, or correlation meters are unique. Its intended differentiation is the integration of offline measurement, event localization, evidence, explainable QC, validation, and reproducible handoff.

This positioning is an engineering goal, not a claim that no existing product offers any overlapping feature.

## Core Differentiation Pillars

### 1. Evidence-Linked Findings

Every significant finding should connect to:

- The measured value
- The relevant channel
- The exact time range
- The relevant frequency range, when applicable
- The configured threshold or comparison rule
- A supporting graph or marker
- The calculation method

The user should be able to select a finding and move every relevant view to the same evidence.

### 2. Confidence and Limitations

The tool should separate:

- Exact facts, such as sample rate or channel count
- Deterministic detections, such as sample-for-sample duplicated channels
- Estimates, such as interchannel delay in complex program material
- Heuristic warnings, such as a possible channel swap
- Insufficient-evidence conditions

Applicable findings may use:

```text
High confidence
Moderate confidence
Low confidence
Insufficient evidence
```

Confidence must not imply formal statistical certainty unless a documented statistical method supports it.

### 3. Linked Investigation Workspace

A selected waveform region or detected event should update:

- Local level and dynamics measurements
- Spectrum and spectrogram selection
- Stereo correlation
- Mid/side balance
- Mono-cancellation evidence
- Goniometer or vectorscope data
- Event and evidence panels

This makes the visual interface an investigative system rather than a set of unrelated plots.

### 4. Explainable Quality Control

QC results should answer:

- What was measured?
- What rule applied?
- Why did it apply here?
- What threshold was crossed?
- How far did the result exceed the threshold?
- How confident is the finding?
- What might it indicate?
- What does it not prove?

Rules should support applicability conditions such as minimum signal level, minimum duration, channel, time, and frequency range.

### 5. Controlled Validation

The project should include a test-signal laboratory that plants known conditions:

- Known peak and RMS values
- Clipping and silence events
- DC offset
- Known frequencies
- Polarity inversion
- Known channel delay
- Frequency-dependent correlation
- Side-heavy low-frequency content

Each measurement should have documented expected results and numerical tolerances. A portfolio reviewer should be able to see not only that the code produced a number, but why that number is trusted.

### 6. Reproducible Handoff

A reproducible analysis package may contain:

```text
report.html
measurements.json
events.csv
spectral-data.csv
settings.json
manifest.json
analysis.log
plots/
```

It should record:

- Source-file checksum
- Program version
- Python and dependency versions
- QC profile and version
- Analysis settings
- Commands used
- Confidence and limitations
- Package checksums

Source audio should not be duplicated by default.

### 7. Honest Format and Scope Handling

The project remains focused on stereo analysis.

- Mono and multichannel input may be identified and described.
- Stereo analysis requires exactly two channels.
- Multichannel layouts should be reported only when metadata supports them.
- The program should never infer Atmos from channel count.
- The program should never silently analyze only the first two channels of a larger file.

### 8. Non-Destructive Analysis

The analyzer should not modify source audio by default. Features such as normalization should begin as previews that report predicted results. Any future file-writing function must be explicit, separately tested, and protected against accidental overwrite.

## Release-Level Differentiation

### Version 0.2.0 — Approachable Without Being Opaque

- Brief, normal, verbose, quiet, and debug behavior
- Friendly errors with optional detailed diagnostics
- Explicit graph behavior and safe output handling
- Clear distinction between sample width, bit depth, encoding, and layout

### Version 0.3.0 — Event-Based Dynamics

- Time-localized clipping, silence, dropout, level, and DC-offset events
- Windowed rather than only whole-file measurements
- Normalization previews without modifying the file
- Planted test conditions with expected results

### Version 0.4.0 — Comparable Spectral Evidence

- Shared channel normalization by default
- Spectral difference and numeric band-energy tables
- Selected-region analysis
- Averaged and peak-hold views
- Exportable spectral data with settings and units

### Version 0.5.0 — Defensible Stereo Interpretation

- Frequency-dependent correlation and width
- Mono-cancellation evidence by time and frequency
- Mid/side energy linked to selected regions
- Event timestamps and documented interpretation boundaries

### Version 0.6.0 — Cross-Encoding Measurement Parity

- One normalized internal sample representation
- Equivalent expected measurements across bit depths and encodings
- Exact non-stereo identification without unsupported inference
- Chunk-boundary testing for long-file correctness

### Version 0.7.0 — Investigation Rather Than Decoration

- One chronological event navigator
- Linked measurement and visual panels
- Select an event once and inspect it across every relevant domain
- Accessible, comparable displays with shared scales

### Version 0.8.0 — Evidence-First QC

- Rule applicability, not only thresholds
- Exact versus heuristic finding types
- Confidence and limitation indicators
- “Why was this flagged?” evidence cards
- Reviewed and overridden findings preserved rather than silently hidden

### Version 0.9.0 — Reproducible Session QC

- Folder/session consistency checks
- Resumable batches and content-aware caching
- Checksums and identity distinctions
- Privacy-safe shareable packages
- Versioned schemas for machine-readable results

### Version 1.0.0 — Auditable Trust

- Controlled test-signal laboratory
- Justified numerical tolerances
- Regression tests for every corrected defect
- Stable CLI and schemas
- Safe untrusted-input handling
- Explicit supported platforms and known limitations

## Additional Differentiator Candidates

These ideas may be assigned to releases after technical review.

### Measurement Provenance Graph

Allow a result to show its derivation:

```text
Source file
→ decoded sample representation
→ selected time range
→ analysis window and settings
→ raw measurement
→ QC rule
→ finding and evidence
```

This could make debugging and review unusually transparent.

### Analysis Bookmarks and Notes

Allow users to label regions such as verse, chorus, suspected click, or reference section, then compare those bookmarks across level, spectrum, and stereo measurements.

### Difference-First Review Mode

For two-file comparisons, show only measurements, events, and regions that materially changed. This would help review revised mixes without manually comparing every report field.

### Finding Stability Test

Re-run applicable detections with nearby window sizes or thresholds and report whether the conclusion remains stable. Findings that disappear under small parameter changes could receive lower confidence.

### Human Review State

Support statuses such as:

```text
Unreviewed
Reviewed
Accepted intentional condition
Requires revision
Resolved in later version
```

Preserve the automated finding separately from the human decision.

### Test-Case Explorer

Provide a browsable collection of controlled signals showing how every measurement and warning behaves. This would serve documentation, education, regression testing, and portfolio demonstration simultaneously.

## Claims and Language

Prefer:

- “The implemented checks passed.”
- “Possible mono cancellation detected in this region.”
- “Estimated delay based on cross-correlation.”
- “Layout reported from WAV channel-mask metadata.”

Avoid unsupported claims such as:

- “Certified for broadcast.”
- “Dolby approved.”
- “The source is physically located at this angle.”
- “This mix is objectively too wide.”
- “This graph is a system frequency response” when analyzing arbitrary program audio.

## Differentiation Review Questions

Before adding a major feature, ask:

1. Does it solve a real review or delivery problem?
2. Does it connect to evidence rather than only produce another number?
3. Can it be validated with controlled data?
4. Can its limitations be stated clearly?
5. Does it fit a stereo-file analyzer rather than another future project?
6. Does it make the workflow more explainable, reproducible, or efficient?
7. Would a simpler existing library or tool already solve the need better?
