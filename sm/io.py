"""Audio file I/O."""

from pathlib import Path

import numpy as np
import soundfile as sf


def write_wav(path, y, fs=44_100, normalize=True):
    """Write a 1-D float signal to a 16-bit WAV file.

    Creates parent directories if needed. If ``normalize`` is True the signal
    is scaled so its peak sits at -1 dBFS, which avoids clipping surprises.
    Returns the path written.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    y = np.asarray(y, dtype=np.float64)
    if normalize and np.max(np.abs(y)) > 0:
        y = y / np.max(np.abs(y)) * 10 ** (-1 / 20)
    sf.write(path, y, fs, subtype="PCM_16")
    return path


def read_wav(path):
    """Read a WAV file. Returns (signal, sample_rate); stereo is averaged to mono."""
    y, fs = sf.read(path, dtype="float64")
    if y.ndim > 1:
        y = y.mean(axis=1)
    return y, fs
