---
name: cli-ux-improvements
description: Improve command-line usability for the audio file report tool, including argument clarity, help text, defaults, error messaging, and output readability.
---

# CLI UX Improvements

Use this skill when:
- Users are confused by command flags or help text.
- Error messages are unclear or actionable guidance is missing.
- CLI output is hard to scan in terminal logs.

Do not use this skill when:
- The task is purely analysis correctness.
- The task is only about plot rendering internals.

## Workflow

1. Identify user-facing friction.
- Reproduce the exact command and output that feels confusing.
- Capture current help text and error behavior.

2. Map UX issue to code path.
- Focus on src/audio_file_report/cli.py, src/audio_file_report/app.py, and related messaging helpers.
- Keep behavior backward compatible unless breaking changes are requested.

3. Improve clarity with minimal surface change.
- Use explicit flag descriptions and concrete examples.
- Prefer actionable errors: what failed, why, and how to fix.

4. Preserve scriptability.
- Keep machine-readable outputs stable when possible.
- Avoid noisy output on success paths unless requested.

5. Verify.
- Run representative CLI commands for success and failure cases.
- Check --help output for readability and completeness.

## Output format

- UX issue
- Change summary
- Files changed
- Example commands (before/after)
- Validation commands and results
