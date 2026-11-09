"""Visual identity shared by every scene of the essay.

This is the single place to restyle the project. Scenes and components
read colours, fonts, sizes, stroke widths and easing from ``THEME``
instead of hard-coding values, so a change here propagates everywhere.

The palette is deliberately limited to three colours. Secondary tones
(greys, faint guides) are made by lowering the opacity of ``ink``, never
by introducing a new colour.

Edit the defaults below to restyle every scene at once. Helpers and
components also accept a ``theme`` argument, for one-off experiments::

    from dataclasses import replace
    from common.theme import THEME, Fonts

    ALL_SANS = replace(THEME, fonts=Fonts(serif="Noto Sans"))
    label = Quantity(440, "Hz", theme=ALL_SANS)
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from manim import LIGHT, NORMAL
from manim.utils import rate_functions as rf

RateFunc = Callable[[float], float]


@dataclass(frozen=True)
class Palette:
    """The three colours of the project, as hex strings."""

    background: str = "#F4F1EA"  # off-white paper
    ink: str = "#1C1C1C"  # off-black for text and shapes
    accent: str = "#E0472B"  # vermilion, used sparingly for emphasis


@dataclass(frozen=True)
class Opacity:
    """Named opacities used to derive secondary tones from ``ink``."""

    full: float = 1.0
    strong: float = 0.8
    medium: float = 0.55
    faint: float = 0.3
    ghost: float = 0.14


@dataclass(frozen=True)
class Fonts:
    """Font families and weights.

    Families are resolved by name through Pango. Any ``.ttf``/``.otf``
    placed in ``assets/fonts`` is registered automatically when a scene
    starts, so the bundled Noto files work without a system install.
    """

    serif: str = "Noto Serif"  # titles and prominent figures
    sans: str = "Noto Sans"  # labels and running text
    serif_weight: str = NORMAL
    sans_weight: str = LIGHT


@dataclass(frozen=True)
class TypeScale:
    """Font sizes, in Manim font-size units (Manim's default is 48)."""

    title: float = 72
    figure: float = 40  # prominent numbers, e.g. "20,000"
    figure_small: float = 32  # secondary numbers, e.g. "27.5"
    label: float = 24  # small sans labels
    unit_ratio: float = 0.5  # unit ("Hz") size relative to its figure


@dataclass(frozen=True)
class Strokes:
    """Stroke widths, in Manim units (1 unit is about 1.35 px at 1080p)."""

    hairline: float = 1.0
    thin: float = 1.6
    regular: float = 2.4


@dataclass(frozen=True)
class Motion:
    """Easing curves and standard durations, in seconds."""

    ease: RateFunc = field(default=rf.ease_in_out_cubic)  # moves, morphs
    ease_in: RateFunc = field(default=rf.ease_in_cubic)  # exits
    ease_out: RateFunc = field(default=rf.ease_out_cubic)  # entrances
    ease_soft: RateFunc = field(default=rf.ease_in_out_sine)  # sweeps
    short: float = 0.45
    medium: float = 0.8
    long: float = 1.4
    rise: float = 0.12  # distance text travels while fading in or out


@dataclass(frozen=True)
class NumberFormat:
    """How numbers are written on screen."""

    thousands_separator: str = ","  # "20,000"; use " " for "20 000"
    decimal_separator: str = "."  # "27.5"


@dataclass(frozen=True)
class Layout:
    """Frame geometry in Manim units (the frame is 14.22 x 8 at 16:9)."""

    margin: float = 0.7  # minimum distance between content and frame edge


@dataclass(frozen=True)
class Theme:
    """Bundle of every style decision; pass it around or use ``THEME``."""

    palette: Palette = field(default_factory=Palette)
    opacity: Opacity = field(default_factory=Opacity)
    fonts: Fonts = field(default_factory=Fonts)
    type: TypeScale = field(default_factory=TypeScale)
    strokes: Strokes = field(default_factory=Strokes)
    motion: Motion = field(default_factory=Motion)
    numbers: NumberFormat = field(default_factory=NumberFormat)
    layout: Layout = field(default_factory=Layout)


THEME = Theme()
