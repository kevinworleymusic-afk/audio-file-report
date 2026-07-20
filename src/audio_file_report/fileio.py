import os
import sys
import logging
from pathlib import Path
import wave

from .common import (
    EXIT_NOT_FOUND,
    EXIT_PERMISSION,
    EXIT_EMPTY,
    EXIT_NOT_FILE,
    EXIT_INVALID_WAV,
)

logger = logging.getLogger(__name__)


def validate_input_path(audio_path: Path, debug: bool = False) -> None:
    if not audio_path.exists():
        logger.debug("Input path missing: %s", audio_path)
        print(f"Error: input path '{audio_path}' does not exist.", file=sys.stderr)
        print("Suggestion: check the path and filename (quote spaces) or run: ls -l", file=sys.stderr)
        sys.exit(EXIT_NOT_FOUND)

    if not audio_path.is_file():
        logger.debug("Input path is not a file: %s", audio_path)
        print(f"Error: input path '{audio_path}' is not a file.", file=sys.stderr)
        print("Suggestion: provide a file path (not a directory). Use an explicit filename.", file=sys.stderr)
        sys.exit(EXIT_NOT_FILE)

    try:
        with open(audio_path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
    except PermissionError:
        logger.debug("Permission denied reading: %s", audio_path, exc_info=True)
        print(f"Error: permission denied reading '{audio_path}'.", file=sys.stderr)
        print("Suggestion: check file permissions (ls -l) and grant read access, e.g. chmod u+r <file>.", file=sys.stderr)
        sys.exit(EXIT_PERMISSION)

    if size == 0:
        logger.debug("Input file is empty: %s (size=0)", audio_path)
        print(f"Error: input file '{audio_path}' is empty.", file=sys.stderr)
        print("Suggestion: regenerate the file or ensure the correct source path was used.", file=sys.stderr)
        sys.exit(EXIT_EMPTY)


def validate_wav_file(audio_path: Path, debug: bool = False) -> None:
    try:
        with wave.open(str(audio_path), "rb") as wf:
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            nframes = wf.getnframes()
            comptype = wf.getcomptype()
            compname = wf.getcompname()

            logger.debug("WAV header: channels=%s sampwidth=%s frames=%s", channels, sampwidth, nframes)

            if nframes == 0:
                print(f"Error: WAV file '{audio_path}' contains zero frames.", file=sys.stderr)
                logger.debug("Zero frames in WAV: %s", audio_path)
                sys.exit(EXIT_INVALID_WAV)

            # try reading a small amount of data to ensure frames are readable
            try:
                wf.rewind()
                _ = wf.readframes(1)
            except Exception:
                logger.debug("Could not read WAV frames: %s", audio_path, exc_info=True)
                print("Error: could not read frames from WAV file.", file=sys.stderr)
                sys.exit(EXIT_INVALID_WAV)

            # basic sanity check for sample width
            if sampwidth not in (1, 2, 3, 4):
                logger.debug("Unsupported sampwidth: %s", sampwidth)
                print(f"Error: unsupported sample width ({sampwidth} bytes) in WAV file.", file=sys.stderr)
                sys.exit(EXIT_INVALID_WAV)

            # Check compression type (expect PCM/uncompressed)
            if comptype != "NONE":
                logger.debug("Unsupported compression type: %s (%s)", comptype, compname)
                print(f"Error: unsupported WAV compression type: {comptype} ({compname})", file=sys.stderr)
                sys.exit(EXIT_INVALID_WAV)

            # Additional check for 32-bit files: distinguish float vs int
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
                            logger.debug("Detected 32-bit float WAV (values in -1..1).")
                        elif maxi > 0:
                            logger.debug("Detected 32-bit integer WAV.")
                        else:
                            logger.debug("Could not determine 32-bit WAV subtype; assuming integer.")
                except Exception:
                    logger.debug("Error while inspecting 32-bit WAV subtype: %s", audio_path, exc_info=True)
    except wave.Error as e:
        logger.debug("Invalid WAV file or corrupted header: %s", e, exc_info=True)
        print(f"Error: invalid WAV file or corrupted header: {e}", file=sys.stderr)
        print("Suggestion: verify the file is a valid PCM WAV (try 'ffmpeg -v error -i <file>').", file=sys.stderr)
        sys.exit(EXIT_INVALID_WAV)
    except EOFError:
        logger.debug("Unexpected EOF while reading WAV header: %s", audio_path, exc_info=True)
        print("Error: unexpected end of file while reading WAV header.", file=sys.stderr)
        print("Suggestion: the file appears truncated — re-copy or re-export the source.", file=sys.stderr)
        sys.exit(EXIT_INVALID_WAV)
    except Exception as e:
        logger.debug("Cannot read WAV file: %s", e, exc_info=True)
        print(f"Error: cannot read WAV file: {e}", file=sys.stderr)
        print("Suggestion: inspect the file with a media tool (ffmpeg/sox) or run with --debug for details.", file=sys.stderr)
        sys.exit(EXIT_INVALID_WAV)


def read_wav_file(audio_path: Path):
    with wave.open(str(audio_path), "rb") as audio_file:
        channels = audio_file.getnchannels()
        sample_rate = audio_file.getframerate()
        sample_width = audio_file.getsampwidth()
        frame_count = audio_file.getnframes()
        comptype = audio_file.getcomptype()
        compname = audio_file.getcompname()
        audio_data = audio_file.readframes(frame_count)

    return channels, sample_rate, sample_width, frame_count, audio_data, comptype, compname
