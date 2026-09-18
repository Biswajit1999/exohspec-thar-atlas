# Claims register

| Claim | Evidence | Scope | Excluded interpretation |
|---|---|---|---|
| The measured exposure sequence is close to proportional on a common unsaturated mask. | `report/data/science-metrics.json`: R² = 0.999276; maximum fractional residual = 0.01994. | Four frames under one acquisition sequence. | A full detector-linearity calibration. |
| Global translations are at most 0.071 pixel under the implemented estimator. | Phase-correlation result in `report/data/science-metrics.json`. | Translation-only comparison after block averaging. | A complete stability or uncertainty budget. |
| Pixelwise HDR reduces strong-feature centroid RMSE by 83.9% in the controlled study. | 7,000 strong-feature injections in `results/centroid-recovery/report.json`. | Seeded isolated-Gaussian detector simulation using published relative strengths. | Measured EXOhSPEC wavelength or radial-velocity precision. |
| Pixelwise HDR does not degrade the faint-feature result in this study. | HDR/fixed-180 faint-feature RMSE ratio = 1.000 across 12,000 injections. | The committed forward model and thresholds. | General performance for arbitrary lamps, detectors, blends, or backgrounds. |
| L01–L24 are reproducible detector-feature identifiers. | `data/derived/measured-line-candidates-120s.csv`. | Public normalized detector coordinates. | Atomic identifications or wavelengths. |

Every numerical claim must point to a committed generated result. The project
does not claim a wavelength solution, resolving power, absolute flux scale,
atomic identification of measured candidates, or instrument radial-velocity
precision.
