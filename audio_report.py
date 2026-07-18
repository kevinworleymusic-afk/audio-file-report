import wave
from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt

# audio_path = Path("test_audio.wav")

if len(sys.argv) < 2:
    print("Usage: python3 audio_report.py <audio-file.wav>")
    sys.exit(1)

audio_path = Path(sys.argv[1])

with wave.open(str(audio_path), "rb") as audio_file:
    channels = audio_file.getnchannels()
    sample_rate = audio_file.getframerate()
    sample_width = audio_file.getsampwidth()
    frame_count = audio_file.getnframes()
    audio_data = audio_file.readframes(frame_count)

bit_depth = sample_width * 8
duration = frame_count / sample_rate

print("AUDIO FILE REPORT")
print("-----------------")
print(f"File: {audio_path.name}")
print(f"Channels: {channels}")
print(f"Sample rate: {sample_rate} Hz")
print(f"Bit depth: {bit_depth}-bit")
print(f"Frames: {frame_count}")
print(f"Duration: {duration:.2f} seconds")

if sample_width != 2:
    print("Spectrum analysis currently only supports 16-bit audio files.")
    sys.exit(1) 
    
if channels < 2:
    print("A stereo WAv file is required for left/right comparison.")
    sys.exit(1)

samples = np.frombuffer(audio_data, dtype="<i2")
samples = samples.reshape(-1, channels)

left_channel = samples[:, 0].astype(float)
right_channel = samples[:, 1].astype(float)

window = np.hanning(frame_count)

left_fft = np.fft.rfft(left_channel * window)
right_fft = np.fft.rfft(right_channel * window)

frequencies = np.fft.rfftfreq(
    frame_count,
    d=1.0 / sample_rate,
)

left_magnitude = np.abs(left_fft)
right_magnitude = np.abs(right_fft)

reference = max(
    np.max(left_magnitude), 
    np.max(right_magnitude)
)

left_db = 20 * np.log10(
    np.maximum(left_magnitude / reference, 1e-12)
)

right_db = 20 * np.log10(
    np.maximum(right_magnitude / reference, 1e-12)
)

frequency_range = (
    (frequencies >= 20) 
    & (frequencies <= 20000)
)

plt.figure(figsize=(10, 6))

plt.semilogx(
    frequencies[frequency_range],
    left_db[frequency_range],
    label="Left Channel",
)

plt.semilogx(
    frequencies[frequency_range],
    right_db[frequency_range],
    label="Right Channel",
)
plt.title("Left and Right Channel Frequency Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Relative magnitude (dB)")
plt.xlim(20, 20000)
plt.ylim(-120, 5)
frequency_ticks = [
    20,
    50,
    100,
    200,
    500,
    1_000,
    2_000,
    5_000,
    10_000,
    20_000,
]

frequency_labels = [
    "20",
    "50",
    "100",
    "200",
    "500",
    "1k",
    "2k",
    "5k",
    "10k",
    "20k",
]

plt.xticks(frequency_ticks, frequency_labels)

plt.grid(which="both", linestyle="--", alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()
