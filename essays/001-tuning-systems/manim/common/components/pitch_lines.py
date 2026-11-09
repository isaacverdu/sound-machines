"""Vertical lines standing on a frequency axis, one per pitch.

``TickField`` draws thousands of hairlines as a single path, for dense
"every possible pitch" textures. ``PitchLine`` is one line that can bow
sideways like a vibrating string. ``pluck`` and ``drift`` build clocked
updaters (see ``EssayScene.add_clocked``) that animate them over time.
"""

import math
from collections.abc import Callable, Sequence

import numpy as np
from manim import UP, ValueTracker, VMobject

from ..theme import THEME, Theme
from .frequency_axis import FrequencyAxis


def _ease_out(t: np.ndarray) -> np.ndarray:
    return 1 - (1 - t) ** 3


def _ease_in(t: np.ndarray) -> np.ndarray:
    return t ** 3


class TickField(VMobject):
    """Many vertical hairlines on ``axis``, rendered as one path.

    Every tick has a birth time, when it grows out of the axis, and an
    optional death time, when it retracts into it. Call ``update_to(t)``
    with the narration time on every frame (``EssayScene.add_clocked``).
    The overall opacity is the ``opacity`` tracker, so it can be
    animated with ``field.opacity.animate.set_value(...)``.
    """

    def __init__(
        self,
        axis: FrequencyAxis,
        frequencies: Sequence[float],
        height: float,
        births: Sequence[float],
        deaths: Sequence[float] | None = None,
        grow_time: float = 0.25,
        retract_time: float = 0.3,
        opacity: float | None = None,
        stroke_width: float | None = None,
        color: str | None = None,
        theme: Theme = THEME,
        **kwargs,
    ):
        super().__init__(
            stroke_color=color or theme.palette.ink,
            stroke_width=stroke_width or theme.strokes.hairline,
            fill_opacity=0,
            **kwargs,
        )
        self.axis = axis
        self.frequencies = np.asarray(frequencies, dtype=float)
        self.tick_height = height
        self.births = np.asarray(births, dtype=float)
        count = len(self.frequencies)
        self.deaths = (np.full(count, np.inf) if deaths is None
                       else np.asarray(deaths, dtype=float))
        self.grow_time = grow_time
        self.retract_time = retract_time
        self.opacity = ValueTracker(
            theme.opacity.faint if opacity is None else opacity)
        self.update_to(-np.inf)

    def heights_at(self, t: float) -> np.ndarray:
        """Height of every tick at narration time ``t``."""
        grown = _ease_out(np.clip((t - self.births) / self.grow_time, 0, 1))
        gone = _ease_in(np.clip((t - self.deaths) / self.retract_time, 0, 1))
        return self.tick_height * grown * (1 - gone)

    def update_to(self, t: float) -> "TickField":
        """Rebuild the path for narration time ``t``."""
        heights = self.heights_at(t)
        visible = heights > 1e-4
        self.set_stroke(opacity=self.opacity.get_value())
        if not visible.any():
            # Keep a degenerate, invisible path so the mobject stays valid.
            self.set_points(np.zeros((4, 3)) + self.axis.point_of(
                self.axis.f_min))
            self.set_stroke(opacity=0)
            return self
        xs = self.axis.x_of(self.frequencies[visible])
        base = self.axis.y
        tops = base + heights[visible]
        points = np.zeros((4 * len(xs), 3))
        for k in range(4):
            points[k::4, 0] = xs
            points[k::4, 1] = base + (tops - base) * k / 3
        self.set_points(points)
        return self


class PitchLine(VMobject):
    """A vertical line for one pitch that can bow like a plucked string.

    The bottom and top points stay fixed while bowing, so the line can
    be shifted or restyled freely in between.
    """

    def __init__(
        self,
        base: np.ndarray,
        height: float,
        frequency: float | None = None,
        theme: Theme = THEME,
        **kwargs,
    ):
        kwargs.setdefault("stroke_color", theme.palette.ink)
        kwargs.setdefault("stroke_width", theme.strokes.thin)
        super().__init__(**kwargs)
        self.frequency = frequency
        self.set_points_as_corners([base, base + UP * height])

    @property
    def base(self) -> np.ndarray:
        return self.get_start()

    def set_bow(self, amount: float, samples: int = 25) -> "PitchLine":
        """Displace the middle of the line sideways by ``amount``."""
        start, end = self.get_start().copy(), self.get_end().copy()
        if abs(amount) < 1e-5:
            return self.set_points_as_corners([start, end])
        s = np.linspace(0, 1, samples)
        points = start + np.outer(s, end - start)
        points[:, 0] += amount * np.sin(np.pi * s)
        return self.set_points_smoothly(points)


Clocked = Callable[[VMobject, float], None]


def pluck(
    start: float,
    frequency: float,
    amplitude: float,
    decay: float,
    attack: float = 0.05,
) -> Clocked:
    """Clocked updater that vibrates a ``PitchLine`` from ``start``.

    ``frequency`` is the visual vibration rate in Hz (keep it under a
    third of the frame rate), ``decay`` the time constant in seconds.
    """
    def update(line: PitchLine, t: float) -> None:
        elapsed = t - start
        if elapsed <= 0:
            line.set_bow(0)
            return
        envelope = (1 - math.exp(-elapsed / attack)) * math.exp(
            -elapsed / decay)
        line.set_bow(
            amplitude * envelope * math.sin(2 * math.pi * frequency * elapsed))

    return update


def drift(
    lines: Sequence[VMobject],
    amplitude: float,
    ramp_in: tuple[float, float],
    ramp_out: tuple[float, float],
    seed: int = 7,
) -> Clocked:
    """Clocked updater that lets ``lines`` wander sideways, then settle.

    The wander grows from 0 to ``amplitude`` across ``ramp_in`` (start,
    end in narration seconds) and returns to 0 across ``ramp_out``, at
    which point every line is back exactly where it started and the
    updater stops touching the lines.
    """
    rng = np.random.default_rng(seed)
    count = len(lines)
    rest_x = np.array([line.get_start()[0] for line in lines])
    speeds = rng.uniform(0.5, 1.3, (2, count))
    phases = rng.uniform(0, 2 * np.pi, (2, count))

    def ramp(t: float, start: float, end: float) -> float:
        x = min(max((t - start) / (end - start), 0.0), 1.0)
        return x * x * (3 - 2 * x)

    settled = False

    def update(_group: VMobject, t: float) -> None:
        nonlocal settled
        if t >= ramp_out[1]:
            # Back at rest: snap exactly once, then leave the lines alone
            # so other animations can move them.
            if not settled:
                for line, x in zip(lines, rest_x):
                    line.shift((x - line.get_start()[0]) * np.array(
                        [1.0, 0.0, 0.0]))
                settled = True
            return
        settled = False
        strength = amplitude * (ramp(t, *ramp_in) - ramp(t, *ramp_out))
        offsets = strength * (
            0.65 * np.sin(speeds[0] * t + phases[0])
            + 0.35 * np.sin(speeds[1] * 1.7 * t + phases[1])
        )
        for line, x, offset in zip(lines, rest_x, offsets):
            line.shift((x + offset - line.get_start()[0]) * np.array(
                [1.0, 0.0, 0.0]))

    return update
