# Multi-exposure centroid injection–recovery study

## Research question

Can the existing 30, 60, 120, and 180 second exposure ladder preserve the
centroids of strong Th–Ar features better than a single 180 second exposure,
without degrading faint-feature recovery?

The study tests a detector-domain algorithm. It does **not** infer a wavelength
solution, identify atomic transitions, or estimate EXOhSPEC radial-velocity
precision.

## Predeclared hypothesis

The null hypothesis states that pixelwise HDR reduces strong-line centroid RMSE
by less than 50% relative to a fixed 180 second exposure. It is rejected when
the relative reduction is at least 0.50. A separate guardrail requires the
faint-line HDR/fixed-180 RMSE ratio to remain at or below 1.10.

## Design

- The 24 privacy-reviewed measured candidates provide feature identifiers,
  relative peak strengths, and reproducible sub-pixel phases.
- Each feature receives 1,000 seeded injections: 24,000 injections in total.
- The forward model is an isolated Gaussian detector feature with 1.15 pixel
  sigma, signal shot noise, the measured 4.45 ADU background scatter, a 65,535
  ADU hard ceiling, and the analysis pipeline's 60,000 ADU selection ceiling.
- Four estimators are compared on the same realizations: fixed 120 seconds,
  fixed 180 seconds, the longest wholly unsaturated exposure, and pixelwise
  HDR selection.
- Strong features have measured relative peak signal at least 0.8; faint
  features have relative peak signal at most 0.12. These boundaries are stored
  in code and are not selected from the outcome.

The configuration is committed in
[`research/centroid-recovery-config.json`](../research/centroid-recovery-config.json).
The implementation is
[`src/exohspec_thar/centroid_recovery.py`](../src/exohspec_thar/centroid_recovery.py).

## Results

| Strength band | Estimator | Injections | Bias (px) | RMSE (px) |
|---|---|---:|---:|---:|
| All | fixed 120 s | 24,000 | -0.000475 | 0.009671 |
| All | fixed 180 s | 24,000 | -0.000639 | 0.008338 |
| All | longest unsaturated | 24,000 | -0.000026 | 0.004849 |
| All | pixelwise HDR | 24,000 | -0.000022 | 0.004675 |
| Strong | fixed 180 s | 7,000 | -0.002136 | 0.012954 |
| Strong | longest unsaturated | 7,000 | -0.000056 | 0.003082 |
| Strong | pixelwise HDR | 7,000 | -0.000021 | 0.002086 |
| Faint | fixed 180 s | 12,000 | -0.000043 | 0.005834 |
| Faint | pixelwise HDR | 12,000 | -0.000043 | 0.005834 |

Pixelwise HDR reduces strong-feature RMSE by **83.9%**, so the predeclared null
is rejected. The faint-feature RMSE ratio is **1.000**, satisfying the guardrail.
Across all features, pixelwise HDR reduces RMSE by **43.9%** relative to the
fixed 180 second strategy.

Machine-readable results are committed in
[`results/centroid-recovery`](../results/centroid-recovery). Regenerate them
with:

```bash
python scripts/run_centroid_recovery.py
```

## Interpretation

The controlled result supports the exposure-ladder algorithmic design: shorter
frames preserve information in saturated cores while the longest valid frame
retains faint wings. It does not prove that the same numerical improvement
occurs in the private FITS frames. A measured validation requires repeat
exposures, local background models, empirical line-spread functions, blends,
cosmic rays, gain calibration, and a traced wavelength solution.

This distinction matters because Th–Ar lines span a large intensity range and
line selection is instrument- and exposure-specific. Murphy et al. (2007) and
Lovis & Pepe (2007) both motivate careful rejection or treatment of saturated,
blended, and otherwise unreliable calibration features.

## Limitations

1. The forward model uses isolated symmetric Gaussian lines; real line-spread
   functions may be asymmetric or blended.
2. Relative peak values set scenario amplitudes but are not treated as an
   absolute detector calibration.
3. The measured background scatter is used as a constant Gaussian term; gain,
   dark current, non-linearity below saturation, and spatially varying
   backgrounds are not inferred.
4. Sub-pixel phases are deterministic transformations of normalized public
   coordinates, not recovered private pixel positions.
5. Pixel errors are not converted to wavelength or velocity because no
   validated dispersion solution is public.
6. The 24 labelled candidates were selected for readable display and are not a
   random sample of all detector features.

## References

- Lovis, C. & Pepe, F. (2007), *A new list of thorium and argon spectral
  lines in the visible*, A&A 468, 1115–1121,
  <https://doi.org/10.1051/0004-6361:20077249>.
- Murphy, M. T. et al. (2007), *Selection of ThAr lines for wavelength
  calibration of echelle spectra*, MNRAS 378, 221–230,
  <https://doi.org/10.1111/j.1365-2966.2007.11768.x>.
- Redman, S. L., Nave, G. & Sansonetti, C. J. (2014), *The Spectrum of
  Thorium from 250 nm to 5500 nm*, ApJS 211(1),
  <https://doi.org/10.1088/0067-0049/211/1/4>.
