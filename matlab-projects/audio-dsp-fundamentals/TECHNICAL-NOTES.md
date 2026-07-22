# Technical Notes

## Pink-noise synthesis

The original `prob2.m` script:

- Generates five seconds of Gaussian white noise at 48 kHz.
- Builds octave-spaced normalized frequency and amplitude arrays.
- Uses `fir2` to design an FIR shaping filter.
- Convolves the white noise with the filter.
- Plots a log-frequency magnitude response.
- Writes the result to `pinkNoise.wav`.

The exported file is a valid five-second, 48 kHz, 16-bit mono WAV. Its measured peak is approximately -55.8 dBFS, indicating that the original gain design produced an unusually low output level despite the final multiplication by two.

A revised implementation should use a target magnitude proportional to `1/sqrt(f)` for an approximately -3 dB-per-octave amplitude slope, normalize safely after filtering, and plot the designed filter or output power spectral density directly.

## Band-pass filter

`bandPass.m` creates:

1. A low-pass FIR filter at the upper cutoff.
2. A high-pass FIR filter at the lower cutoff.
3. A cascade of the two filters through sequential convolution.

This implements the assignment’s required serial filter structure.

## Band-stop filter

`bandStop.m` creates:

1. A low-pass FIR filter at the lower cutoff.
2. A high-pass FIR filter at the upper cutoff.
3. Parallel filtered paths that are summed at the output.

This implements the assignment’s required parallel filter structure.

## Testing

`problem2.m` generates an impulse, processes it through both reusable functions, and passes the resulting impulse responses to `freqz`.

`bandTest.m` applies the functions to an external acoustic-guitar file. That source file was not included with the surviving materials, so the script is preserved but is not presently reproducible without a replacement input.

## Discrete-time system

The assignment defines:

`y[n] = 0.45x[n] - 0.5x[n-1] + 0.05x[n-2]`

The corresponding transfer function is:

`H(z) = 0.45 - 0.5z^-1 + 0.05z^-2`

The written solution identifies the system’s high-pass behavior and preserves its block diagram and zero analysis. The surviving `problem3HW.m` script is incomplete and contains undefined or unfinished operations, so it is retained as developmental evidence rather than presented as executable final code.

## Recommended next iteration

- Separate filter design from signal processing.
- Accept cutoff frequencies in hertz and normalize them inside each function.
- Validate `0 < lowFreq < highFreq < Fs/2`.
- Use `filter` or `fftfilt` where appropriate instead of full-length convolution.
- Add automated impulse-response tests.
- Plot the filter coefficients’ response rather than treating arbitrary program audio as a filter.
- Correct and complete the difference-equation implementation.
- Add reproducible audio fixtures or generate test signals within each test.
