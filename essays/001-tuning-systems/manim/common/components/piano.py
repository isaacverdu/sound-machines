"""A line-drawn 88-key piano keyboard and pitch helpers."""

import numpy as np
from manim import DOWN, LEFT, UP, Rectangle, VGroup

from ..theme import THEME, Theme

LOWEST_KEY = 21  # MIDI number of A0, 27.5 Hz
HIGHEST_KEY = 108  # MIDI number of C8, 4186 Hz
WHITE_PITCH_CLASSES = frozenset({0, 2, 4, 5, 7, 9, 11})

# Horizontal offset of each black key from the boundary between its two
# neighbouring white keys, in white-key widths (as on a real keyboard).
BLACK_KEY_OFFSETS = {1: -0.1, 3: 0.1, 6: -0.12, 8: 0.0, 10: 0.12}


def midi_to_frequency(midi: int, a4: float = 440.0) -> float:
    """Equal-tempered frequency of MIDI note ``midi``."""
    return a4 * 2 ** ((midi - 69) / 12)


def is_black(midi: int) -> bool:
    return midi % 12 not in WHITE_PITCH_CLASSES


def piano_keys(lowest: int = LOWEST_KEY, highest: int = HIGHEST_KEY):
    """MIDI numbers of a keyboard's keys, low to high."""
    return range(lowest, highest + 1)


class PianoKeyboard(VGroup):
    """A keyboard drawn with thin outlines and solid black keys.

    Built with its top-left corner at the origin; position it with the
    usual Manim methods. ``keys[midi]`` returns one key; ``white_keys``
    and ``black_keys`` are the two layers (black keys drawn on top).
    """

    def __init__(
        self,
        white_width: float,
        white_height: float,
        black_width_ratio: float = 0.58,
        black_height_ratio: float = 0.62,
        lowest: int = LOWEST_KEY,
        highest: int = HIGHEST_KEY,
        theme: Theme = THEME,
        **kwargs,
    ):
        self.white_width = white_width
        self.keys: dict[int, Rectangle] = {}
        whites, blacks = VGroup(), VGroup()
        palette, strokes = theme.palette, theme.strokes
        edge = 0.0  # x of the left edge of the next white key
        for midi in piano_keys(lowest, highest):
            if not is_black(midi):
                key = Rectangle(
                    width=white_width,
                    height=white_height,
                    stroke_color=palette.ink,
                    stroke_width=strokes.hairline,
                    fill_color=palette.background,
                    fill_opacity=1,
                )
                key.move_to(np.array([edge, 0, 0]), aligned_edge=UP + LEFT)
                edge += white_width
                whites.add(key)
            else:
                width = white_width * black_width_ratio
                key = Rectangle(
                    width=width,
                    height=white_height * black_height_ratio,
                    stroke_color=palette.ink,
                    stroke_width=strokes.hairline,
                    fill_color=palette.ink,
                    fill_opacity=1,
                )
                center_x = edge + BLACK_KEY_OFFSETS[midi % 12] * white_width
                key.move_to(np.array([center_x, 0, 0]), aligned_edge=UP)
                blacks.add(key)
            self.keys[midi] = key
        self.white_keys = whites
        self.black_keys = blacks
        super().__init__(whites, blacks, **kwargs)

    def top_of(self, midi: int) -> np.ndarray:
        """Centre of the top edge of key ``midi``."""
        return self.keys[midi].get_edge_center(UP)

    def bottom_of(self, midi: int) -> np.ndarray:
        """Centre of the bottom edge of key ``midi``."""
        return self.keys[midi].get_edge_center(DOWN)


def white_key_width_for(span: float, lowest: int = LOWEST_KEY,
                        highest: int = HIGHEST_KEY) -> float:
    """White-key width so the outer key centres are ``span`` apart.

    Assumes both outer keys are white, as on a standard 88-key piano.
    """
    whites = sum(not is_black(m) for m in piano_keys(lowest, highest))
    return span / (whites - 1)


__all__ = [
    "HIGHEST_KEY",
    "LOWEST_KEY",
    "PianoKeyboard",
    "is_black",
    "midi_to_frequency",
    "piano_keys",
    "white_key_width_for",
]
