"""Small, deliberate FITS helpers.

The public pipeline reads only the primary image and a tiny allow-list of header
fields. It never serializes the input header. This matters because astronomical
headers may contain observer, location, hardware, or filesystem information.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np
from astropy.io import fits


PUBLIC_HEADER_ALLOWLIST = frozenset({"EXPTIME", "EXPOSURE"})


@dataclass(frozen=True)
class FrameSummary:
    """Privacy-reviewed statistics for one exposure."""

    exposure_seconds: float
    background_adu: float
    background_sigma_adu: float
    maximum_adu: float
    full_scale_pixels: int


@contextmanager
def open_raw_primary(path: str | Path) -> Iterator[tuple[np.ndarray, fits.Header]]:
    """Memory-map the unscaled primary image.

    Unsigned 16-bit FITS data are commonly stored as signed int16 plus BZERO.
    ``do_not_scale_image_data`` keeps the array memory-mappable; ``scale_array``
    applies the FITS linear transform only to the requested array or crop.
    """

    with fits.open(
        Path(path),
        mode="readonly",
        memmap=True,
        do_not_scale_image_data=True,
    ) as hdul:
        if hdul[0].data is None or hdul[0].data.ndim != 2:
            raise ValueError(f"Expected one 2-D primary image: {path}")
        yield hdul[0].data, hdul[0].header


def scale_array(raw: np.ndarray, header: fits.Header) -> np.ndarray:
    """Apply BSCALE/BZERO and return float32 ADU values."""

    bscale = float(header.get("BSCALE", 1.0))
    bzero = float(header.get("BZERO", 0.0))
    return raw.astype(np.float32) * bscale + bzero


def exposure_seconds(header: fits.Header) -> float:
    """Read exposure time from the only two header keys allowed downstream."""

    value = header.get("EXPTIME", header.get("EXPOSURE"))
    if value is None:
        raise ValueError("FITS primary header has no EXPTIME or EXPOSURE value")
    seconds = float(value)
    if not np.isfinite(seconds) or seconds <= 0:
        raise ValueError(f"Invalid exposure time: {value!r}")
    return seconds


def robust_background(raw: np.ndarray, header: fits.Header, stride: int = 32) -> tuple[float, float]:
    """Estimate the frame pedestal and robust scatter from a sparse sample."""

    sample = scale_array(raw[::stride, ::stride], header)
    median = float(np.nanmedian(sample))
    mad = float(np.nanmedian(np.abs(sample - median)))
    return median, 1.4826 * mad


def summarize_frame(path: str | Path) -> FrameSummary:
    """Calculate safe scalar diagnostics without copying the header."""

    with open_raw_primary(path) as (raw, header):
        background, sigma = robust_background(raw, header)
        bscale = float(header.get("BSCALE", 1.0))
        bzero = float(header.get("BZERO", 0.0))
        raw_max = int(np.max(raw))
        maximum = raw_max * bscale + bzero
        count_at_max = int(np.count_nonzero(raw == raw_max))
        return FrameSummary(
            exposure_seconds=exposure_seconds(header),
            background_adu=background,
            background_sigma_adu=sigma,
            maximum_adu=float(maximum),
            full_scale_pixels=count_at_max if maximum >= 65535 else 0,
        )

