"""Waveform mobjects: steady sine waves and logarithmic sweeps."""

import math

import numpy as np
from manim import VMobject

from ..theme import THEME, Theme
from .frequency_axis import FrequencyAxis


class SineWave(VMobject):
    """A cosine wave between ``x_start`` and ``x_end`` around ``y``.

    ``period`` is in scene units. With ``phase=0`` the wave starts on a
    crest, so waves whose periods have a simple ratio share crests at
    regular intervals. Two waves built with the same ``x`` range,
    ``period`` and ``samples_per_period`` interpolate point by point, so
    ``Transform(flat_wave, full_wave)`` grows the amplitude smoothly.
    """

    def __init__(
        self,
        x_start: float,
        x_end: float,
        period: float,
        amplitude: float,
        y: float = 0.0,
        phase: float = 0.0,
        samples_per_period: int = 48,
        theme: Theme = THEME,
        **kwargs,
    ):
        kwargs.setdefault("stroke_color", theme.palette.ink)
        kwargs.setdefault("stroke_width", theme.strokes.thin)
        super().__init__(**kwargs)
        self.period = period
        self.amplitude = amplitude
        samples = max(2, int((x_end - x_start) / period * samples_per_period))
        xs = np.linspace(x_start, x_end, samples + 1)
        ys = y + amplitude * np.cos(2 * np.pi * (xs - x_start) / period
                                    + phase)
        self.set_points_smoothly(np.column_stack([xs, ys, np.zeros_like(xs)]))


def log_sweep(
    axis: FrequencyAxis,
    amplitude: float,
    period_start: float,
    period_end: float,
    samples_per_end_period: int = 14,
    theme: Theme = THEME,
    **kwargs,
) -> VMobject:
    """A sine wave along ``axis`` whose period shrinks exponentially.

    On a logarithmic axis this is what an exponential sine sweep (20 Hz
    rising to 20 kHz) looks like: the wave tightens steadily from left
    to right. Points are evenly spaced in x, so ``Create`` draws it at a
    constant horizontal speed.
    """
    kwargs.setdefault("stroke_color", theme.palette.ink)
    kwargs.setdefault("stroke_width", theme.strokes.hairline)
    width = axis.length
    left = axis.x_of(axis.f_min)
    k0, k1 = 1 / period_start, 1 / period_end
    ratio = k1 / k0
    count = int(width / period_end * samples_per_end_period)
    u = np.linspace(0.0, 1.0, count + 1)
    phase = 2 * np.pi * k0 * width * (ratio ** u - 1) / math.log(ratio)
    xs = left + u * width
    ys = axis.y + amplitude * np.sin(phase)
    wave = VMobject(**kwargs)
    wave.set_points_as_corners(np.column_stack([xs, ys, np.zeros_like(xs)]))
    return wave
