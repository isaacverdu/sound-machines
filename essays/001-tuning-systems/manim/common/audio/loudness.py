"""Perceived loudness (ITU-R BS.1770 K-weighting), in LUFS.

Plain RMS overrates low notes and underrates bright ones; K-weighting
approximates how loud a sound actually seems, so a 27.5 Hz piano note,
a 4 kHz piano note and a voice can be balanced with a single number.
"""

from pathlib import Path

import av
import numpy as np
from scipy.signal import lfilter

from .sound import SAMPLE_RATE

# BS.1770 filters at 48 kHz: a high shelf (head effect) and a high-pass.
_SHELF = ([1.53512485958697, -2.69169618940638, 1.19839281085285],
          [1.0, -1.69065929318241, 0.73248077421585])
_HIGHPASS = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])
_BLOCK, _HOP = 0.4, 0.1  # momentary loudness window and step, seconds


def _block_loudness(samples: np.ndarray) -> np.ndarray:
    """Loudness of each 400 ms block (75 % overlap) of 48 kHz audio."""
    channels = samples.reshape(len(samples), -1).astype(np.float64)
    weighted = lfilter(*_HIGHPASS, lfilter(*_SHELF, channels, axis=0),
                       axis=0)
    size, hop = int(_BLOCK * SAMPLE_RATE), int(_HOP * SAMPLE_RATE)
    if len(weighted) < size:
        weighted = np.pad(weighted, ((0, size - len(weighted)), (0, 0)))
    starts = range(0, len(weighted) - size + 1, hop)
    power = np.array([(weighted[s:s + size] ** 2).mean(axis=0).sum()
                      for s in starts])
    return -0.691 + 10 * np.log10(np.maximum(power, 1e-12))


def max_momentary(samples: np.ndarray) -> float:
    """Loudest 400 ms of a short sound, in LUFS (48 kHz input)."""
    return float(_block_loudness(samples).max())


def integrated(samples: np.ndarray) -> float:
    """Gated integrated loudness of a programme, in LUFS (48 kHz input).

    Silence and quiet passages are gated out as in BS.1770, so a
    voice-over's pauses do not lower its measured loudness.
    """
    blocks = _block_loudness(samples)
    blocks = blocks[blocks > -70]
    if not len(blocks):
        return -70.0
    mean_power = np.mean(10 ** ((blocks + 0.691) / 10))
    relative_gate = -0.691 + 10 * np.log10(mean_power) - 10
    kept = blocks[blocks > relative_gate]
    return float(-0.691 + 10 * np.log10(
        np.mean(10 ** ((kept + 0.691) / 10))))


def file_loudness(path: Path) -> float:
    """Integrated loudness of an audio file of any format, in LUFS.

    The file is measured as stereo, the way it plays in the final mix
    (a mono voice-over is heard on both channels).
    """
    resampler = av.AudioResampler(format="flt", layout="stereo",
                                  rate=SAMPLE_RATE)
    chunks = []
    with av.open(str(path)) as container:
        for frame in container.decode(audio=0):
            chunks += [f.to_ndarray().reshape(-1, 2) for f in
                       resampler.resample(frame)]
        chunks += [f.to_ndarray().reshape(-1, 2)
                   for f in resampler.resample(None)]
    return integrated(np.concatenate(chunks))
