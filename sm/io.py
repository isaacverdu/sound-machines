"""Audio file I/O."""

import io as _io
from pathlib import Path

import numpy as np
import soundfile as sf


def _normalized(y, normalize=True):
    """Peak the signal at -1 dBFS, which avoids clipping surprises."""
    y = np.asarray(y, dtype=np.float64)
    if normalize and np.max(np.abs(y)) > 0:
        y = y / np.max(np.abs(y)) * 10 ** (-1 / 20)
    return y


def wav_bytes(y, fs=44_100, normalize=True):
    """Encode a 1-D float signal as 16-bit WAV bytes.

    The same encoding write_wav puts on disk, handed back in memory instead.
    That is what the browser build needs: under Pyodide there is no filesystem
    worth writing to, and an <audio> element wants the bytes directly.
    """
    buf = _io.BytesIO()
    sf.write(buf, _normalized(y, normalize), fs, format="WAV", subtype="PCM_16")
    return buf.getvalue()


def write_wav(path, y, fs=44_100, normalize=True):
    """Write a 1-D float signal to a 16-bit WAV file.

    Creates parent directories if needed. Returns the path written.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(wav_bytes(y, fs, normalize))
    return path


def read_wav(path):
    """Read a WAV file. Returns (signal, sample_rate); stereo is averaged to mono."""
    y, fs = sf.read(path, dtype="float64")
    if y.ndim > 1:
        y = y.mean(axis=1)
    return y, fs
