# Thorium-Argon Spectral Lines: A Scientific Guide and FITS Example

[![Scientific report](https://img.shields.io/badge/live-scientific_report-102f52)](https://biswajit1999.github.io/exohspec-thar-atlas/)
[![Publish scientific report](https://github.com/Biswajit1999/exohspec-thar-atlas/actions/workflows/pages.yml/badge.svg)](https://github.com/Biswajit1999/exohspec-thar-atlas/actions/workflows/pages.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-1e5e91)
[![MIT License](https://img.shields.io/badge/license-MIT-c56820)](LICENSE)

A general-audience scientific guide to thorium-argon hollow-cathode spectra,
supported by privacy-reviewed FITS examples recorded during practical work on
the EXOhSPEC project. It explains how the lamp works, why its bright features
are emission lines, how thorium and argon contribute, and why astronomers use
the pattern as a wavelength reference. Detector features are not assigned
atomic wavelengths until a wavelength solution has been validated.

**[Open the interactive scientific report →](https://biswajit1999.github.io/exohspec-thar-atlas/)**

![Measured EXOhSPEC Th-Ar spectral format with provisional dispersion and cross-dispersion directions](web/assets/detector-orientation.png)

The image above is a privacy-reviewed derivative of the measured exposure set,
rotated into a conventional landscape presentation. The wavelength-increase
direction remains intentionally unassigned until a trace and dispersion solution
are validated.

## Why this repository exists

Thorium-argon hollow-cathode lamps are dense emission-line references used to
calibrate astronomical spectrographs. Argon ions sustain a discharge and sputter
thorium from the cathode. Excited neutral and ionized thorium and argon then emit
photons at discrete wavelengths. A calibrated pattern can act as a wavelength
ruler; an uncalibrated detector image cannot yet support atomic labels.

The project began with a simple question after recording several lamp spectra:
what are all these bright lines, and how do they work? It connects that question
to a real EXOhSPEC exposure sequence. It
explains emission versus absorption, detector dispersion and cross-dispersion,
dynamic-range selection, HDR composition, line morphology, reference-list
matching, wavelength-solution validation, abundance, applications, and the
limits of inference from uncalibrated FITS frames.

## Contents

- [Measured exposure findings](#what-the-supplied-data-show)
- [Quantitative results](#quantitative-results)
- [Scientific products](#scientific-products)
- [Reproduce the analysis](#reproduce-the-derived-products)
- [Privacy and interpretation boundary](#scientific-scope)
- [Acknowledgements](#acknowledgements)

## What the supplied data show

- **120 s is the best single-frame compromise.** It reveals substantially more
  faint structure than 30-60 s while preserving more bright-core headroom than
  180 s.
- **30 s protects the strongest line cores.** It is the preferred source when
  longer frames approach the detector ceiling.
- **180 s reaches faint structure.** It is useful where the corresponding pixels
  remain unsaturated.
- **The strongest public image is an HDR composite.** The pipeline uses the
  longest valid exposure pixel by pixel and falls back to shorter frames near
  full scale.

These are detector-level conclusions. They do not replace a complete
calibration and extraction chain or a wavelength solution.

## Quantitative results

| Exposure | Median background | Robust sigma | Bright pixels | Pixels >= 60,000 ADU | Signal / 30 s |
|---:|---:|---:|---:|---:|---:|
| 30 s | 502 ADU | 2.965 ADU | 6,267 | 1 | 1.00000 |
| 60 s | 504 ADU | 4.448 ADU | 10,906 | 15 | 1.97961 |
| 120 s | 505 ADU | 4.448 ADU | 17,998 | 75 | 4.01202 |
| 180 s | 508 ADU | 4.448 ADU | 26,132 | 121 | 5.84104 |

The common unsaturated response has **R2 = 0.999276** under a through-origin
fit, with a maximum fractional residual of **1.994%**. Translation-only phase
correlation estimates a maximum displacement of **0.071 native pixel** relative
to the 120 s frame. These are detector-domain diagnostics, not a complete camera
linearity or spectrograph stability budget.

## Read the project

- [Live scientific website](https://biswajit1999.github.io/exohspec-thar-atlas/)
- [Detailed technical report](report/technical-report.md)
- [Publication-ready PDF](output/pdf/exohspec-thar-detector-study.pdf)
- [Methodology](docs/methodology.md) and [privacy boundary](docs/privacy.md)
- [AI illustration prompts and disclosure](docs/image-prompts.md)

## Scientific products

- a rotated, zoomed-out detector overview with provisional dispersion and
  cross-dispersion directions;
- an annotated measured frame explaining emission-line images, diffuse
  background, candidate order loci, and high-signal regions;
- an interactive detector-coordinate spectrum for 30, 60, 120, 180 s, and HDR;
- light-background plots of pedestal, visible structure, near-ceiling pixels,
  exposure response, registration, and representative profiles;
- a detailed explanation of Th I-III and Ar I-III, blends, saturation, line
  centroids, the instrumental profile, reference matching, and validation;
- clearly labelled AI-generated conceptual illustrations of the lamp and
  discharge process, kept separate from measured evidence;
- a reproducible Python pipeline and privacy-contract tests.

## Reproduce the derived products

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python scripts/build_products.py path/to/ThAr_30sec.fit path/to/ThAr_60sec.fit \
  path/to/ThAr_120sec.fit path/to/ThAr_180sec.fit --output-root .
python scripts/build_science_report.py path/to/ThAr_30sec.fit path/to/ThAr_60sec.fit \
  path/to/ThAr_120sec.fit path/to/ThAr_180sec.fit --output-root .
python scripts/build_explanatory_figures.py
python scripts/build_pdf_report.py
pytest
```

Serve the data story locally:

```bash
python -m http.server 8000 --directory web
```

Then visit `http://localhost:8000`.

## Repository map

```text
src/exohspec_thar/   FITS reading, safe summaries, HDR, diagnostics
scripts/             product, figure, science-report, and PDF builders
tests/               numerical and privacy-contract tests
data/raw/            ignored local input area
data/derived/        privacy-reviewed scalar table
web/                 static GitHub Pages scientific report
report/              detailed narrative, metrics, and publication figures
docs/                method, privacy, sources, and AI prompt disclosure
```

## Reusable README / project prompt

> Create a research-grade GitHub README for an astronomical thorium-argon
> calibration project. Lead with the scientific question and measured result,
> distinguish raw detector data from conceptual illustrations, explain
> hollow-cathode emission, Th I-III and Ar I-III notation, echelle dispersion
> and cross-dispersion, line centroids, blends, saturation, reference matching,
> wavelength-model validation, limitations, privacy boundaries, reproduction
> commands, citations, and acknowledgements. Include a quantitative results
> table, live-report link, repository map, and explicit warning not to assign
> wavelengths before a validated solution. Use a restrained light scientific
> style and searchable terminology without marketing exaggeration.

## Scientific scope

This release answers one focused question: how do 30, 60, 120, and 180 second
exposures trade bright-line headroom against faint-line visibility? A later
release may add atomic labels only after order tracing and a validated
pixel-to-wavelength model are available.

NIST SRD 161 is the authoritative reference source for such matching. Its atlas
contains more than 20,000 thorium reference wavelengths across multiple
Fourier-transform spectra; the database does not automatically identify spots
in this detector image.

### Public

- exposure times and privacy-reviewed aggregate measurements;
- normalized detector coordinates and derived visual products;
- generic EXOhSPEC and ZWO CMOS-family descriptions;
- reproducible analysis code.

### Intentionally private

- raw FITS files and full headers;
- exact detector geometry, serial information, and settings;
- optical prescriptions and laboratory layout;
- local paths and unrelated calibration material.

## Conceptual artwork disclosure

The lamp and discharge-process illustrations are AI generated and are labelled
as conceptual wherever they appear. They are not observations, engineering
drawings, or inputs to the analysis. The prompts are preserved in
[docs/image-prompts.md](docs/image-prompts.md). Every spectrum, detector image,
metric, and diagnostic plot presented as measured evidence comes from the
supplied FITS exposure sequence.

## Acknowledgements

During practical laboratory work on the EXOhSPEC project, **Biswajit Jana**
recorded several thorium-argon spectra and became interested in what the bright
lines represent, how they are produced, and why they are useful. That curiosity
led to this analysis and educational report. The author gratefully acknowledges
**Prof. Hugh Jones** for supervision of the EXOhSPEC work and **Prof. Bill
Martin** for guidance and supervision during the optics laboratory work at the
University of Hertfordshire.

## Citation, license, and data

Citation metadata are provided in [CITATION.cff](CITATION.cff). Code and original
explanatory text are released under the MIT License. Raw laboratory FITS files
are intentionally excluded. NIST atomic data and linked papers retain their own
terms and should be cited directly.
