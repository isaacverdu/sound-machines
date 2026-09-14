"""Sound Machines shared library.

Every essay's model imports from here so that helpers accumulate in one place.
This package is the seed of the software arm: keep functions small, pure, and
operating on plain numpy arrays.
"""

from . import io, plot  # noqa: F401

FS = 44_100  # default sample rate in Hz
