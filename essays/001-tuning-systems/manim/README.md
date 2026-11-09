# Tuning Systems · motion graphics

Manim scenes for essay 001 of *Sound Machines*. Each scene animates
one stretch of narration, and its animations are synced word by word to
the voice-over.

| Scene | File | Narration |
|-------|------|-----------|
| 01 · Introduction | `scenes/s01_introduction.py` | `assets/narration/01-introduction.*` |

## Setup

Requires Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

If pip fails while building `pycairo` or `manimpango` on macOS, install
the system libraries first: `brew install cairo pango pkg-config`.

The Noto fonts are bundled in `assets/fonts` and are registered
automatically, so you don't need to install them on your system.

## Rendering

```bash
python render.py 01                  # final 1920x1080 at 30 fps → renders/s01_introduction.mp4
python render.py 01 --draft          # quick 960x540 at 15 fps preview
python render.py 01 --quality 4k     # 3840x2160 at 30 fps
python render.py all                 # every scene
python render.py 01 --stills 5 20.5  # also save PNG frames at those video times
```

The narration audio is mixed into each video. Every scene opens on a
blank frame, holds it for 0.5 s, plays the narration and then fades
back to a blank frame. That makes it safe to cut scenes together end to end.

You can also call Manim directly from this folder:
`manim -pql scenes/s01_introduction.py Introduction`.

## Changing the style

Every visual decision lives in **`common/theme.py`**:

- `Palette`: the three colours (`background`, `ink`, `accent`). Greys
  are `ink` at lower opacity (`Opacity`). Don't add colours.
- `Fonts`: the serif (for titles and figures) and the sans (for labels)
  families and weights. To use a different family, drop its `.ttf`
  files into `assets/fonts` (or install it on your system) and change
  the name here.
- `TypeScale`, `Strokes`: font sizes and line widths.
- `Motion`: easing curves and standard durations.
- `NumberFormat`: thousands and decimal separators. For example, set
  `thousands_separator = " "` to get "20 000 Hz".

Scene-specific layout and content (axis size, wave ratio, cue offsets)
are constants at the top of each scene file.

## Narration and timing

Each scene's voice-over lives in `assets/narration` as three files that
share a stem:

```
01-introduction.mp3        audio
01-introduction.txt        script, written as spoken ("twenty thousand")
01-introduction.words.tsv  word timings (generated)
```

Scenes refer to moments in the narration **by word**, not by seconds:

```python
CUES = {
    "low_hz": ("twenty", 1),           # start of the 1st "twenty"
    "high_hz": ("thousand", 1),
    "rain_end": ("hear", 1, "end"),    # end of the 1st "hear"
}
```

If the voice-over is re-recorded or edited, regenerate the timings and
render again. The animations follow the new audio automatically:

```bash
pip install pocketsphinx           # offline aligner, only needed for this step
python tools/align_narration.py 01-introduction
```

## Sound

Scenes can add sound under the narration with `common.audio`:

```python
from common.audio import Piano, tone

piano = Piano()
self.add_sfx(tone(440, 1.5), at=cues.note, level=-14)
self.add_sfx(piano.note(220, 2.0).mix(piano.note(330, 2.0)),
             at=cues.together, level=-9)
```

- `tone(freq, duration)` is a pure sine wave at exactly `freq` Hz.
- `Piano().note(freq, duration)` is a sampled grand piano retuned to
  exactly `freq` Hz, so any tuning system or ratio is possible (220 and
  330 Hz give an exact 3:2 fifth, within a tenth of a cent). It uses the
  Salamander Grand Piano in `assets/samples/piano`. Its licence is
  CC BY 3.0, so **credit "Salamander Grand Piano by Alexander Holm (CC BY
  3.0)" wherever the video is published.**
- `level` is the sound's loudness relative to the narration, in dB of
  perceived loudness: -10 sits clearly under the voice, 0 matches it.
- `at` is narration time, so word cues work here too. Schedule sounds
  at the start of `compose` (a `soundtrack()` method), since Manim can't
  add a sound in the past. Make sure each sound ends before the scene
  does.

`tools/import_piano_samples.py` re-downloads the samples, for example
with another velocity layer (`--layer 6` for softer notes), and
re-measures each sample's real pitch.

## Adding a scene

1. Put `NN-name.mp3` and its spoken-form `NN-name.txt` in
   `assets/narration`, then run `tools/align_narration.py NN-name`.
2. Create `scenes/sNN_name.py` with one `EssayScene` subclass whose
   `narration = "NN-name"`. Write one method per beat and call them
   from `compose()`. `AGENTS.md` has a skeleton.
3. Run `python render.py NN --draft --stills …`, check the frames, then
   do a final render.

## Layout

```
manim/
├── render.py               render scenes with consistent settings
├── manim.cfg               Manim defaults (1080p30, no cache)
├── common/                 shared code; scenes import from here
│   ├── theme.py            colours, fonts, sizes, strokes, easing
│   ├── typography.py       serif(), sans(), Quantity ("20 Hz"), number format
│   ├── motion.py           appear, disappear, draw, Translate, Restyle
│   ├── timeline.py         at() and Timeline: animations at narration times
│   ├── narration.py        audio + word timings, cue lookup
│   ├── base_scene.py       EssayScene: background, narration, sound, blank bookends
│   ├── audio/              tone(), Piano sampler, perceived loudness
│   └── components/         FrequencyAxis, PianoKeyboard, PitchLine,
│                           TickField, SineWave, log_sweep, pluck, drift
├── scenes/                 one file per scene: sNN_name.py
├── tools/
│   ├── align_narration.py      word timings for a voice-over
│   └── import_piano_samples.py piano samples + measured pitches
└── assets/
    ├── fonts/              Noto Serif + Noto Sans (SIL OFL)
    ├── narration/          audio, scripts and word timings
    └── samples/piano/      Salamander Grand Piano, one layer (CC BY 3.0)
```

`media/` (Manim's working files) and `renders/` (finished videos) are
generated and git-ignored.

## Code style

The code follows PEP 8. Before committing, check it with
`pip install flake8 isort && flake8 && isort --check-only .`.
