# Piano samples

Salamander Grand Piano V3, a Yamaha C5 recorded by Alexander Holm,
licensed under Creative Commons Attribution 3.0 (see `LICENSE.txt`).
Source: <https://github.com/sfzinstruments/SalamanderGrandPiano>.

**Credit required:** any published video that uses these sounds must
credit "Salamander Grand Piano by Alexander Holm (CC BY 3.0)", for
example in the description or end credits.

These files are velocity layer 10 (mezzo-forte), one note every minor
third from A0 to C8, trimmed to 8 s and stored as 16-bit FLAC.
`manifest.tsv` lists each sample's measured fundamental: the piano is
stretch-tuned like any real piano (A0 about 25 cents flat, C8 about 40
cents sharp), and `common.audio.Piano` uses the measured values to land
on exact frequencies. Regenerate everything with
`python tools/import_piano_samples.py`.
