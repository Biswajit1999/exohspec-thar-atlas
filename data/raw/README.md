# Local raw data

Place the exposure FITS files here only on a trusted workstation. Files matching
`*.fit`, `*.fits`, and `*.fts` are ignored by Git and must not be committed.

The public build reads only exposure time from each header and exports derived,
cropped, normalized products. It does not copy complete FITS headers.

