"""Import piano samples for ``common.audio.Piano``.

Usage (from the project root)::

    python tools/import_piano_samples.py              # download from GitHub
    python tools/import_piano_samples.py --source ~/SalamanderGrandPiano

Takes one velocity layer of the Salamander Grand Piano V3 (Yamaha C5,
recorded by Alexander Holm, CC BY 3.0: credit it wherever the audio is
published). Every note is trimmed, saved as 16-bit FLAC in
``assets/samples/piano`` and measured: the manifest stores each sample's
actual fundamental, so the sampler can retune to exact frequencies.
"""

import argparse
import csv
import io
import re
import shutil
import sys
import urllib.request
from pathlib import Path

import numpy as np
import soundfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.audio.piano import PIANO_DIR  # noqa: E402

REPOSITORY = ("https://raw.githubusercontent.com/sfzinstruments/"
              "SalamanderGrandPiano/master")
# Sampled every minor third from A0 to C8.
NOTES = [f"{name}{octave}" for octave in range(0, 9)
         for name in ("C", "D#", "F#", "A")]
NOTES = NOTES[NOTES.index("A0"):NOTES.index("C8") + 1]
PITCH_CLASSES = {"C": 0, "D#": 3, "F#": 6, "A": 9}


def midi_number(note: str) -> int:
    name, octave = re.fullmatch(r"([A-G]#?)(\d)", note).groups()
    return 12 * (int(octave) + 1) + PITCH_CLASSES[name]


def equal_tempered(midi: int) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def load(note: str, layer: int, source: Path | None):
    """Read one sample from a local copy or straight from GitHub."""
    name = f"{note}v{layer}.flac"
    if source is not None:
        return soundfile.read(source / "Samples" / name, dtype="float32")
    url = f"{REPOSITORY}/Samples/{name.replace('#', '%23')}"
    with urllib.request.urlopen(url, timeout=60) as response:
        return soundfile.read(io.BytesIO(response.read()), dtype="float32")


def measure_fundamental(data: np.ndarray, rate: int, nominal: float) -> float:
    """Frequency of the first partial (the fundamental), in Hz.

    Looks for the strongest spectral peak within 150 cents of the
    equal-tempered pitch (the top notes of this piano are stretched by up
    to a semitone), with sub-bin (parabolic) interpolation. A struck
    string glides slightly flat as it decays, so the window covers the
    first two seconds, the part a short note actually plays.
    """
    mono = data.mean(axis=1) if data.ndim == 2 else data
    start, stop = int(0.1 * rate), int(min(len(mono) / rate, 2.1) * rate)
    segment = mono[start:stop] * np.hanning(stop - start)
    size = 1 << 22
    spectrum = np.abs(np.fft.rfft(segment, size))
    step = rate / size
    low, high = nominal * 2 ** (-150 / 1200), nominal * 2 ** (150 / 1200)
    lo, hi = int(low / step), int(high / step) + 1
    k = lo + int(np.argmax(spectrum[lo:hi]))
    y0, y1, y2 = np.log(spectrum[k - 1:k + 2] + 1e-12)
    return (k + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)) * step


def trimmed(data: np.ndarray, rate: int, keep: float, fade: float):
    end = min(len(data), int((keep + fade) * rate))
    out = data[:end].copy()
    tail = max(0, end - int(keep * rate))
    if tail:
        curve = np.cos(np.linspace(0, np.pi / 2, tail)) ** 2
        out[-tail:] *= curve[:, None] if out.ndim == 2 else curve
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--source", type=Path,
                        help="local SalamanderGrandPiano checkout")
    parser.add_argument("--layer", type=int, default=10,
                        help="velocity layer 1-16 (default 10, mezzo-forte)")
    parser.add_argument("--keep", type=float, default=6.5,
                        help="seconds kept before the fade (default 6.5)")
    parser.add_argument("--fade", type=float, default=1.5,
                        help="fade-out length in seconds (default 1.5)")
    args = parser.parse_args()

    PIANO_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for note in NOTES:
        data, rate = load(note, args.layer, args.source)
        midi = midi_number(note)
        nominal = equal_tempered(midi)
        root = measure_fundamental(data, rate, nominal)
        file = f"{note.replace('#', 's')}.flac"
        soundfile.write(PIANO_DIR / file,
                        trimmed(data, rate, args.keep, args.fade), rate,
                        subtype="PCM_16")
        cents = 1200 * np.log2(root / nominal)
        rows.append([note, midi, file, f"{root:.4f}", f"{cents:+.1f}"])
        print(f"{note:4s} {root:10.3f} Hz  {cents:+6.1f} cents from ET")

    with (PIANO_DIR / "manifest.tsv").open("w", newline="") as handle:
        handle.write(f"# Salamander Grand Piano V3, velocity layer "
                     f"{args.layer}; root_hz is the measured fundamental\n")
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["note", "midi", "file", "root_hz", "cents_from_et"])
        writer.writerows(rows)
    licence = PIANO_DIR / "LICENSE.txt"
    if args.source is not None:
        shutil.copyfile(args.source / "LICENSE", licence)
    else:
        with urllib.request.urlopen(f"{REPOSITORY}/LICENSE",
                                    timeout=60) as response:
            licence.write_bytes(response.read())
    print(f"Wrote {len(rows)} samples and manifest.tsv to {PIANO_DIR}")


if __name__ == "__main__":
    main()
