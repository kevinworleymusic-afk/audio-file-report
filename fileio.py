import os
import sys
from pathlib import Path
import wave

from common import (
    EXIT_NOT_FOUND,
    EXIT_PERMISSION,
    EXIT_EMPTY,
    EXIT_NOT_FILE,
    EXIT_INVALID_WAV,
)


def validate_input_path(audio_path: Path, debug: bool = False) -> None:
    if not audio_path.exists():
        print(f"Error: input path '{audio_path}' does not exist.")
        if debug:
            print(f"DEBUG: looked for: {audio_path.resolve()}")
        sys.exit(EXIT_NOT_FOUND)

    if not audio_path.is_file():
        print(f"Error: input path '{audio_path}' is not a file.")
        if debug:
            print(f"DEBUG: path exists but is not a file: {audio_path}")
        sys.exit(EXIT_NOT_FILE)

    try:
        with open(audio_path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
    except PermissionError:
        print(f"Error: permission denied reading '{audio_path}'.")
        if debug:
            print(f"DEBUG: permission check failed for: {audio_path}")
        sys.exit(EXIT_PERMISSION)

    if size == 0:
        print(f"Error: input file '{audio_path}' is empty.")
        if debug:
            print(f"DEBUG: file size (bytes): {size}")
        sys.exit(EXIT_EMPTY)


def validate_wav_file(audio_path: Path, debug: bool = False) -> None:
    try:
        with wave.open(str(audio_path), "rb") as wf:
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            nframes = wf.getnframes()
            comptype = wf.getcomptype()
            compname = wf.getcompname()

            if debug:
                print(f"DEBUG: WAV channels={channels}, sampwidth={sampwidth}, frames={nframes}")

            if nframes == 0:
                print(f"Error: WAV file '{audio_path}' contains zero frames.")
                sys.exit(EXIT_INVALID_WAV)

            try:
                wf.rewind()
                sample = wf.readframes(1)
            except Exception as e:
                print(f"Error: could not read frames from WAV file: {e}")
                if debug:
                    import traceback; traceback.print_exc()
                sys.exit(EXIT_INVALID_WAV)

            if sampwidth not in (1, 2, 3, 4):
                print(f"Error: unsupported sample width ({sampwidth} bytes) in WAV file.")
                sys.exit(EXIT_INVALID_WAV)

            if comptype != "NONE":
                print(f"Error: unsupported WAV compression type: {comptype} ({compname})")
                sys.exit(EXIT_INVALID_WAV)

            if sampwidth == 4:
                try:
                    wf.rewind()
                    raw = wf.readframes(min(1024, nframes))
                    import numpy as _np

                    if len(raw) >= 4:
                        try:
                            f = _np.frombuffer(raw, dtype='<f4')
                            maxf = float(_np.max(_np.abs(f))) if f.size else 0.0
                        except Exception:
                            maxf = float('inf')

                        try:
                            i = _np.frombuffer(raw, dtype='<i4')
                            maxi = int(_np.max(_np.abs(i))) if i.size else 0
                        except Exception:
                            maxi = 0

                        if maxf <= 1.5:
                            if debug:
                                print("DEBUG: detected 32-bit float WAV (values in -1..1).")
                        elif maxi > 0:
                            if debug:
                                print("DEBUG: detected 32-bit integer WAV.")
                        else:
                            if debug:
                                print("DEBUG: could not determine 32-bit WAV subtype; assuming integer.")
                except Exception:
                    if debug:
                        import traceback; traceback.print_exc()

    except wave.Error as e:
        print(f"Error: invalid WAV file or corrupted header: {e}")
        if debug:
            import traceback; traceback.print_exc()
        sys.exit(EXIT_INVALID_WAV)
    except EOFError:
        print("Error: unexpected end of file while reading WAV header.")
        sys.exit(EXIT_INVALID_WAV)
    except Exception as e:
        print(f"Error: cannot read WAV file: {e}")
        if debug:
            import traceback; traceback.print_exc()
        sys.exit(EXIT_INVALID_WAV)


def read_wav_file(audio_path: Path):
    with wave.open(str(audio_path), "rb") as audio_file:
        channels = audio_file.getnchannels()
        sample_rate = audio_file.getframerate()
        sample_width = audio_file.getsampwidth()
        frame_count = audio_file.getnframes()
        audio_data = audio_file.readframes(frame_count)

    return channels, sample_rate, sample_width, frame_count, audio_data
