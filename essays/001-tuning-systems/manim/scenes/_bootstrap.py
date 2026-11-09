"""Put the project root on ``sys.path`` so scenes can import ``common``.

Manim adds the scene file's own folder (``scenes/``) to the import path,
but not the project root. Importing this module first fixes that, so
both ``manim scenes/<file>.py`` and ``python render.py`` work without
installing anything::

    import _bootstrap  # noqa: F401  # isort: skip
    from common import EssayScene
"""

import sys
from pathlib import Path

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
