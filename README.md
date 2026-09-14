# Sound Machines

*The art, science and history of music technology, told from the signal's point of view.*

This repository is the lab. Every figure, sound and line of code behind an
essay is produced here. The published essays live on Ghost; this repo also
renders a local Quarto site for previewing an essay as one page before it is
pasted into Ghost.

## Layout

```
_quarto.yml            Quarto website config (local preview only)
pressmark.scss         vendored Pressmark theme — do not edit
signal.scss            our additions (the "Follow the signal" block style)
index.qmd              timeline front page (sortable by milestone year / publish date)
sm/                    shared Python package: audio I/O, plotting, later DSP
ghost/
  code-injection.html  canonical copy of the Ghost site-header injection
milestones/
  _metadata.yml        settings shared by every essay
  NN-slug/
    index.qmd          the essay (narrative beats + signal blocks)
    ghost-post.md      paste guide for the Ghost editor
    notes.md           research session output
    sources.bib        references, cited with [@key]
    model/             the DSP model, plain functions on numpy arrays
    out/audio/         rendered sounds
    out/figs/          rendered figures
NEXT.md                the single next action, written at the end of every session
```

## Setup (once)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt      # also installs sm/ in editable mode
quarto check jupyter                 # Quarto must see the venv's python
```

If `quarto check` picks up the wrong Python, run `quarto` from a shell where
the venv is activated, or set `QUARTO_PYTHON=.venv/bin/python`.

## Everyday commands

```bash
quarto preview                        # live-reloading local site
quarto render                         # render everything to _site/
python milestones/00-test-post/model/ping.py   # regenerate one model's outputs
```

Executed cells are cached in `_freeze/`; commit it. To force one essay to
re-execute, delete its folder under `_freeze/milestones/`.

## Starting a new milestone

Copy `milestones/00-test-post` to `milestones/NN-slug`, replace the front
matter, and delete the placeholder prose. The six narrative beats and the
three signal blocks stay.
