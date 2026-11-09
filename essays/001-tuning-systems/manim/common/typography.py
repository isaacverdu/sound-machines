"""Text helpers that apply the theme's fonts, sizes and colours.

Use ``serif`` for titles and prominent figures, ``sans`` for labels and
running text, and ``Quantity`` for a number with a unit ("20 Hz").
"""

from pathlib import Path

import manimpango
from manim import RIGHT, UP, Text, VGroup

from .paths import FONTS_DIR
from .theme import THEME, Theme

_FONT_SUFFIXES = (".ttf", ".otf")
_registered_fonts: set[Path] = set()

# Glyphs whose bottom sits exactly on the baseline (no overshoot).
_FLAT_BOTTOM_GLYPHS = "1247HIKLMNTXZ"


def register_project_fonts(directory: Path = FONTS_DIR) -> None:
    """Make every font file in ``directory`` available to Pango."""
    if not directory.is_dir():
        return
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() in _FONT_SUFFIXES:
            resolved = path.resolve()
            if resolved not in _registered_fonts:
                manimpango.register_font(str(resolved))
                _registered_fonts.add(resolved)


def serif(
    text: str,
    size: float | None = None,
    color: str | None = None,
    weight: str | None = None,
    theme: Theme = THEME,
    **kwargs,
) -> Text:
    """Return ``text`` set in the theme's serif (titles, figures)."""
    return Text(
        text,
        font=theme.fonts.serif,
        weight=weight or theme.fonts.serif_weight,
        font_size=size or theme.type.title,
        color=color or theme.palette.ink,
        **kwargs,
    )


def sans(
    text: str,
    size: float | None = None,
    color: str | None = None,
    weight: str | None = None,
    theme: Theme = THEME,
    **kwargs,
) -> Text:
    """Return ``text`` set in the theme's sans serif (labels, text)."""
    return Text(
        text,
        font=theme.fonts.sans,
        weight=weight or theme.fonts.sans_weight,
        font_size=size or theme.type.label,
        color=color or theme.palette.ink,
        **kwargs,
    )


def format_number(
    value: float,
    decimals: int | None = None,
    theme: Theme = THEME,
) -> str:
    """Format ``value`` with the theme's separators.

    When ``decimals`` is None, integers get no decimals and other values
    get as many as needed (up to three).
    """
    if decimals is None:
        decimals = 0 if float(value).is_integer() else 3
        text = f"{value:,.{decimals}f}"
        if decimals:
            text = text.rstrip("0").rstrip(".")
    else:
        text = f"{value:,.{decimals}f}"
    fmt = theme.numbers
    return (
        text.replace(",", "\0")
        .replace(".", fmt.decimal_separator)
        .replace("\0", fmt.thousands_separator)
    )


def _baseline_glyph(text: Text, source: str):
    """Return a glyph of ``text`` that sits on the baseline."""
    glyphs = [char for char in source if not char.isspace()]
    for index, char in enumerate(glyphs):
        if char in _FLAT_BOTTOM_GLYPHS and index < len(text):
            return text[index]
    return text[0]


class Quantity(VGroup):
    """A serif figure followed by a smaller sans unit, sharing a baseline.

    ``Quantity(20000, "Hz")`` renders as "20,000 Hz". Access the parts
    through ``.figure`` and ``.unit``.
    """

    def __init__(
        self,
        value: float | str,
        unit: str = "Hz",
        size: float | None = None,
        color: str | None = None,
        theme: Theme = THEME,
        **kwargs,
    ):
        size = size or theme.type.figure
        figure_text = (
            value if isinstance(value, str)
            else format_number(value, theme=theme)
        )
        self.figure = serif(figure_text, size=size, color=color, theme=theme)
        self.unit = sans(
            unit,
            size=size * theme.type.unit_ratio,
            color=color,
            theme=theme,
        )
        gap = 0.22 * self.figure.height
        self.unit.next_to(self.figure, RIGHT, buff=gap)
        baseline = _baseline_glyph(self.figure, figure_text).get_bottom()[1]
        unit_base = _baseline_glyph(self.unit, unit).get_bottom()[1]
        self.unit.shift(UP * (baseline - unit_base))
        super().__init__(self.figure, self.unit, **kwargs)
