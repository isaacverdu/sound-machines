"""Filesystem locations shared by scenes, components and tools."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
NARRATION_DIR = ASSETS_DIR / "narration"
