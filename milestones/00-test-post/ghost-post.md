# Ghost paste guide — 00 test post

Follow top to bottom. Each section says which editor card to use. The
narrative goes in as ordinary text; every signal block is one **HTML card**
(type `/html` on an empty line). Figures are **image cards**, sounds are
**audio cards**.

Before starting, make sure `ghost/code-injection.html` has been pasted into
Settings → Code injection → Site header, and that
`python model/ping.py` has been run so `out/` contains the files below.

---

## Title / excerpt / settings

- **Title:** Test post: every element in one place
- **Excerpt (post settings):** A pipeline check, not a milestone.
- **Tag:** `meta`
- **Feature image:** `out/figs/ping-waveform.png` (optional)

---

## Callout card (`/callout`)

> This post exists to test the publishing pipeline. Every element below is
> one a real essay will use. Unpublish it once essay 01 is live.

---

## Text — beat 1

Type the heading as a normal H2 (`## ` shortcut works in the editor).

**A room, a sound, a date**

Stanford, late 1982. A terminal, a loudspeaker, and two students who have
found that a few dozen memory locations and a single averaging instruction
produce something that sounds unmistakably like a plucked string.

This is **beat one, the cold open**: a scene, a sound, a moment. *Italics*
and **bold** are fine here. Ghost has no footnotes, so a footnote becomes a
parenthetical or a short sentence at the end of the paragraph.

---

## Text — beat 2

**What couldn't be done**

Beat two states the problem. Before this milestone, what was impossible, or
too expensive, or too slow? What did musicians do instead?

Ghost has no margin column either. A margin note becomes an *italic
one-liner paragraph* directly after the paragraph it belongs to, or is cut.

---

## HTML card — block A

```html
<div class="signal">
  <p class="signal-label">Follow the signal</p>
  <p><strong>Block A — the signal before.</strong> A signal block answers the
  one question the narrative just raised, then stops. Text is visible; code is
  shown in full (Ghost can't fold it, so keep it short). Here the question is
  "what does a simple tone even look like?", so we make one.</p>
<pre><code class="language-python">from ping import ping
from sm import FS, io, plot

y = ping()                                   # the model
io.write_wav("out/audio/ping.wav", y)        # keep the artifact on disk
plot.waveform(y, t_max=0.02)</code></pre>
</div>
```

Then, directly below the HTML card:

- **Image card:** upload `out/figs/ping-waveform.png`, caption *"The first 20 ms of a decaying two-partial tone: a fundamental at 440 Hz plus a quieter partial at 1320 Hz."*
- **Audio card:** upload `out/audio/ping.wav`, title *"ping"*.

(Image and audio cards sit *between* HTML cards rather than inside them so
Ghost hosts the files and the email version shows the image. The CSS margins
make the sequence read as one block. If you'd rather keep everything in one
card, upload the files first and use `<img src="…">` / `<audio controls src="…">`
with the URLs Ghost gives you.)

---

## Text — beat 3

**The insight**

Beat three is the idea in plain words, and the audio-critical paragraph. If a
listener hears only this section, they should still come away knowing *why*
the milestone worked. No equations.

Then a **quote card** (`/quote`):

> A blockquote for a primary-source line, a quote from the inventor, or an
> advertisement of the period.

---

## HTML card — block B (math and a table)

Underscores inside `$…$` are safe in an HTML card because the editor does
not Markdown-parse HTML cards. This is the reason math always goes in a card,
never in a text paragraph.

```html
<div class="signal">
  <p class="signal-label">Follow the signal</p>
  <p><strong>Block B — the mechanism.</strong> Inline math: the fundamental
  period is $T = 1/f_0$, and the sample delay that produces it is
  $N = f_s / f_0$. Display math gets its own line:</p>
  <p>$$ y[n] = e^{-\alpha n / f_s}\,\big(\sin(2\pi f_0 n / f_s) + 0.3\,\sin(2\pi\,3 f_0\, n / f_s)\big) $$</p>
  <table>
    <thead><tr><th>parameter</th><th>value</th><th>meaning</th></tr></thead>
    <tbody>
      <tr><td>$f_0$</td><td>440 Hz</td><td>fundamental</td></tr>
      <tr><td>$\alpha$</td><td>4 /s</td><td>decay rate</td></tr>
      <tr><td>$f_s$</td><td>44.1 k</td><td>sample rate</td></tr>
    </tbody>
  </table>
</div>
```

Then an **image card:** `out/figs/ping-spectrum.png`, caption *"Magnitude
spectrum of the tone. Two peaks, as promised by the equation."*

---

## Text — beat 4

**The people and the machine**

Beat four is the story proper: who, where, with what constraints, and what
went wrong first. Usually the longest beat.

---

## HTML card — block C (code only)

```html
<div class="signal">
  <p class="signal-label">Follow the signal</p>
  <p><strong>Block C — the detail that makes it sound right.</strong> The
  tweak the inventors found, or the one everyone gets wrong.</p>
<pre><code class="language-python">def one_pole_lowpass(x, a=0.5):
    y = np.zeros_like(x)
    for n in range(1, len(x)):
        y[n] = (1 - a) * x[n] + a * y[n - 1]
    return y</code></pre>
</div>
```

---

## Text — beats 5 and 6

**What it changed**

Beat five: the records, the imitators, the descendants. Concrete names and
years.

**Coda**

Beat six returns to the cold open with one image to leave on. Short.

---

## Text — footer

*Run it yourself:* the model and outputs for this post live in
`milestones/00-test-post` of the Sound Machines repository. (Link it.)

**Sources**

Karplus, K. and Strong, A. (1983). "Digital Synthesis of Plucked-String and
Drum Timbres." *Computer Music Journal* 7(2), 43–55.

---

## What to check after publishing

- [ ] Inline and display math render inside the HTML cards
- [ ] Python is highlighted
- [ ] Signal blocks show the left rule and small-caps label (code injection working)
- [ ] Audio card plays
- [ ] **Email preview:** the narrative reads cleanly with the blocks stripped or degraded
- [ ] Mobile width: the table and code block don't overflow
- [ ] Note anything tedious in `NEXT.md` — that list is the spec for the push script later
