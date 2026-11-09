"""Render essay scenes with consistent settings.

Usage (from this folder)::

    python render.py 01                 # final 1080p30 -> renders/
    python render.py 01 --draft         # quick 540p15 preview
    python render.py 01 --quality 4k    # 2160p30
    python render.py all                # every scene, in order
    python render.py 01 --stills 3.5 20 # also save PNGs at those seconds

Scenes are the files ``scenes/sNN_<name>.py``; select them by number
(``01``) or name (``introduction``). Each finished video, with its
narration mixed in, is copied to ``renders/sNN_<name>.mp4``. Still
times are seconds into the rendered video, which starts with the
scene's blank lead-in (0.5 s by default).
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import av

ROOT = Path(__file__).resolve().parent
SCENES_DIR = ROOT / "scenes"
MEDIA_DIR = ROOT / "media"
RENDERS_DIR = ROOT / "renders"

QUALITIES = {
    "draft": (960, 540, 15),
    "final": (1920, 1080, 30),
    "4k": (3840, 2160, 30),
}


def scene_files(selection: str) -> list[Path]:
    """Scene files matching a number, a name fragment, or ``all``."""
    files = sorted(SCENES_DIR.glob("s[0-9][0-9]_*.py"))
    if selection != "all":
        key = selection.lower().removeprefix("s")
        files = [path for path in files
                 if path.stem[1:3] == key.zfill(2) or key in path.stem]
    if not files:
        sys.exit(f"No scene matches '{selection}' in {SCENES_DIR}")
    return files


def render(path: Path, width: int, height: int, fps: int) -> Path:
    """Render every scene class in ``path``; return the newest video."""
    command = [
        sys.executable, "-m", "manim", "render",
        "-r", f"{width},{height}",
        "--fps", str(fps),
        "--media_dir", str(MEDIA_DIR),
        "--verbosity", "WARNING",
        "-a",
        str(path.relative_to(ROOT)),
    ]
    print(" ".join(command[1:]))
    subprocess.run(command, cwd=ROOT, check=True)
    folder = MEDIA_DIR / "videos" / path.stem / f"{height}p{fps}"
    videos = sorted(folder.glob("*.mp4"), key=lambda p: p.stat().st_mtime)
    if not videos:
        sys.exit(f"Manim produced no video in {folder}")
    return videos[-1]


def save_stills(video: Path, times: list[float], folder: Path) -> None:
    """Save the frames nearest to ``times`` (seconds) as PNG files."""
    folder.mkdir(parents=True, exist_ok=True)
    pending = sorted(times)
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        half_frame = 0.5 / float(stream.base_rate)
        for frame in container.decode(stream):
            while pending and frame.time >= pending[0] - half_frame:
                moment = pending.pop(0)
                target = folder / f"{video.stem}_{moment:06.2f}s.png"
                frame.to_image().save(target)
                print(f"still  {target.relative_to(ROOT)}")
            if not pending:
                break


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render essay scenes.",
        epilog="Example: python render.py 01 --draft --stills 4 12.5")
    parser.add_argument("scene", help="scene number, name, or 'all'")
    parser.add_argument("--quality", choices=QUALITIES, default="final")
    parser.add_argument("--draft", action="store_true",
                        help="shortcut for --quality draft")
    parser.add_argument("--stills", type=float, nargs="+", default=[],
                        metavar="SECONDS",
                        help="also save frames at these video times")
    args = parser.parse_args()

    width, height, fps = QUALITIES["draft" if args.draft else args.quality]
    RENDERS_DIR.mkdir(exist_ok=True)
    for path in scene_files(args.scene):
        video = render(path, width, height, fps)
        suffix = "" if (width, height) == QUALITIES["final"][:2] else (
            f"_{height}p")
        target = RENDERS_DIR / f"{path.stem}{suffix}.mp4"
        shutil.copyfile(video, target)
        print(f"video  {target.relative_to(ROOT)}")
        if args.stills:
            save_stills(target, args.stills, RENDERS_DIR / "stills")


if __name__ == "__main__":
    main()
