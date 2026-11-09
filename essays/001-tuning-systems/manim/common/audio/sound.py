"""A minimal stereo audio buffer with the operations scenes need."""

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile

SAMPLE_RATE = 48_000


@dataclass(frozen=True)
class Sound:
    """Stereo samples (``frames x 2``, float32 in -1..1) at ``rate`` Hz.

    Operations return new sounds, so a sound can be reused safely.
    """

    samples: np.ndarray
    rate: int = SAMPLE_RATE

    @classmethod
    def from_mono(cls, mono: np.ndarray, rate: int = SAMPLE_RATE) -> "Sound":
        mono = np.asarray(mono, dtype=np.float32)
        return cls(np.column_stack([mono, mono]), rate)

    @property
    def duration(self) -> float:
        return len(self.samples) / self.rate

    def gain(self, db: float) -> "Sound":
        """Louder (positive) or quieter (negative) by ``db`` decibels."""
        return Sound(self.samples * np.float32(10 ** (db / 20)), self.rate)

    def loudness(self) -> float:
        """Loudest 400 ms of the sound, in LUFS (perceived loudness)."""
        from .loudness import max_momentary
        return max_momentary(self.samples)

    def at_loudness(self, lufs: float) -> "Sound":
        """Scale so the loudest 400 ms measure ``lufs``."""
        return self.gain(lufs - self.loudness())

    def trimmed(self, duration: float, release: float) -> "Sound":
        """Keep ``duration`` seconds, then fade out over ``release``."""
        keep = int(duration * self.rate)
        fade = int(release * self.rate)
        body = self.samples[: keep + fade].copy()
        tail = body[keep:]
        curve = np.cos(np.linspace(0, np.pi / 2, len(tail))) ** 2
        body[keep:] = tail * curve[:, None].astype(np.float32)
        return Sound(body, self.rate)

    def mix(self, other: "Sound", offset: float = 0.0) -> "Sound":
        """Overlay ``other`` starting ``offset`` seconds into this sound."""
        if other.rate != self.rate:
            raise ValueError("Cannot mix sounds with different rates.")
        start = int(offset * self.rate)
        length = max(len(self.samples), start + len(other.samples))
        out = np.zeros((length, 2), dtype=np.float32)
        out[: len(self.samples)] += self.samples
        out[start:start + len(other.samples)] += other.samples
        return Sound(out, self.rate)

    def fingerprint(self) -> str:
        """Short content hash, used to cache rendered files."""
        digest = hashlib.sha1(self.samples.tobytes())
        digest.update(str(self.rate).encode())
        return digest.hexdigest()[:16]

    def write(self, path: Path) -> Path:
        """Write a 16-bit WAV file and return its path."""
        path.parent.mkdir(parents=True, exist_ok=True)
        peak = float(np.abs(self.samples).max(initial=0.0))
        if peak > 1.0:
            raise ValueError(
                f"Sound clips ({20 * np.log10(peak):+.1f} dBFS); lower its "
                "level before writing it.")
        soundfile.write(path, self.samples, self.rate, subtype="PCM_16")
        return path
