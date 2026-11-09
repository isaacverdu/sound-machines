# Working on this project (for AI agents and humans)

Read `README.md` first. These are the rules that keep scenes consistent
and in sync with the narration.

## Style

- **No hard-coded style.** Colours, fonts, sizes, stroke widths and
  easing come from `common.theme.THEME`. If a value is missing, add it
  to the theme instead of writing it inline.
- **Three colours only:** `background`, `ink` and `accent`. Make greys
  with `ink` at an `OPACITY` level. Keep the accent rare: it marks the
  one thing the narration is pointing at.
- **Type:** use `serif()` for titles and prominent figures, `sans()` for
  labels, and `Quantity(value, unit)` for numbers with units. Put
  numbers on screen and keep sentences off it. Don't caption the
  narration.
- **Lines:** use `STROKES.hairline`, `thin` or `regular`. Don't use
  anything heavier.
- **Motion:** ease almost everything. Use `appear` / `disappear` (fade
  plus a small drift), `draw` (eased `Create`), `Translate` and
  `Restyle`. Keep linear timing for things that are physically uniform.
- **Bookends:** `EssayScene` handles the blank first and last frames
  and the final fade. Don't override `construct`. Put the content in
  `compose`.

## Timing

- Refer to moments by narration word, through the `CUES` dict at the top
  of the scene, never by raw seconds. Offsets of ±0.3 s around a cue
  are fine, and visuals may lead their word by about 0.1 s.
- `self.now` is narration time (negative during the 0.5 s lead-in).
  `self.hold_until(t)` waits until a given narration time.
- A beat is one method. It schedules clips with
  `self.play_clips(at(t, animation), …)`.
- **Within one `play_clips` call, each mobject may be targeted by only
  one clip.** Manim captures every starting state when the call begins.
  `Translate` and `Restyle` are the exception: they can overlap each
  other on the same mobject. To change a mobject twice, use two
  consecutive calls. A clip that starts before the current time raises
  an error with both times in the message.
- For continuous effects (sweeps, rain, vibration, drift), use
  `driver = self.add_clocked(target, fn)` where `fn(target, t)` sets
  the target's state for narration time `t`. End the effect with
  `self.stop_clocked(driver)`. Write `fn` so that it is absolute
  (a pure function of `t`), not incremental.
- Anything faded out inside `play_clips` is removed from the scene
  automatically. Use `self.discard(mob)` to remove a mobject and all of
  its parts.

## Manim pitfalls already hit here

- Don't assign `self.width`, `self.height` or `self.color` in a Mobject
  subclass. They are properties and will resize or recolour it.
- `Scene.remove(group)` leaves behind parts that were added separately.
  Use `self.discard`.
- `FadeOut` restores its mobject after cleanup. `play_clips` discards
  it for you, but plain `self.play(FadeOut(x))` does not.
- Manim freezes mobjects that it thinks are static into a cached
  background. Anything changed by an updater must be driven through
  `add_clocked`, which marks the target as moving.
- Caching is disabled in `manim.cfg` because Manim can't hash clocked
  updaters, so stale partial movies would survive edits.

## Verifying a change

1. `python render.py NN --draft --stills <times>` and look at the PNGs in
   `renders/stills/`, especially at the busiest moments and around
   transitions. Still times are video seconds (narration time + 0.5).
2. Final render: `python render.py NN`.
3. `flake8 && isort --check-only .`

## Scene skeleton

```python
"""Scene NN, Title: one-line summary.

Narration::

    (paste the script here)

Beats:
    first_beat   what the viewer sees
"""

import _bootstrap  # noqa: F401  # isort: skip

from common import THEME, EssayScene, appear, at, serif

CUES = {
    "start": ("first", 1),
}


class Title(EssayScene):
    """What this scene shows."""

    narration = "NN-name"

    def compose(self) -> None:
        self.cue = self.voice.cues(CUES)
        self.first_beat()

    def first_beat(self) -> None:
        title = serif("Title", color=THEME.palette.ink)
        self.play_clips(at(self.cue.start - 0.1, appear(title)))
```
