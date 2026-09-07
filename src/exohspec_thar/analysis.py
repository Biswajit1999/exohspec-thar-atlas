"""Exposure comparison, privacy-safe crops, and HDR combination."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np

from .fits import open_raw_primary, robust_background, scale_array, summarize_frame


@dataclass(frozen=True)
class ExposureResult:
    exposure_seconds: float
    background_adu: float
    background_sigma_adu: float
    full_scale_pixels: int
    bright_pixels: int
    display_role: str


def _role(seconds: float, ordered_seconds: list[float]) -> str:
    if seconds == min(ordered_seconds):
        return "protects bright line cores"
    if seconds == max(ordered_seconds):
        return "reveals faint structure"
    if seconds == sorted(ordered_seconds)[-2]:
        return "best single-frame balance"
    return "bridges bright and faint regimes"


def _locate_public_crop(reference_path: Path) -> tuple[slice, slice]:
    """Find a padded crop around the luminous spectral format.

    The returned crop is used internally only. Published images use normalized
    coordinates and intentionally omit detector dimensions and pixel positions.
    """

    with open_raw_primary(reference_path) as (raw, header):
        background, sigma = robust_background(raw, header)
        threshold = background + max(250.0, 25.0 * sigma)
        image = scale_array(raw, header)
        bright_y, bright_x = np.nonzero(image > threshold)
        if bright_x.size < 50:
            raise RuntimeError("Could not locate enough bright spectral pixels")

        # Percentiles reject isolated hot pixels and cosmic-ray events.
        x0, x1 = np.quantile(bright_x, [0.03, 0.97]).astype(int)
        y0, y1 = np.quantile(bright_y, [0.01, 0.99]).astype(int)
        x_pad = max(64, int((x1 - x0) * 0.16))
        y_pad = max(64, int((y1 - y0) * 0.04))
        x_slice = slice(max(0, x0 - x_pad), min(raw.shape[1], x1 + x_pad + 1))
        y_slice = slice(max(0, y0 - y_pad), min(raw.shape[0], y1 + y_pad + 1))
        return y_slice, x_slice


def _load_crop(path: Path, crop: tuple[slice, slice]) -> tuple[np.ndarray, float, float, float]:
    with open_raw_primary(path) as (raw, header):
        background, sigma = robust_background(raw, header)
        seconds = float(header.get("EXPTIME", header.get("EXPOSURE")))
        return scale_array(raw[crop], header), seconds, background, sigma


def _hdr_rate(paths: list[Path], crop: tuple[slice, slice]) -> tuple[np.ndarray, list[float]]:
    """Combine frames into an unsaturated signal-rate image.

    The longest exposure supplies faint structure. Pixels approaching full scale
    are replaced by progressively shorter exposures. Values are ADU/s above each
    frame's robust pedestal; no absolute radiometric calibration is implied.
    """

    loaded = [_load_crop(path, crop) for path in paths]
    loaded.sort(key=lambda item: item[1], reverse=True)
    result = np.full(loaded[0][0].shape, np.nan, dtype=np.float32)
    chosen = np.zeros(result.shape, dtype=bool)
    used: list[float] = []

    for image, seconds, background, _sigma in loaded:
        valid = np.isfinite(image) & (image < 60000.0) & ~chosen
        signal_rate = np.maximum(image - background, 0.0) / seconds
        result[valid] = signal_rate[valid]
        chosen |= valid
        used.append(seconds)

    result[~np.isfinite(result)] = 0.0
    return result, used


def _asinh_display(image: np.ndarray, upper_percentile: float = 99.8) -> np.ndarray:
    finite = image[np.isfinite(image)]
    low = float(np.percentile(finite, 15.0))
    high = float(np.percentile(finite, upper_percentile))
    scaled = np.clip((image - low) / max(high - low, 1e-6), 0.0, None)
    return np.arcsinh(7.0 * scaled) / np.arcsinh(7.0)


def _save_image(image: np.ndarray, path: Path, label: str) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 10.0), constrained_layout=True)
    ax.imshow(_asinh_display(image), origin="lower", aspect="auto", cmap="magma")
    ax.set_axis_off()
    ax.text(
        0.035,
        0.025,
        label,
        transform=ax.transAxes,
        color="white",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.45", "facecolor": "#090b12dd", "edgecolor": "#ffffff33"},
    )
    fig.savefig(path, dpi=150, facecolor="#090b12")
    plt.close(fig)


def _save_exposure_chart(results: list[ExposureResult], path: Path) -> None:
    seconds = np.array([item.exposure_seconds for item in results])
    bright = np.array([item.bright_pixels for item in results])
    full = np.array([item.full_scale_pixels for item in results])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.2), constrained_layout=True)
    fig.patch.set_facecolor("#0b0d14")
    for ax in (ax1, ax2):
        ax.set_facecolor("#111520")
        ax.tick_params(colors="#cbd5e1")
        for spine in ax.spines.values():
            spine.set_color("#334155")
        ax.grid(axis="y", color="#334155", alpha=0.5, linewidth=0.7)
    ax1.plot(seconds, bright, "o-", color="#f2bd58", linewidth=2.2, markersize=7)
    ax1.set(xlabel="Exposure (s)", ylabel="Bright pixels in public crop", title="Faint structure grows")
    ax2.plot(seconds, full, "o-", color="#fb7185", linewidth=2.2, markersize=7)
    ax2.set(xlabel="Exposure (s)", ylabel="Full-scale pixels (whole frame)", title="Bright cores reach the ceiling")
    for ax in (ax1, ax2):
        ax.xaxis.label.set_color("#e2e8f0")
        ax.yaxis.label.set_color("#e2e8f0")
        ax.title.set_color("#f8fafc")
    fig.savefig(path, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def build_public_products(input_paths: Iterable[str | Path], output_root: str | Path) -> list[ExposureResult]:
    """Build privacy-reviewed web data and figures from local FITS paths."""

    paths = [Path(path).expanduser().resolve() for path in input_paths]
    if len(paths) < 2:
        raise ValueError("At least two exposure files are required for comparison")
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"Missing input files: {missing}")

    output_root = Path(output_root).resolve()
    assets = output_root / "web" / "assets"
    data_dir = output_root / "web" / "data"
    derived = output_root / "data" / "derived"
    for directory in (assets, data_dir, derived):
        directory.mkdir(parents=True, exist_ok=True)

    summaries = [(path, summarize_frame(path)) for path in paths]
    summaries.sort(key=lambda pair: pair[1].exposure_seconds)
    ordered_seconds = [summary.exposure_seconds for _, summary in summaries]
    reference = summaries[-1][0]
    crop = _locate_public_crop(reference)

    results: list[ExposureResult] = []
    images: dict[float, np.ndarray] = {}
    for path, summary in summaries:
        image, seconds, background, sigma = _load_crop(path, crop)
        images[seconds] = image
        bright_threshold = background + max(100.0, 15.0 * sigma)
        results.append(
            ExposureResult(
                exposure_seconds=seconds,
                background_adu=round(background, 2),
                background_sigma_adu=round(sigma, 2),
                full_scale_pixels=summary.full_scale_pixels,
                bright_pixels=int(np.count_nonzero(image > bright_threshold)),
                display_role=_role(seconds, ordered_seconds),
            )
        )

    single_seconds = sorted(ordered_seconds)[-2]
    single = images[single_seconds]
    single_background = next(item.background_adu for item in results if item.exposure_seconds == single_seconds)
    _save_image(
        np.maximum(single - single_background, 0.0),
        assets / "spectral-format.webp",
        f"Measured Th–Ar format · {single_seconds:g} s",
    )

    hdr, used = _hdr_rate([path for path, _ in summaries], crop)
    _save_image(hdr, assets / "hdr-spectrum.webp", "HDR composite · signal rate")
    _save_exposure_chart(results, assets / "exposure-study.png")

    public_payload = {
        "schema_version": 1,
        "instrument": "EXOhSPEC",
        "detector": "ZWO CMOS detector",
        "calibration_source": "thorium–argon hollow-cathode lamp",
        "recommended_single_exposure_seconds": single_seconds,
        "hdr_exposures_seconds": sorted(used),
        "coordinate_policy": "normalized public crop; raw detector geometry withheld",
        "wavelength_status": "not yet calibrated; detector features are not atomic identifications",
        "exposures": [asdict(item) for item in results],
    }
    (data_dir / "summary.json").write_text(json.dumps(public_payload, indent=2) + "\n", encoding="utf-8")

    with (derived / "exposure-summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=asdict(results[0]).keys())
        writer.writeheader()
        writer.writerows(asdict(item) for item in results)

    return results

