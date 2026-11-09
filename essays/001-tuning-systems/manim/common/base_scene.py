"""Base class for every scene of the essay."""

from collections.abc import Callable
from functools import cached_property

from manim import (
    Animation,
    AnimationGroup,
    FadeOut,
    Mobject,
    Scene,
    ValueTracker,
    config,
)

from .audio import Sound, file_loudness
from .narration import Narration
from .paths import PROJECT_ROOT
from .theme import THEME
from .timeline import Clip, Timeline
from .typography import register_project_fonts

ClockedUpdater = Callable[[Mobject, float], object]

_TIME_TOLERANCE = 1e-3
SFX_DIR = PROJECT_ROOT / "media" / "sfx"
REFERENCE_LOUDNESS = -23.0  # LUFS, used for scenes without narration


class EssayScene(Scene):
    """Paper background, bundled fonts, narration and blank bookends.

    Subclasses set ``narration`` (a file stem in ``assets/narration``)
    and implement ``compose``. Every scene starts on a blank frame,
    holds blank for ``lead_in`` seconds, plays the narration, and ends by
    fading whatever is left to a blank frame.

    Two clocks exist: Manim's ``self.time`` (seconds since the first
    frame) and ``self.now`` (seconds into the narration audio). Scenes
    should only think in narration time, which is what the word cues
    from ``Narration.cues`` are expressed in.
    """

    narration: str | None = None

    lead_in: float = 0.5  # blank seconds before the narration starts
    hold_after: float = 0.6  # seconds after the narration ends
    fade_out_time: float = 0.7  # final fade to blank
    blank_tail: float = 0.5  # blank seconds at the very end

    def setup(self) -> None:
        register_project_fonts()
        self.camera.background_color = THEME.palette.background
        self.voice = Narration.load(self.narration) if self.narration else None

    def construct(self) -> None:
        if self.voice is not None:
            self.add_sound(str(self.voice.audio_path),
                           time_offset=self.lead_in)
        self.compose()
        self.finish_on_blank()

    def compose(self) -> None:
        """Build and animate the scene. Implemented by subclasses."""
        raise NotImplementedError

    # Narration clock -------------------------------------------------

    @property
    def now(self) -> float:
        """Seconds into the narration (negative during the lead-in)."""
        return self.time - self.lead_in

    def hold_until(self, moment: float) -> None:
        """Wait until narration time ``moment`` (no-op if already past)."""
        remaining = moment - self.now
        if remaining > _TIME_TOLERANCE:
            self.wait(remaining)

    def play_clips(self, *clips: Clip) -> None:
        """Play clips at their scheduled narration times.

        The call blocks until the last clip ends. Clips scheduled before
        the current time raise an error rather than silently drifting
        out of sync. Whatever a clip fades out (``FadeOut``,
        ``disappear``) is removed from the scene for good afterwards.
        """
        origin = self.now
        tolerance = 1.5 / config.frame_rate  # holds may overshoot a frame
        late = [clip for clip in clips if clip.start < origin - tolerance]
        if late:
            starts = ", ".join(f"{clip.start:.2f}s" for clip in late)
            raise ValueError(
                f"Clips start at {starts} but the scene is already at "
                f"{origin:.2f}s. Check the beat order or its cue times."
            )
        self.play(Timeline(*clips, origin=origin))
        for clip in clips:
            self.discard(*_removed_by(clip.animation))

    def discard(self, *mobjects: Mobject) -> None:
        """Remove ``mobjects`` and all their parts from the scene.

        ``Scene.remove`` leaves behind parts that were added on their
        own (by an earlier animation, for instance); this does not.
        """
        self.remove(*(part for mob in mobjects for part in mob.get_family()))

    def add_clocked(self, target: Mobject, update: ClockedUpdater) -> Mobject:
        """Drive ``target`` from narration time on every frame.

        ``update(target, t)`` receives the narration time of the frame
        being rendered. Use it for continuous effects (sweeps, rain,
        vibration) that should not be tied to a single ``play`` call.

        The updater lives on an invisible driver added to the scene, so
        it runs whether or not ``target`` itself is in the scene, and is
        never paused by animations playing on ``target``. ``target`` also
        gets a no-op time-based updater so Manim redraws it every frame
        instead of freezing it into the cached static background. Pass
        the returned driver to ``stop_clocked`` to end the effect.
        """
        driver = Mobject()
        driver.add_updater(lambda _driver, dt: update(target, self.now))
        driver.clocked_target = target
        driver.clocked_marker = _redraw_marker()
        target.add_updater(driver.clocked_marker)
        driver.update(0)
        self.add(driver)
        return driver

    def stop_clocked(self, *drivers: Mobject) -> None:
        """End effects started with ``add_clocked``."""
        for driver in drivers:
            driver.clocked_target.remove_updater(driver.clocked_marker)
            self.remove(driver)

    # Sound effects ---------------------------------------------------

    def add_sfx(self, sound: Sound, at: float, level: float = -10.0) -> None:
        """Play ``sound`` at narration time ``at``, mixed under the voice.

        ``level`` is the sound's loudness relative to the narration, in
        dB of perceived loudness (LU): the loudest moment of the sound is
        set ``level`` below the voice's average loudness. -10 sits
        clearly under speech; 0 matches it.

        Sounds are rendered to ``media/sfx`` (cached by content) and
        mixed into the soundtrack by Manim. Schedule them in advance,
        never in the past, and make them end before the scene does.
        """
        offset = at + self.lead_in - self.time
        if offset < -_TIME_TOLERANCE:
            raise ValueError(
                f"Sound scheduled at {at:.2f}s but the scene is already at "
                f"{self.now:.2f}s. Schedule it earlier in compose().")
        sound = sound.at_loudness(self.voice_loudness + level)
        path = sound.write(SFX_DIR / f"{sound.fingerprint()}.wav")
        self.add_sound(str(path), time_offset=max(offset, 0.0))

    @cached_property
    def voice_loudness(self) -> float:
        """Integrated loudness of the narration in LUFS (-23 if none)."""
        if self.voice is None:
            return REFERENCE_LOUDNESS
        return file_loudness(self.voice.audio_path)

    # Ending ----------------------------------------------------------

    def finish_on_blank(self) -> None:
        """Hold after the narration, fade everything out, end blank."""
        if self.voice is not None:
            self.hold_until(self.voice.duration + self.hold_after)
        for mob in self.mobjects:
            mob.clear_updaters()
        visible = [
            mob for mob in self.mobjects
            if not isinstance(mob, ValueTracker)
            and mob.family_members_with_points()
        ]
        if visible:
            self.play(
                *(FadeOut(mob) for mob in visible),
                run_time=self.fade_out_time,
                rate_func=THEME.motion.ease_in,
            )
        self.clear()
        self.wait(self.blank_tail)


def _redraw_marker() -> Callable[[Mobject, float], None]:
    """A fresh no-op time-based updater that marks a mobject as moving."""
    def marker(mobject: Mobject, dt: float) -> None:
        """Does nothing; its ``dt`` argument is what Manim looks for."""
    return marker


def _removed_by(animation: Animation) -> list[Mobject]:
    """Mobjects that ``animation`` (or any animation inside it) removes."""
    if isinstance(animation, AnimationGroup):
        return [mob for inner in animation.animations
                for mob in _removed_by(inner)]
    return [animation.mobject] if animation.is_remover() else []
