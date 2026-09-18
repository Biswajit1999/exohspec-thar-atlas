# Limitations and boundary of inference

- Only one measured frame exists at each exposure duration; fixed-duration
  repeatability and temporal lamp evolution cannot be estimated.
- The public derivatives deliberately omit raw FITS data, full headers, exact
  detector geometry, and private laboratory details.
- The measured candidates have no validated order trace, dispersion solution,
  wavelength, or atomic identity.
- The response analysis assumes stable lamp output over the acquisition
  sequence and uses a global robust pedestal rather than a local scattered-light
  model.
- Registration models a global translation only. Rotation, scale, local
  distortion, and estimator uncertainty are not measured.
- The 60,000 ADU threshold is an operational diagnostic, not an independently
  measured detector-linearity boundary.
- The injection-recovery study uses isolated Gaussian features. It omits
  blending, empirical line-spread asymmetry, gain uncertainty, cosmic rays,
  spatially varying backgrounds, and non-linearity below the hard ceiling.
- Simulation errors remain in pixels. Converting them to wavelength or velocity
  would require a validated, public dispersion model and would overstate the
  current evidence.

The next decisive experiment is a repeated measured exposure ladder with
empirical profile injection, local background fitting, and a blinded held-out
line set after wavelength calibration.
