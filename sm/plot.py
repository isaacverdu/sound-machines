"""Plotting helpers. Each function returns the matplotlib Figure so the
caller can save it or let Quarto display it inline.

Importing this module also puts every figure on the site palette — see
SITE_STYLE below.
"""

import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

# The site palette, kept in step with palette.scss / pressmark.scss.
PAGE = "#f0eee7"  # $primary-color   — the page itself
PANEL = "#e6e3d7"  # $primary-color-shade — cards, code, "Follow the signal"
INK = "#1b1b1b"  # $font-color
ACCENT = "#990f3d"  # $highlight-color
MUTED = "#7d7a72"  # ink, dialled back for axes and ticks

SITE_STYLE = {
    # A figure can land on the page or inside a deeper "Follow the signal"
    # panel, and the plotting code has no way of knowing which. Transparent
    # means it does not have to: whatever is behind it shows through, and a
    # later change of palette needs no change here. PAGE and PANEL are still
    # exported above for the odd figure that has to paint its own background.
    "figure.facecolor": "none",
    "figure.edgecolor": "none",
    "axes.facecolor": "none",
    "savefig.facecolor": "none",
    "savefig.edgecolor": "none",
    "savefig.transparent": True,
    # Text wears the body ink rather than the colour of the data.
    "text.color": INK,
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "xtick.labelcolor": INK,
    "ytick.labelcolor": INK,
    # Frame and ticks recede: keep the two spines that carry a scale, drop the
    # two that only draw a box.
    "axes.edgecolor": MUTED,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "grid.color": MUTED,
    "grid.alpha": 0.25,
    # These are single-series plots, so the one series wears the site accent
    # and the figure needs no legend — the caption names what it shows.
    "axes.prop_cycle": cycler(color=[ACCENT, INK, MUTED]),
}

plt.rcParams.update(SITE_STYLE)


def waveform(y, fs=44_100, t_max=None, title=None):
    """Time-domain plot of a signal. ``t_max`` (seconds) crops the x-axis."""
    y = np.asarray(y)
    t = np.arange(len(y)) / fs
    if t_max is not None:
        n = int(t_max * fs)
        t, y = t[:n], y[:n]
    fig, ax = plt.subplots(figsize=(8, 2.6))
    ax.plot(t, y, linewidth=0.8)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("amplitude")
    if title:
        ax.set_title(title)
    ax.margins(x=0)
    fig.tight_layout()
    return fig


def spectrum(y, fs=44_100, f_max=None, title=None, db=True):
    """Magnitude spectrum of a signal via a single FFT of the whole thing."""
    y = np.asarray(y)
    Y = np.fft.rfft(y * np.hanning(len(y)))
    f = np.fft.rfftfreq(len(y), 1 / fs)
    mag = np.abs(Y) / len(y)
    if db:
        mag = 20 * np.log10(mag + 1e-12)
        mag -= mag.max()
    fig, ax = plt.subplots(figsize=(8, 2.6))
    ax.plot(f, mag, linewidth=0.8)
    ax.set_xlabel("frequency (Hz)")
    ax.set_ylabel("magnitude (dB)" if db else "magnitude")
    if f_max is not None:
        ax.set_xlim(0, f_max)
    if db:
        ax.set_ylim(-100, 3)
    if title:
        ax.set_title(title)
    fig.tight_layout()
    return fig
