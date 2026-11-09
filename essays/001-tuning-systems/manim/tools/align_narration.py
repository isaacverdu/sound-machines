"""Align a narration script to its audio and write word timings.

Usage (from the project root)::

    python tools/align_narration.py 01-introduction

Reads ``assets/narration/<stem>.<audio>`` and ``<stem>.txt`` and writes
``<stem>.words.tsv``, which scenes load through ``common.Narration``.
Re-run it whenever the voice-over is re-recorded or the script changes.

The script must be written as spoken: "twenty thousand", not "20,000".
Alignment uses PocketSphinx (``pip install pocketsphinx``), which ships
with an English model and works offline.
"""

import argparse
import re
import sys
from pathlib import Path

import av
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from common.narration import (  # noqa: E402
    AUDIO_SUFFIXES,
    Word,
    normalize,
    write_words,
)
from common.paths import NARRATION_DIR  # noqa: E402

SAMPLE_RATE = 16_000
FRAMES_PER_SECOND = 100  # PocketSphinx frame rate
FILLER_TOKENS = {"<s>", "</s>", "<sil>", "(NULL)", "[NOISE]"}


def load_pcm(path: Path) -> bytes:
    """Decode ``path`` to 16 kHz mono signed 16-bit PCM."""
    resampler = av.AudioResampler(format="s16", layout="mono",
                                  rate=SAMPLE_RATE)
    chunks = []
    with av.open(str(path)) as container:
        for frame in container.decode(audio=0):
            for resampled in resampler.resample(frame):
                chunks.append(resampled.to_ndarray().ravel())
        for resampled in resampler.resample(None):
            chunks.append(resampled.to_ndarray().ravel())
    return np.concatenate(chunks).astype(np.int16).tobytes()


def script_words(text: str) -> list[str]:
    """Split a spoken-form script into normalized words."""
    tokens = re.split(r"[\s—–-]+", text)
    return [word for word in (normalize(token) for token in tokens) if word]


def align(pcm: bytes, words: list[str]) -> list[Word]:
    """Force-align ``words`` to ``pcm`` and return their timings."""
    from pocketsphinx import Decoder

    decoder = Decoder(samprate=SAMPLE_RATE, bestpath=False, loglevel="FATAL")
    decoder.set_align_text(" ".join(words))
    decoder.start_utt()
    decoder.process_raw(pcm, full_utt=True)
    decoder.end_utt()
    if decoder.hyp() is None:
        raise RuntimeError("Alignment failed; check the script matches.")
    aligned = []
    for segment in decoder.seg():
        if segment.word in FILLER_TOKENS:
            continue
        text = re.sub(r"\(\d+\)$", "", segment.word)
        aligned.append(
            Word(
                index=len(aligned),
                text=normalize(text),
                start=segment.start_frame / FRAMES_PER_SECOND,
                end=(segment.end_frame + 1) / FRAMES_PER_SECOND,
            )
        )
    if [word.text for word in aligned] != words:
        raise RuntimeError("Aligned words differ from the script.")
    return aligned


def find_audio(stem: str, directory: Path) -> Path:
    for suffix in AUDIO_SUFFIXES:
        candidate = directory / f"{stem}{suffix}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No audio for '{stem}' in {directory}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("stem", help="file stem, e.g. 01-introduction")
    parser.add_argument("--dir", type=Path, default=NARRATION_DIR,
                        help="narration folder (default: assets/narration)")
    args = parser.parse_args()

    audio = find_audio(args.stem, args.dir)
    script = (args.dir / f"{args.stem}.txt").read_text(encoding="utf-8")
    words = align(load_pcm(audio), script_words(script))
    output = args.dir / f"{args.stem}.words.tsv"
    write_words(output, words, source=audio.name)
    print(f"Wrote {len(words)} words to {output.relative_to(Path.cwd())}"
          if output.is_relative_to(Path.cwd()) else f"Wrote {output}")


if __name__ == "__main__":
    main()
