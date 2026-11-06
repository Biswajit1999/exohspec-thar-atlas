# Pixel-integrated centroid information (2026-11-03)

Independent detector-domain synthetic sensitivity checks, without changing the privacy-reviewed FITS products or the existing injection–recovery study.

A Gaussian profile is integrated over pixel width using midpoint quadrature. A finite-difference centroid derivative yields a conditional Gaussian-variance Fisher bound. Independent exposure information is summed while masking expected pixels above a selectable ceiling. Five tests cover area conservation, shot-noise exposure scaling, independent-exposure information additivity, saturation monotonicity, and invalid inputs.

Reproduce from repository root: `python -m pytest -q tests/test_centroid_information.py`.

Illustrative synthetic example: Gaussian sigma 1.2 px, total rate 100 counts/s, 30 s exposure, background 2 counts/s/pixel gives a conditional centroid bound of 0.026084 px. A separate synthetic 30+180 s ladder at 800 counts/s with a 30000-count ceiling gives 0.003505 px and 39 retained pixel-exposure samples. These are not observations or validated detector noise parameters.

Assumptions: independent Poisson-like pixels, background rate known, read noise in count units, fixed-variance Fisher approximation, stable source profile and independent frames. Saturation is treated as an exclusion mask rather than a censored-likelihood model. No wavelength solution, spectral-line species assignment, or EXOhSPEC radial-velocity precision is inferred.
