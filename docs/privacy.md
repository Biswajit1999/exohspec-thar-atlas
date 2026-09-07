# Public-release privacy boundary

## Public

- Instrument name: EXOhSPEC
- Detector family: ZWO CMOS detector
- Lamp type: thorium–argon hollow-cathode lamp
- Exposure times: 30, 60, 120, and 180 seconds
- Cropped, normalized, derived figures
- Scalar exposure diagnostics required to explain the conclusion

## Withheld

- Exact detector model, serial identifiers, gain/offset settings, and temperature
- Raw FITS files and full FITS headers
- Absolute detector geometry and pixel-coordinate axes
- Optical layout, alignments, laboratory configuration, and file-system paths
- Observer/location metadata and unrelated calibration frames

The pipeline enforces a two-key header allow-list and the repository ignores raw
FITS extensions. Before publication, `git ls-files` and a text search for local
paths, email addresses, serial-like fields, and forbidden header names should be
part of the release check.

