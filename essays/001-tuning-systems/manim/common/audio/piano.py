"""A piano sampler that plays any frequency exactly.

Recorded pianos are stretch-tuned and never sit exactly on paper
frequencies, which matters in an essay about tuning. Each bundled sample
comes with its measured fundamental (``manifest.tsv``, produced by
``tools/import_piano_samples.py``), and ``Piano.note`` resamples the
nearest sample from that measured pitch to the requested one. Asking for
220 Hz and 330 Hz therefore gives an exact 3:2 fifth.
"""

import csv
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import numpy as np
import soundfile
from scipy.signal import resample_poly

from ..paths import ASSETS_DIR
from .sound import SAMPLE_RATE, Sound

PIANO_DIR = ASSETS_DIR / "samples" / "piano"


class Piano:
    """Sampled grand piano (Salamander Grand Piano V3, one layer)."""

    def __init__(self, directory: Path = PIANO_DIR):
        self.directory = directory
        with (directory / "manifest.tsv").open(encoding="utf-8") as handle:
            rows = csv.DictReader(
                (line for line in handle if not line.startswith("#")),
                delimiter="\t")
            self.samples = [
                (row["file"], float(row["root_hz"])) for row in rows]

    def nearest(self, frequency: float) -> tuple[str, float]:
        """The sample whose measured pitch is closest to ``frequency``."""
        return min(self.samples,
                   key=lambda item: abs(math.log(frequency / item[1])))

    def note(
        self,
        frequency: float,
        duration: float | None = None,
        release: float = 0.6,
    ) -> Sound:
        """A piano note whose fundamental is exactly ``frequency`` Hz.

        With ``duration`` the key is released after that many seconds and
        the sound fades over ``release``; without it, the note rings for
        the whole sample.
        """
        name, root = self.nearest(frequency)
        samples = _resampled(self.directory / name, root / frequency)
        sound = Sound(samples, SAMPLE_RATE)
        if duration is not None:
            sound = sound.trimmed(duration, release)
        return sound


@lru_cache(maxsize=64)
def _resampled(path: Path, stretch: float) -> np.ndarray:
    """Load ``path`` at the project rate, ``stretch`` times as long.

    Playing a recording more slowly lowers its pitch by the same factor,
    so a stretch of ``root / target`` moves the pitch onto ``target``.
    The ratio is approximated to well under 0.001 cent.
    """
    data, rate = soundfile.read(path, dtype="float32", always_2d=True)
    if data.shape[1] == 1:
        data = np.repeat(data, 2, axis=1)
    ratio = Fraction(stretch * SAMPLE_RATE / rate).limit_denominator(4000)
    if ratio == 1:
        return data
    out = resample_poly(data, ratio.numerator, ratio.denominator, axis=0)
    return out.astype(np.float32)
