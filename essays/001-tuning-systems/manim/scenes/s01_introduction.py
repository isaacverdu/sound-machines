"""Scene 01, Introduction: from every audible pitch to the few we use.

Narration (``assets/narration/01-introduction.*``)::

    The human ear can perceive frequencies between 20 Hertz and 20,000
    Hertz. That's a practically infinite number of pitched sounds that
    most people can hear. In music, each note we hear is a pitched
    sound, but there are relatively few. A grand piano, for instance,
    has 88 keys, with the lowest vibrating at 27.5 Hertz and the highest
    at 4186 Hertz. So how do we choose the specific frequencies that
    will make up the notes in our music? In short: we choose frequencies
    that sound good when played together.

Beats, one method each, played in order by ``compose``:

    hearing_range  A sine sweep tightens across a logarithmic frequency
                   range as "20 Hz" and "20,000 Hz" land on its ends,
                   then holds through the next sentence.
    few_notes      One pitch is drawn in accent (a note) as the sweep
                   greys out and the range labels leave; the sweep then
                   fades as the 88 piano pitches grow, evenly spaced.
    piano          The pitches glide to the centre as a keyboard builds
                   under them; the lowest and highest keys light up and
                   their pitches vibrate.
    question       The keyboard leaves; the pitches loosen and drift.
    consonance     Two pitches a fifth apart unfold into waves that slide
                   together; their crests coincide at regular points.

Render with ``python render.py 01`` (see README.md).
"""

import _bootstrap  # noqa: F401  # isort: skip

import numpy as np
from manim import (
    DOWN,
    LEFT,
    UP,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    Transform,
    VGroup,
)

from common import (
    THEME,
    EssayScene,
    Quantity,
    Restyle,
    Translate,
    appear,
    at,
    disappear,
    draw,
)
from common.components import (
    HIGHEST_KEY,
    LOWEST_KEY,
    FrequencyAxis,
    PianoKeyboard,
    PitchLine,
    SineWave,
    drift,
    log_sweep,
    midi_to_frequency,
    piano_keys,
    pluck,
    white_key_width_for,
)

PALETTE = THEME.palette
OPACITY = THEME.opacity
MOTION = THEME.motion
STROKES = THEME.strokes
TYPE = THEME.type

# Moments in the narration, anchored to words of the aligned transcript:
# "word" | (word, occurrence) | (word, occurrence, "end"). Beats add small
# offsets to these (a negative offset lets a visual lead its word).
CUES = {
    # hearing_range
    "sweep": ("frequencies", 1),
    "low_hz": ("twenty", 1),
    "high_hz": ("thousand", 1),
    # few_notes
    "note": ("each", 1),
    "few": ("but", 1),
    "few_end": ("few", 1, "end"),
    # piano
    "piano": ("grand", 1),
    "lowest": ("lowest", 1),
    "vibrating": ("vibrating", 1),
    "low_freq": ("twenty", 3),
    "highest": ("highest", 1),
    "high_freq": ("four", 1),
    # question
    "question": ("so", 1),
    "how": ("how", 1),
    # consonance
    "split": ("in", 2),  # "...in our music?"
    "in_short": ("in", 3),
    "sound_good": ("sound", 2),
    "together": ("together", 1),
}

# Layout, in scene units (the frame is 14.22 x 8 with the origin at its
# centre).
# The frequency axis is an invisible reference: it maps frequency to x
# and sets the baseline that the sweep and the pitch lines share.
AXIS_WIDTH = 11.4
AXIS_Y = -0.2
PIANO_LIFT = 0.25  # the pitches rise to make room for the keyboard
PITCH_HEIGHT = 0.9
NOTE_HEIGHT = 1.4
KEYBOARD_GAP = 0.4  # from the baseline down to the top of the keys
KEYBOARD_HEIGHT = 1.0
WAVE_X = (-5.5, 5.5)
WAVE_ROWS = (0.95, -0.95)
WAVE_AMPLITUDE = 0.42  # shared by the opening sweep and the final waves
SWEEP_PERIODS = (1.6, 0.07)  # wave period at 20 Hz and at 20 kHz

# Labels in this scene are 20% smaller than the theme's defaults.
LABEL_SCALE = 0.8
RANGE_LABEL_SIZE = TYPE.figure * LABEL_SCALE
DETAIL_LABEL_SIZE = TYPE.figure_small * LABEL_SCALE
RANGE_LABEL_GAP = 0.18  # below the sweep's troughs

# Content.
NOTE_HZ = 440.0  # A4, the usual tuning reference
FIFTH_KEYS = (57, 64)  # A3 and E4, the piano's approximation of 3:2
FIFTH_HZ = (220.0, 330.0)  # the waves are drawn as an exact 3:2
WAVE_CYCLES = (6, 9)  # cycles across WAVE_X; same 2:3 period ratio


class Introduction(EssayScene):
    """Every audible pitch, the few that music uses, and why."""

    narration = "01-introduction"
    hold_after = 1.0  # let the final image breathe before the fade

    def compose(self) -> None:
        self.cue = self.voice.cues(CUES)
        self.axis = FrequencyAxis(width=AXIS_WIDTH).shift(UP * AXIS_Y)
        self.pitch = {
            midi: PitchLine(
                self.axis.point_of(midi_to_frequency(midi)),
                PITCH_HEIGHT,
                frequency=midi_to_frequency(midi),
                stroke_opacity=OPACITY.strong,
            )
            for midi in piano_keys()
        }
        self.pitches = VGroup(*self.pitch.values())

        self.hearing_range()
        self.few_notes()
        self.piano()
        self.question()
        self.consonance()

    # 1 -----------------------------------------------------------------

    def hearing_range(self) -> None:
        """The two limits of hearing, and a sine sweep between them."""
        cue, axis = self.cue, self.axis
        below = WAVE_AMPLITUDE + RANGE_LABEL_GAP
        self.range_labels = VGroup(
            Quantity(20, "Hz", size=RANGE_LABEL_SIZE).next_to(
                axis.point_of(axis.f_min), DOWN, buff=below),
            Quantity(20_000, "Hz", size=RANGE_LABEL_SIZE).next_to(
                axis.point_of(axis.f_max), DOWN, buff=below),
        )
        low_label, high_label = self.range_labels
        self.sweep = log_sweep(
            axis,
            amplitude=WAVE_AMPLITUDE,
            period_start=SWEEP_PERIODS[0],
            period_end=SWEEP_PERIODS[1],
            stroke_width=STROKES.thin,
        )
        self.play_clips(
            at(cue.sweep - 0.05, draw(self.sweep,
                                      run_time=cue.high_hz + 0.4 - cue.sweep,
                                      rate_func=MOTION.ease_soft)),
            at(cue.low_hz - 0.05, appear(low_label)),
            at(cue.high_hz - 0.05, appear(high_label)),
        )

    # 2 -----------------------------------------------------------------

    def few_notes(self) -> None:
        """One note stands out; the sweep gives way to the piano's 88."""
        cue, axis = self.cue, self.axis
        self.note_line = PitchLine(
            axis.point_of(NOTE_HZ),
            NOTE_HEIGHT,
            stroke_color=PALETTE.accent,
            stroke_width=STROKES.regular,
        )
        self.note_label = Quantity(
            NOTE_HZ, "Hz", size=DETAIL_LABEL_SIZE, color=PALETTE.accent,
        ).next_to(self.note_line, UP, buff=0.15)
        self.play_clips(
            at(cue.note - 0.1, draw(self.note_line, run_time=0.7,
                                    rate_func=MOTION.ease_out)),
            at(cue.note - 0.1, Restyle(self.sweep,
                                       stroke_opacity=OPACITY.faint,
                                       run_time=0.8)),
            at(cue.note + 0.35, appear(self.note_label)),
            at(cue.note - 0.1, disappear(self.range_labels)),
        )
        grow_pitches = LaggedStart(
            *(draw(line, run_time=0.5, rate_func=MOTION.ease_out)
              for line in self.pitches),
            lag_ratio=0.016,
        )
        self.play_clips(
            at(cue.few + 0.1, FadeOut(self.sweep),
               run_time=1.2, rate_func=MOTION.ease),
            at(cue.few + 0.2, grow_pitches),
        )
        self.hold_until(cue.few_end + 0.1)

    # 3 -----------------------------------------------------------------

    def piano(self) -> None:
        """A centred keyboard under the pitches; its extremes vibrate."""
        cue, axis = self.cue, self.axis
        x_low = axis.x_of(midi_to_frequency(LOWEST_KEY))
        x_high = axis.x_of(midi_to_frequency(HIGHEST_KEY))
        white = white_key_width_for(x_high - x_low)
        # The pitches slide right to centre the piano range on screen and
        # rise a little; the keyboard is built under where they land.
        move = np.array([-(x_low + x_high) / 2, PIANO_LIFT, 0.0])
        self.keyboard = PianoKeyboard(white, KEYBOARD_HEIGHT).shift(
            np.array([x_low - white / 2, axis.y - KEYBOARD_GAP, 0.0]) + move)
        self.keyboard.black_keys.set_z_index(1)

        keys_in = LaggedStart(
            *(FadeIn(self.keyboard.keys[midi], shift=UP * 0.1,
                     run_time=0.5, rate_func=MOTION.ease_out)
              for midi in piano_keys()),
            lag_ratio=0.02,
        )
        self.play_clips(
            at(cue.piano - 0.1, Translate(self.pitches, move, run_time=1.0)),
            at(cue.piano - 0.1,
               FadeOut(VGroup(self.note_line, self.note_label)),
               run_time=0.45, rate_func=MOTION.ease_in),
            at(cue.piano + 0.1, keys_in),
        )

        lowest, highest = self.pitch[LOWEST_KEY], self.pitch[HIGHEST_KEY]
        self.extreme_labels = VGroup(
            Quantity(27.5, "Hz", size=DETAIL_LABEL_SIZE,
                     color=PALETTE.accent).next_to(lowest, UP, buff=0.18),
            Quantity(4186, "Hz", size=DETAIL_LABEL_SIZE,
                     color=PALETTE.accent).next_to(highest, UP, buff=0.18),
        )
        self.plucks = [
            self.add_clocked(lowest, pluck(
                cue.vibrating, frequency=2.0, amplitude=0.12, decay=2.4)),
            self.add_clocked(highest, pluck(
                cue.high_freq, frequency=7.0, amplitude=0.05, decay=0.9)),
        ]
        self.play_clips(
            *self._highlight_key(LOWEST_KEY, cue.lowest - 0.05),
            at(cue.low_freq - 0.05, appear(self.extreme_labels[0])),
            *self._highlight_key(HIGHEST_KEY, cue.highest - 0.05),
            at(cue.high_freq - 0.05, appear(self.extreme_labels[1])),
        )
        self.hold_until(cue.question - 0.05)

    def _highlight_key(self, midi: int, start: float) -> list:
        """Clips that turn one key and its pitch line accent."""
        return [
            at(start, Restyle(self.keyboard.keys[midi],
                              fill_color=PALETTE.accent)),
            at(start, Restyle(self.pitch[midi],
                              stroke_color=PALETTE.accent,
                              stroke_opacity=OPACITY.full)),
        ]

    # 4 -----------------------------------------------------------------

    def question(self) -> None:
        """The keyboard leaves and the pitches come loose."""
        cue = self.cue
        self.stop_clocked(*self.plucks)
        extremes = VGroup(self.pitch[LOWEST_KEY], self.pitch[HIGHEST_KEY])
        for line in extremes:
            line.set_bow(0)
        leaving = VGroup(self.keyboard, self.extreme_labels)
        self.drift_clock = self.add_clocked(self.pitches, drift(
            list(self.pitches),
            amplitude=0.3,
            ramp_in=(cue.how, cue.how + 1.8),
            ramp_out=(cue.split - 0.85, cue.split - 0.15),
        ))
        self.play_clips(
            at(cue.question - 0.05, disappear(leaving, run_time=0.6)),
            at(cue.question - 0.05,
               Restyle(extremes, stroke_color=PALETTE.ink,
                       stroke_opacity=OPACITY.strong)),
            at(cue.question + 0.15,
               Translate(self.pitches, DOWN * PIANO_LIFT, run_time=1.0)),
        )
        self.hold_until(cue.split - 0.1)

    # 5 -----------------------------------------------------------------

    def consonance(self) -> None:
        """Two pitches become waves whose crests line up when combined."""
        cue = self.cue
        chosen = [self.pitch[midi] for midi in FIFTH_KEYS]
        others = VGroup(*(line for midi, line in self.pitch.items()
                          if midi not in FIFTH_KEYS))
        span = WAVE_X[1] - WAVE_X[0]
        periods = [span / cycles for cycles in WAVE_CYCLES]
        waves = [
            SineWave(*WAVE_X, period, WAVE_AMPLITUDE, y=row)
            for row, period in zip(WAVE_ROWS, periods)
        ]
        # Each chosen pitch slides to the start of its wave, as a segment
        # spanning the wave's height; the wave then unrolls from it.
        starts = [
            Line(np.array([WAVE_X[0], row - WAVE_AMPLITUDE, 0]),
                 np.array([WAVE_X[0], row + WAVE_AMPLITUDE, 0]),
                 stroke_color=PALETTE.accent,
                 stroke_width=STROKES.regular)
            for row in WAVE_ROWS
        ]
        labels = VGroup(*(
            Quantity(hz, "Hz", size=DETAIL_LABEL_SIZE).next_to(
                wave.get_corner(UP + LEFT), UP, buff=0.22,
                aligned_edge=LEFT)
            for hz, wave in zip(FIFTH_HZ, waves)
        ))

        self.play_clips(
            at(cue.split - 0.05,
               Restyle(others, stroke_opacity=0, run_time=1.0)),
            *(at(cue.split - 0.05, Transform(line, target),
                 run_time=1.2, rate_func=MOTION.ease)
              for line, target in zip(chosen, starts)),
        )
        self.stop_clocked(self.drift_clock)
        self.discard(others)

        self.play_clips(
            *(at(cue.in_short - 0.15 + 0.2 * index,
                 draw(wave, run_time=1.5, rate_func=MOTION.ease_soft))
              for index, wave in enumerate(waves)),
            at(cue.in_short,
               FadeOut(VGroup(*chosen), run_time=0.8,
                       rate_func=MOTION.ease_in)),
            at(cue.in_short + 0.55, appear(labels, run_time=0.6)),
        )

        # Crests coincide every 2 cycles of the lower wave (3 of the
        # upper), starting at the left edge where both waves begin.
        common_period = periods[0] * 2
        crests = np.arange(WAVE_X[0], WAVE_X[1] + 1e-6, common_period)
        guides = VGroup(*(
            Line(np.array([x, -0.85, 0]), np.array([x, 0.85, 0]),
                 stroke_color=PALETTE.accent,
                 stroke_width=STROKES.hairline,
                 stroke_opacity=OPACITY.medium)
            for x in crests
        ))
        dots = VGroup(*(
            Dot(np.array([x, WAVE_AMPLITUDE, 0]), radius=0.055,
                color=PALETTE.accent)
            for x in crests
        ))
        self.play_clips(
            *(at(cue.sound_good - 0.1,
                 Translate(wave, DOWN * row, run_time=1.1))
              for wave, row in zip(waves, WAVE_ROWS)),
            at(cue.sound_good - 0.1, disappear(labels, run_time=0.5)),
            at(cue.together - 0.1, LaggedStart(
                *(draw(guide, run_time=0.5) for guide in guides),
                lag_ratio=0.15)),
            at(cue.together, LaggedStart(
                *(FadeIn(dot, scale=0.4, run_time=0.4,
                         rate_func=MOTION.ease_out) for dot in dots),
                lag_ratio=0.15)),
        )
