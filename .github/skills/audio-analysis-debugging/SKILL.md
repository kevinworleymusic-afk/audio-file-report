---
name: audio-analysis-debugging
description: Diagnose incorrect or surprising audio analysis results, including duration, channels, sample rate, peak/rms metrics, and spectrum outputs.
---

# Audio Analysis Debugging

Use this skill when:
- A metric in analysis output looks wrong or unstable.
- A test fails in analysis-related code.
- A user reports unexpected values in generated reports.

Do not use this skill when:
- The request is primarily about visualization styling.
- The request is about CLI argument wording only.

## Workflow

1. Reproduce the issue quickly.
- Run the narrowest command or test that shows the bug.
- Prefer a single failing test over a full suite first.

2. Trace data flow.
- Identify where values are read, transformed, and reported.
- Focus on likely paths in src/audio_file_report/fileio.py and src/audio_file_report/analysis.py.

3. Validate assumptions with small checks.
- Confirm units (seconds vs samples), channel layout, dtype/range normalization, and windowing assumptions.
- Add temporary assertions or focused diagnostics only if needed.

4. Apply the smallest safe fix.
- Avoid broad refactors unless required for correctness.
- Preserve public behavior except for the bug fix.

5. Verify.
- Re-run targeted tests, then broader diagnostics if available.
- Confirm no obvious regression in related metrics.

## Output format

- Root cause
- Files changed
- Why this fix is correct
- Validation commands and results
- Remaining risks
