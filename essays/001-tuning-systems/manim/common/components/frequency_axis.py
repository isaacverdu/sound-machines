"""A horizontal, logarithmic frequency axis."""

import math

import numpy as np
from manim import DOWN, LEFT, RIGHT, UP, Line, VectorizedPoint, VGroup

from ..theme import THEME, Theme


class FrequencyAxis(VGroup):
    """A thin baseline mapping frequency to x on a logarithmic scale.

    On a log scale equal musical intervals take equal space, so the 88
    keys of a piano land evenly spaced. Use ``x_of`` / ``point_of`` to
    place anything on the axis; they follow the axis when it is shifted
    (do not scale the axis after creating it).

    Parts: ``line`` (the baseline) and ``min_tick`` / ``max_tick`` (short
    marks at both ends). Animate the parts individually to reveal them
    one by one; shifting the axis moves every part, shown or not.
    """

    def __init__(
        self,
        f_min: float = 20.0,
        f_max: float = 20_000.0,
        width: float = 11.4,
        tick_size: float = 0.16,
        theme: Theme = THEME,
        **kwargs,
    ):
        self.f_min = f_min
        self.f_max = f_max
        self.length = width
        self.theme = theme
        self.line = Line(
            LEFT * width / 2,
            RIGHT * width / 2,
            color=theme.palette.ink,
            stroke_width=theme.strokes.thin,
        )
        # Invisible anchor that moves with the group; the line itself is
        # partially drawn while it is being created, so it is unreliable.
        self._anchor = VectorizedPoint(LEFT * width / 2)
        self.min_tick = self.tick(f_min, tick_size)
        self.max_tick = self.tick(f_max, tick_size)
        super().__init__(
            self._anchor, self.line, self.min_tick, self.max_tick, **kwargs
        )

    @property
    def y(self) -> float:
        """Vertical position of the baseline."""
        return float(self._anchor.get_center()[1])

    def fraction(self, frequency: float) -> float:
        """Position of ``frequency`` along the axis, from 0 to 1."""
        return math.log(frequency / self.f_min) / math.log(
            self.f_max / self.f_min)

    def x_of(self, frequency: float | np.ndarray) -> float | np.ndarray:
        """Scene x coordinate of ``frequency`` (scalar or array)."""
        left = self._anchor.get_center()[0]
        span = np.log(np.asarray(frequency) / self.f_min)
        return left + self.length * span / math.log(self.f_max / self.f_min)

    def point_of(self, frequency: float, height: float = 0.0) -> np.ndarray:
        """Scene point at ``frequency``, ``height`` above the baseline."""
        return np.array([self.x_of(frequency), self.y + height, 0.0])

    def tick(self, frequency: float, size: float) -> Line:
        """A short vertical mark centred on the baseline."""
        center = self.point_of(frequency)
        return Line(
            center + DOWN * size / 2,
            center + UP * size / 2,
            color=self.theme.palette.ink,
            stroke_width=self.theme.strokes.thin,
        )
