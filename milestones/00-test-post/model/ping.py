"""Test model for the pipeline: a decaying two-partial tone.

Not a real milestone. It exists so the essay template has something to
execute, plot and play. Run it directly to regenerate the outputs:

    python model/ping.py
"""

from pathlib import Path

import numpy as np

from sm import FS, io, plot

HERE = Path(__file__).resolve().parent.parent  # the milestone folder


def ping(f0=440.0, duration=1.5, decay=4.0, fs=FS):
    """A fundamental plus a quieter partial at 3*f0, both decaying exponentially.

    y[n] = e^{-decay * t} * ( sin(2 pi f0 t) + 0.3 sin(2 pi 3 f0 t) )
    """
    t = np.arange(int(duration * fs)) / fs
    env = np.exp(-decay * t)
    y = env * (np.sin(2 * np.pi * f0 * t) + 0.3 * np.sin(2 * np.pi * 3 * f0 * t))
    return y


if __name__ == "__main__":
    y = ping()
    io.write_wav(HERE / "out/audio/ping.wav", y)
    plot.waveform(y, t_max=0.02, title="ping — first 20 ms").savefig(HERE / "out/figs/ping-waveform.png")
    plot.spectrum(y, f_max=3000, title="ping — spectrum").savefig(HERE / "out/figs/ping-spectrum.png")
    print("wrote out/audio/ping.wav, out/figs/ping-*.png")
