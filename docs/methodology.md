# Methodology

## Question

Which of the supplied 30, 60, 120, and 180 second Th–Ar exposures best balances
faint-feature visibility against bright-feature saturation?

## Safe ingestion

The primary two-dimensional image is memory-mapped. Only `EXPTIME` (or the
equivalent `EXPOSURE`) is allowed into a derived public product. The complete
header is neither copied nor serialized.

Unsigned 16-bit FITS images may be represented as signed integers with `BZERO`
and `BSCALE`; the reader explicitly applies that linear transform to arrays and
crops used for analysis.

## Background and display

The pedestal is the median of a sparse, full-frame sample. Scatter is estimated
as `1.4826 × median absolute deviation`. This robust statistic is useful for
diagnosis but is not presented as a full detector-noise model.

The public crop is located from bright pixels in the longest exposure. Coordinate
percentiles reject isolated detector events, and padding preserves context. The
published view has no raw pixel axes. An inverse-hyperbolic-sine stretch makes
faint and bright features visible together; it is a display transform, not a
linear intensity scale.

## HDR rule

For each pixel in the public crop:

1. subtract the robust pedestal for that exposure;
2. divide by exposure time to obtain a relative signal rate;
3. use the longest exposure below 60,000 ADU;
4. fall back to progressively shorter exposures near the detector ceiling.

The result is a relative detector signal-rate image. It is not a calibrated flux
map.

## Interpretation boundary

The present release compares exposure behavior. It does not identify atomic
transitions. A defensible line identification requires traced spectral orders,
an initial dispersion model, matching to a reference list, rejection of blends,
and residual validation. Until those steps exist, the page calls features
“emission features” or “detector peaks,” not named Th I, Th II, or Ar I lines.

