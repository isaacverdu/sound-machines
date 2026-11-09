"""Schedule animations at absolute narration times.

Manim plays animations one ``play`` call at a time. Syncing to a voice-
over needs overlapping animations that start at arbitrary moments, so a
beat is written as a list of clips::

    self.play_clips(
        at(cues.low_hz, appear(label_low)),
        at(cues.low_hz + 0.1, draw(sweep, run_time=2.0)),
    )

Rule: within one ``play_clips`` call, a mobject (or any of its parts)
may be the target of only one clip, because Manim captures every
animation's starting state when the call begins. Split a beat into
consecutive calls when the same mobject must change twice. The
exception is animations marked ``composable`` (``Translate`` and
``Restyle``), which change only position or only style and can overlap
each other freely.
"""

from dataclasses import dataclass

import numpy as np
from manim import Animation, AnimationGroup
from manim.animation.animation import prepare_animation


@dataclass(frozen=True)
class Clip:
    """An animation and the narration time (seconds) when it starts."""

    start: float
    animation: Animation

    @property
    def end(self) -> float:
        return self.start + self.animation.run_time


def at(
    start: float,
    animation: Animation,
    run_time: float | None = None,
    rate_func=None,
) -> Clip:
    """Schedule ``animation`` to start at narration time ``start``."""
    animation = prepare_animation(animation)
    if run_time is not None:
        animation.run_time = run_time
    if rate_func is not None:
        animation.rate_func = rate_func
    return Clip(start, animation)


class Timeline(AnimationGroup):
    """An ``AnimationGroup`` whose members start at explicit times.

    ``origin`` is the narration time at which the group starts playing.
    Mobject updaters keep running during the group, so time-driven
    effects (vibrations, drifts) continue underneath scheduled clips.
    """

    def __init__(self, *clips: Clip, origin: float, **kwargs):
        if not clips:
            raise ValueError("A Timeline needs at least one clip.")
        _check_unique_targets(clips)
        self._offsets = np.clip(
            [clip.start - origin for clip in clips], 0.0, None)
        for clip in clips:
            clip.animation.suspend_mobject_updating = False
        kwargs.setdefault("suspend_mobject_updating", False)
        super().__init__(*(clip.animation for clip in clips), **kwargs)

    def build_animations_with_timings(self) -> None:
        super().build_animations_with_timings()
        run_times = np.array([anim.run_time for anim in self.animations])
        self.anims_with_timings["start"] = self._offsets
        self.anims_with_timings["end"] = self._offsets + run_times


def _compatible(first: Animation, second: Animation) -> bool:
    """Two composable animations of different kinds may share targets."""
    return (
        getattr(first, "composable", False)
        and getattr(second, "composable", False)
        and type(first) is not type(second)
    )


def _check_unique_targets(clips: tuple[Clip, ...]) -> None:
    """Refuse clips whose targets overlap, unless they are compatible."""
    owners: dict[int, Clip] = {}
    for clip in clips:
        for member in clip.animation.mobject.get_family():
            other = owners.get(id(member))
            if other is not None and not _compatible(
                    other.animation, clip.animation):
                raise ValueError(
                    f"A {type(member).__name__} is animated by clips at "
                    f"{other.start:.2f}s and {clip.start:.2f}s in the same "
                    "play_clips call; split them into consecutive calls."
                )
            owners.setdefault(id(member), clip)
