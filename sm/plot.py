"""Plotting helpers. Each function returns the matplotlib Figure so the
caller can save it or let Quarto display it inline."""

import matplotlib.pyplot as plt
import numpy as np


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
