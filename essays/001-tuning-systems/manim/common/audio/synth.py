"""Synthesized sounds."""

import numpy as np

from .sound import SAMPLE_RATE, Sound


def tone(
    frequency: float,
    duration: float,
    attack: float = 0.05,
    release: float = 0.5,
    rate: int = SAMPLE_RATE,
) -> Sound:
    """A pure sine tone at exactly ``frequency`` Hz.

    ``duration`` excludes the ``release`` fade, so the tone lasts
    ``duration + release`` seconds. Attack and release are raised-cosine
    ramps, which avoid clicks.
    """
    total = int((duration + release) * rate)
    t = np.arange(total) / rate
    wave = np.sin(2 * np.pi * frequency * t)
    envelope = np.ones(total)
    rise = max(1, int(attack * rate))
    fall = max(1, int(release * rate))
    envelope[:rise] = np.sin(np.linspace(0, np.pi / 2, rise)) ** 2
    envelope[-fall:] *= np.cos(np.linspace(0, np.pi / 2, fall)) ** 2
    return Sound.from_mono((wave * envelope).astype(np.float32), rate)
