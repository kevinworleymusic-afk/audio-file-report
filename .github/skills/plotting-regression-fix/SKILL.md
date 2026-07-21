---
name: plotting-regression-fix
description: Fix regressions in generated audio plots, including waveform and spectrum rendering differences, scaling, labels, and saved artifact consistency.
---

# Plotting Regression Fix

Use this skill when:
- A generated plot changed unexpectedly after code edits.
- Plot tests or visual checks show scale, axis, legend, or layout regressions.
- Saved artifact filenames, dimensions, or output paths are incorrect.

Do not use this skill when:
- The task is a net-new visual redesign request.
- The issue is unrelated to plotting output.

## Workflow

1. Reproduce visual difference.
- Generate the smallest plot that shows the regression.
- Compare current output against expected behavior from tests or docs.

2. Localize the break.
- Inspect plotting pipeline in src/audio_file_report/plotting.py and call sites.
- Check data inputs, normalization, axis limits, and figure size/dpi.

3. Fix for determinism first.
- Prefer stable defaults and explicit parameters.
- Avoid hidden state from global plotting configuration.

4. Keep output contracts stable.
- Preserve output file paths, names, and basic schema unless asked to change.
- Ensure compatibility with existing tests and artifacts usage.

5. Verify.
- Re-run targeted plotting tests.
- Regenerate a sample artifact and confirm expected dimensions/labels.

## Output format

- Regression symptom
- Root cause
- Files changed
- Before/after behavior
- Validation commands and results
