"""House motion vocabulary: eased entrances, exits, draws and restyles.

Prefer these helpers over raw Manim animations so every scene moves the
same way. Each returns a regular Manim ``Animation``.
"""

import numpy as np
from manim import (
    DOWN,
    UP,
    Animation,
    Create,
    FadeIn,
    FadeOut,
    ManimColor,
    Mobject,
    VMobject,
    interpolate_color,
)

from .theme import THEME, Theme


def appear(
    mobject: Mobject,
    direction: np.ndarray = UP,
    run_time: float | None = None,
    theme: Theme = THEME,
    **kwargs,
) -> Animation:
    """Fade in while drifting a short distance along ``direction``."""
    return FadeIn(
        mobject,
        shift=direction * theme.motion.rise,
        run_time=run_time or theme.motion.medium,
        rate_func=theme.motion.ease_out,
        **kwargs,
    )


def disappear(
    mobject: Mobject,
    direction: np.ndarray = DOWN,
    run_time: float | None = None,
    theme: Theme = THEME,
    **kwargs,
) -> Animation:
    """Fade out while drifting a short distance along ``direction``."""
    return FadeOut(
        mobject,
        shift=direction * theme.motion.rise,
        run_time=run_time or theme.motion.short,
        rate_func=theme.motion.ease_in,
        **kwargs,
    )


def draw(
    mobject: Mobject,
    run_time: float | None = None,
    theme: Theme = THEME,
    **kwargs,
) -> Animation:
    """Draw strokes from their start to their end with eased timing."""
    kwargs.setdefault("rate_func", theme.motion.ease)
    return Create(mobject, run_time=run_time or theme.motion.long, **kwargs)


class Translate(Animation):
    """Move a mobject by ``vector`` without touching its style.

    It shifts incrementally instead of interpolating to a stored copy, so
    it composes with ``Restyle`` and with clocked updaters on the same
    mobject (both may run in one ``play_clips`` call).
    """

    composable = True

    def __init__(
        self,
        mobject: Mobject,
        vector: np.ndarray,
        theme: Theme = THEME,
        **kwargs,
    ):
        kwargs.setdefault("rate_func", theme.motion.ease)
        kwargs.setdefault("run_time", theme.motion.medium)
        self.vector = np.asarray(vector, dtype=float)
        self._progress = 0.0
        super().__init__(mobject, **kwargs)

    def begin(self) -> None:
        self._progress = 0.0
        super().begin()

    def interpolate_mobject(self, alpha: float) -> None:
        progress = self.rate_func(alpha)
        self.mobject.shift((progress - self._progress) * self.vector)
        self._progress = progress


class Restyle(Animation):
    """Animate stroke and fill colour/opacity without touching points.

    Unlike ``mobject.animate.set_color(...)`` this does not interpolate
    geometry, so it is safe on mobjects whose shape is driven by an
    updater (vibrating or drifting lines, for instance), and it composes
    with ``Translate`` on the same mobject.
    """

    composable = True

    def __init__(
        self,
        mobject: VMobject,
        *,
        stroke_color: str | None = None,
        stroke_opacity: float | None = None,
        fill_color: str | None = None,
        fill_opacity: float | None = None,
        theme: Theme = THEME,
        **kwargs,
    ):
        kwargs.setdefault("rate_func", theme.motion.ease)
        kwargs.setdefault("run_time", theme.motion.short)
        self._targets = (stroke_color, stroke_opacity, fill_color,
                         fill_opacity)
        self._starts: list[tuple] = []
        super().__init__(mobject, **kwargs)

    def begin(self) -> None:
        self._starts = [
            (
                member,
                member.get_stroke_color(),
                member.get_stroke_opacity(),
                member.get_fill_color(),
                member.get_fill_opacity(),
            )
            for member in self.mobject.family_members_with_points()
        ]
        super().begin()

    def interpolate_mobject(self, alpha: float) -> None:
        t = self.rate_func(alpha)
        s_color, s_opacity, f_color, f_opacity = self._targets
        restroke = s_color is not None or s_opacity is not None
        refill = f_color is not None or f_opacity is not None
        for member, sc, so, fc, fo in self._starts:
            if restroke:
                member.set_stroke(
                    color=_mix(sc, s_color, t),
                    opacity=_lerp(so, s_opacity, t),
                    family=False,
                )
            if refill:
                member.set_fill(
                    color=_mix(fc, f_color, t),
                    opacity=_lerp(fo, f_opacity, t),
                    family=False,
                )


def _mix(start: ManimColor, end: str | None, t: float) -> ManimColor:
    """Interpolate colours; ``end=None`` keeps ``start``."""
    return start if end is None else interpolate_color(
        start, ManimColor(end), t)


def _lerp(start: float, end: float | None, t: float) -> float:
    """Interpolate numbers; ``end=None`` keeps ``start``."""
    return start if end is None else start + (end - start) * t
