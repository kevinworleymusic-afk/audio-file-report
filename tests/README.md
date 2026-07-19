Running diagnostics tests

Prerequisites

- Python 3.8+ (the repo was tested with 3.14)
- NumPy and Matplotlib are optional for some tests; most diagnostic tests exercise validation logic only.

Run the test module

From the repository root:

```bash
python3 -m unittest tests/test_diagnostics.py -v
```

Or run the test module directly:

```bash
python3 tests/test_diagnostics.py -v
```

Notes

- `test_logfile_startup_header` expects `test_audio.wav` to exist at the repository root; the test will be skipped if not present.
- The tests create temporary files and will clean up after themselves. A test that modifies file permissions restores them before exit.
- If you want to run an individual test, use `-k`/`-m` with your test runner or run the specific method by invoking the module directly and filtering with `unittest` options.
