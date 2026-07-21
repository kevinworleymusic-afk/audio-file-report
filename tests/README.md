Running diagnostics tests

Prerequisites

- Python 3.9+ (the repo was tested with 3.14)
- NumPy and Matplotlib are optional for some tests; most diagnostic tests exercise validation logic only.

Run all test modules (all versions)

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

Run tests by version

```bash
# Version 0.2.x diagnostics and CLI/plotting regressions
python3 -m unittest \
	tests/test_diagnostics.py \
	tests/test_cli_plotting_regressions.py \
	tests/test_cli_argument_matrix.py \
	tests/test_error_code_regressions.py -v

# Version 0.3.x level and dynamics regressions
python3 -m unittest \
	tests/test_v030_fundamental_amplitude_script.py \
	tests/test_v030_rms_crest_factor_script.py \
	tests/test_v030_level_metrics.py \
	tests/test_v030_regression_validation_track.py -v
```

Run the test module

From the repository root:

```bash
python3 -m unittest tests/test_diagnostics.py -v
```

Run regression tests for CLI/plotting fixes:

```bash
python3 -m unittest tests/test_cli_plotting_regressions.py -v
```

Run CLI argument matrix regressions:

```bash
python3 -m unittest tests/test_cli_argument_matrix.py -v
```

Run error-code regression matrix:

```bash
python3 -m unittest tests/test_error_code_regressions.py -v
```

Run 0.3.0 level-metric unit tests:

```bash
python3 -m unittest tests/test_v030_level_metrics.py -v
```

Run 0.3.0 fundamental amplitude script tests:

```bash
python3 -m unittest tests/test_v030_fundamental_amplitude_script.py -v
```

Run 0.3.0 RMS/Crest script tests:

```bash
python3 -m unittest tests/test_v030_rms_crest_factor_script.py -v
```

Run 0.3.0 regression/validation track tests:

```bash
python3 -m unittest tests/test_v030_regression_validation_track.py -v
```

Or run the test module directly:

```bash
python3 tests/test_diagnostics.py -v
```

Notes

- `test_logfile_startup_header` expects `assets/audio/test_audio.wav` to exist; the test will be skipped if not present.
- The tests create temporary files and will clean up after themselves. A test that modifies file permissions restores them before exit.
- If you want to run an individual test, use `-k`/`-m` with your test runner or run the specific method by invoking the module directly and filtering with `unittest` options.
