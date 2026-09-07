# EXOhSPEC Th–Ar Atlas

A privacy-aware, reproducible look at four thorium–argon hollow-cathode lamp
exposures recorded with EXOhSPEC and a ZWO CMOS detector. The project is written
for a general audience while keeping the scientific boundary clear: detector
features are not assigned atomic wavelengths until a wavelength solution has
been validated.

## What the supplied data show

- **120 s is the best single-frame compromise.** It reveals substantially more
  faint structure than 30–60 s while clipping fewer bright cores than 180 s.
- **30 s protects the strongest line cores.** It is the preferred source when
  longer frames approach the detector ceiling.
- **180 s reaches faint structure.** It is useful where the corresponding pixels
  remain unsaturated.
- **The strongest public image is an HDR composite.** The pipeline uses the
  longest valid exposure pixel by pixel and falls back to shorter frames near
  full scale.

These are detector-level conclusions. They do not replace bias/dark/flat
calibration, radiometric calibration, or a wavelength solution; those topics are
deliberately outside this public-facing release.

## Reproduce the derived products

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python scripts/build_products.py path/to/ThAr_30sec.fit path/to/ThAr_60sec.fit \
  path/to/ThAr_120sec.fit path/to/ThAr_180sec.fit --output-root .
pytest
```

Serve the data story locally:

```bash
python -m http.server 8000 --directory web
```

Then visit `http://localhost:8000`.

## Repository map

```text
src/exohspec_thar/   FITS reading, safe summaries, crop detection, HDR builder
scripts/             source-checkout command-line entry point
tests/               numerical and privacy-contract tests
data/raw/            ignored local input area
data/derived/        privacy-reviewed scalar table
web/                 static, GitHub Pages-ready public story
docs/                method, privacy boundary, and scientific sources
```

## Scientific scope

This release answers one focused question: how do 30, 60, 120, and 180 second
exposures trade bright-line headroom against faint-line visibility? A later
release may add atomic labels only after order tracing and a validated
pixel-to-wavelength model are available.

## Acknowledgements

The EXOhSPEC work was supervised by **Prof. Hugh Jones** (EXOhSPEC research) and
**Prof. Bill Martin** (optics and laboratory) at the University of Hertfordshire.

Analysis and public communication: **Biswajit Jana**.

## License and data

Code and original explanatory text are released under the MIT License. Raw
laboratory FITS files are intentionally excluded. NIST atomic data and linked
papers retain their own terms and should be cited directly.

