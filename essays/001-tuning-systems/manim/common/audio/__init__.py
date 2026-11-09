"""Sound for the essay's scenes: synthesized tones and a sampled piano.

Build a ``Sound`` and place it at a narration time with
``EssayScene.add_sfx``, which also sets its loudness relative to the
voice-over (in dB of perceived loudness; negative is quieter)::

    from common.audio import Piano, tone

    self.add_sfx(tone(440, 1.5), at=cues.note, level=-14)
    self.add_sfx(Piano().note(220, 2.0), at=cues.fifth, level=-10)
"""

from .loudness import file_loudness
from .piano import Piano
from .sound import SAMPLE_RATE, Sound
from .synth import tone

__all__ = ["SAMPLE_RATE", "Piano", "Sound", "file_loudness", "tone"]
