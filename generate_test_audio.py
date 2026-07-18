"""Generate a stereo WAV file for the Audio File Technical Report project."""

import math
import struct
import wave
from pathlib import Path


OUTPUT_FILE = Path("test_audio.wav")
SAMPLE_RATE = 48000
DURATION_SECONDS = 5
AMPLITUDE = 0.5
LEFT_FREQUENCY = 440.0
RIGHT_FREQUENCY = 660.0
FADE_SECONDS = 0.25


def fade_gain(time_seconds: float) -> float:
    """Return a gain from 0.0 to 1.0 for smooth start and end fades."""
    time_remaining = DURATION_SECONDS - time_seconds
    return min(1.0, time_seconds / FADE_SECONDS, time_remaining / FADE_SECONDS)


def generate_test_audio(output_path: Path = OUTPUT_FILE) -> None:
    """Write a 16-bit stereo WAV containing separate left and right tones."""
    frame_count = SAMPLE_RATE * DURATION_SECONDS
    maximum_sample = 32767

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)

        for frame_number in range(frame_count):
            time_seconds = frame_number / SAMPLE_RATE
            gain = AMPLITUDE * fade_gain(time_seconds)

            left_sample = int(
                maximum_sample * gain * math.sin(2 * math.pi * LEFT_FREQUENCY * time_seconds)
            )
            right_sample = int(
                maximum_sample * gain * math.sin(2 * math.pi * RIGHT_FREQUENCY * time_seconds)
            )

            wav_file.writeframesraw(struct.pack("<hh", left_sample, right_sample))


if __name__ == "__main__":
    generate_test_audio()
    print(f"Created {OUTPUT_FILE}")
