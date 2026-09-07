"""Higher-level, detector-domain diagnostics for the technical report.

Nothing in this module assigns wavelengths or atomic species. The output is a
quantitative assessment of the exposure ladder and image stability only.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import binary_dilation, gaussian_filter, gaussian_filter1d, maximum_filter
from scipy.signal import find_peaks

from .analysis import _hdr_rate, _locate_public_crop, _load_crop


@dataclass(frozen=True)
class ScienceMetrics:
    exposure_seconds: list[float]
    background_adu: list[float]
    background_sigma_adu: list[float]
    bright_pixel_count: list[int]
    near_ceiling_pixel_count: list[int]
    normalized_integrated_signal: list[float]
    linearity_r_squared: float
    linearity_max_fractional_residual: float
    registration_shift_relative_to_120_px: list[list[float]]
    registration_max_magnitude_px: float
    hdr_fallback_pixel_count: dict[str, int]
    candidate_feature_count: int
    caveat: str


def _subpixel_peak(values: np.ndarray, index: int) -> float:
    """Parabolic interpolation around a wrapped correlation maximum."""

    left = float(values[(index - 1) % values.size])
    centre = float(values[index])
    right = float(values[(index + 1) % values.size])
    denominator = left - 2.0 * centre + right
    return 0.0 if abs(denominator) < 1e-12 else 0.5 * (left - right) / denominator


def _registration_shift(reference: np.ndarray, moving: np.ndarray, block: int = 4) -> tuple[float, float]:
    """Estimate translational offset with phase correlation on binned log images."""

    height = min(reference.shape[0], moving.shape[0]) // block * block
    width = min(reference.shape[1], moving.shape[1]) // block * block

    def prepare(image: np.ndarray) -> np.ndarray:
        clipped = np.clip(image[:height, :width], 0.0, None)
        pooled = clipped.reshape(height // block, block, width // block, block).mean(axis=(1, 3))
        transformed = np.log1p(pooled)
        return transformed - np.mean(transformed)

    ref = prepare(reference)
    mov = prepare(moving)
    cross = np.fft.fft2(ref) * np.conj(np.fft.fft2(mov))
    cross /= np.maximum(np.abs(cross), 1e-12)
    correlation = np.abs(np.fft.ifft2(cross))
    iy, ix = np.unravel_index(int(np.argmax(correlation)), correlation.shape)
    dy = float(iy) + _subpixel_peak(correlation[:, ix], int(iy))
    dx = float(ix) + _subpixel_peak(correlation[iy, :], int(ix))
    if dy > correlation.shape[0] / 2:
        dy -= correlation.shape[0]
    if dx > correlation.shape[1] / 2:
        dx -= correlation.shape[1]
    return dy * block, dx * block


def _candidate_peaks(hdr: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return separated local maxima for morphology statistics, not line IDs."""

    smooth = gaussian_filter(hdr, sigma=1.2)
    positive = smooth[smooth > 0]
    threshold = float(np.percentile(positive, 99.65))
    local = smooth == maximum_filter(smooth, size=11, mode="nearest")
    local &= smooth >= threshold
    local[:6, :] = False
    local[-6:, :] = False
    local[:, :6] = False
    local[:, -6:] = False
    y, x = np.nonzero(local)
    intensity = smooth[y, x]
    order = np.argsort(intensity)[::-1][:500]
    return y[order], x[order], intensity[order]


def _save_ladder(
    exposures: np.ndarray,
    signals: list[np.ndarray],
    output: Path,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 12.5), constrained_layout=True)
    all_rate = np.concatenate([(signal / exposure)[::8, ::8].ravel() for signal, exposure in zip(signals, exposures)])
    high = float(np.percentile(all_rate, 99.85))
    for ax, exposure, signal in zip(axes.flat, exposures, signals):
        rate = np.maximum(signal / exposure, 0.0)
        display = np.arcsinh(6 * np.clip(rate / max(high, 1e-6), 0, None)) / np.arcsinh(6)
        ax.imshow(display, origin="lower", aspect="auto", cmap="gray", vmin=0, vmax=1)
        ax.set_title(f"{exposure:g} s", loc="left", color="#102f52", fontsize=15, fontweight="bold")
        ax.set_axis_off()
    fig.suptitle("One spectral format, four exposure times", color="#102f52", fontsize=21, fontweight="bold")
    fig.patch.set_facecolor("white")
    fig.savefig(output, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def _style_axis(ax: plt.Axes) -> None:
    ax.set_facecolor("white")
    ax.tick_params(colors="#344357")
    ax.xaxis.label.set_color("#142033")
    ax.yaxis.label.set_color("#142033")
    ax.title.set_color("#102f52")
    for spine in ax.spines.values():
        spine.set_color("#9aa8b7")
    ax.grid(color="#dce2e8", alpha=0.9, linewidth=0.7)


def _save_diagnostics(metrics: ScienceMetrics, output: Path) -> None:
    x = np.asarray(metrics.exposure_seconds)
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), constrained_layout=True)
    fig.patch.set_facecolor("white")
    for ax in axes.flat:
        _style_axis(ax)

    axes[0, 0].plot(x, metrics.background_adu, "o-", color="#67d9e8", lw=2.2)
    axes[0, 0].set(title="Detector pedestal", xlabel="Exposure (s)", ylabel="Median background (ADU)")

    axes[0, 1].plot(x, metrics.bright_pixel_count, "o-", color="#f2bd58", lw=2.2)
    axes[0, 1].set(title="Visible structure", xlabel="Exposure (s)", ylabel="Pixels > 100 ADU above pedestal")

    axes[1, 0].plot(x, metrics.near_ceiling_pixel_count, "o-", color="#fb7185", lw=2.2)
    axes[1, 0].set(title="Near-ceiling population", xlabel="Exposure (s)", ylabel="Pixels at or above 60,000 ADU")

    y = np.asarray(metrics.normalized_integrated_signal)
    axes[1, 1].plot(x, y, "o", color="#f2bd58", ms=7, label="measured")
    slope = float(np.dot(x, y) / np.dot(x, x))
    axes[1, 1].plot(x, slope * x, "--", color="#536174", label="through-origin fit")
    axes[1, 1].set(title="Integrated unsaturated response", xlabel="Exposure (s)", ylabel="Signal relative to 30 s")
    axes[1, 1].legend(frameon=False, labelcolor="#142033")

    fig.savefig(output, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def _save_registration(metrics: ScienceMetrics, output: Path) -> None:
    shifts = np.asarray(metrics.registration_shift_relative_to_120_px)
    x = np.arange(len(metrics.exposure_seconds))
    width = 0.36
    fig, ax = plt.subplots(figsize=(9.5, 4.8), constrained_layout=True)
    fig.patch.set_facecolor("white")
    _style_axis(ax)
    ax.bar(x - width / 2, shifts[:, 1], width, label="x shift", color="#67d9e8")
    ax.bar(x + width / 2, shifts[:, 0], width, label="y shift", color="#f2bd58")
    ax.axhline(0, color="#536174", lw=0.8)
    ax.set_xticks(x, [f"{v:g} s" for v in metrics.exposure_seconds])
    ax.set(title="Frame registration relative to 120 s", ylabel="Estimated translation (native pixels)")
    ax.legend(frameon=False, labelcolor="#142033")
    fig.savefig(output, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def _save_peak_map(
    hdr: np.ndarray,
    peaks: tuple[np.ndarray, np.ndarray, np.ndarray],
    output: Path,
) -> None:
    y, x, intensity = peaks
    sample = hdr[::8, ::8]
    high = float(np.percentile(sample, 99.85))
    display = np.arcsinh(6 * np.clip(hdr / max(high, 1e-6), 0, None)) / np.arcsinh(6)
    fig, ax = plt.subplots(figsize=(7.6, 10.5), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#08111e")
    ax.imshow(display, origin="lower", aspect="auto", cmap="gray", vmin=0, vmax=1)
    sizes = 18 + 55 * np.sqrt(intensity / max(float(np.max(intensity)), 1e-6))
    ax.scatter(x, y, s=sizes, facecolors="none", edgecolors="#67d9e8", linewidths=0.55, alpha=0.8)
    ax.set(xlim=(0, hdr.shape[1]), ylim=(0, hdr.shape[0]))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Morphological candidates - not atomic identifications", color="#102f52", fontsize=15)
    fig.savefig(output, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


def _save_annotated_detector(hdr: np.ndarray, output: Path) -> None:
    """Explain the measured detector view without inventing an order or wavelength solution."""

    sample = hdr[::8, ::8]
    high = float(np.percentile(sample, 99.82))
    display = np.arcsinh(9 * np.clip(hdr / max(high, 1e-6), 0, None)) / np.arcsinh(9)
    height, width = hdr.shape
    fig, ax = plt.subplots(figsize=(8.5, 10.8), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.imshow(display, origin="lower", aspect="auto", cmap="gray", vmin=0, vmax=1)
    ax.set_facecolor("#08111e")
    note = dict(boxstyle="round,pad=0.35", fc="white", ec="#102f52", alpha=0.95)
    arrow = dict(arrowstyle="->", color="#18a7b5", lw=1.8)
    ax.annotate(
        "Bright compact features\n(emission-line images)",
        xy=(0.56 * width, 0.48 * height), xytext=(0.70 * width, 0.62 * height),
        color="#102f52", fontsize=10, bbox=note, arrowprops=arrow,
    )
    ax.annotate(
        "High-signal feature:\ncheck for saturation", 
        xy=(0.34 * width, 0.73 * height), xytext=(0.05 * width, 0.84 * height),
        color="#102f52", fontsize=10, bbox=note, arrowprops=arrow,
    )
    ax.annotate(
        "Diffuse/background structure\nis measured and subtracted", 
        xy=(0.86 * width, 0.68 * height), xytext=(0.58 * width, 0.91 * height),
        color="#102f52", fontsize=10, bbox=note, arrowprops=arrow,
    )
    ax.annotate(
        "Repeated curved loci are candidate\nechelle traces; numbering requires tracing", 
        xy=(0.66 * width, 0.28 * height), xytext=(0.05 * width, 0.15 * height),
        color="#102f52", fontsize=10, bbox=note, arrowprops=arrow,
    )
    ax.set_xlabel("Detector x coordinate (cropped; pixel values intentionally omitted)")
    ax.set_ylabel("Detector y coordinate (cropped; pixel values intentionally omitted)")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("How to read the measured EXOhSPEC Th-Ar detector frame", fontsize=16, color="#102f52")
    fig.savefig(output, dpi=190, facecolor="white")
    plt.close(fig)


def _save_emission_absorption_concept(output: Path) -> None:
    """Make an explicitly conceptual comparison for a general audience."""

    wavelength = np.linspace(400.0, 700.0, 2400)
    centres = np.asarray([427.0, 451.0, 486.0, 516.0, 546.0, 577.0, 612.0, 650.0, 680.0])
    strengths = np.asarray([0.35, 0.58, 0.42, 0.72, 1.0, 0.48, 0.62, 0.84, 0.40])
    emission = np.full_like(wavelength, 0.035)
    absorption = 0.82 + 0.05 * np.sin((wavelength - 400.0) / 42.0)
    for centre, strength in zip(centres, strengths):
        profile = np.exp(-0.5 * ((wavelength - centre) / 0.9) ** 2)
        emission += strength * profile
        absorption -= 0.48 * strength * profile

    fig, axes = plt.subplots(2, 1, figsize=(11, 6.8), sharex=True, constrained_layout=True)
    fig.patch.set_facecolor("white")
    for ax in axes:
        _style_axis(ax)
        ax.set_ylim(0, 1.12)
        ax.set_ylabel("Relative intensity")
    axes[0].plot(wavelength, emission, color="#c56820", lw=1.7)
    axes[0].fill_between(wavelength, emission, 0, color="#f3c49e", alpha=0.35)
    axes[0].set_title("Emission spectrum: narrow peaks added by excited atoms and ions", loc="left")
    axes[0].annotate("emission line", xy=(546, 1.03), xytext=(565, 0.82), arrowprops=dict(arrowstyle="->", color="#102f52"))
    axes[1].plot(wavelength, absorption, color="#1e5e91", lw=1.7)
    axes[1].fill_between(wavelength, absorption, 0, color="#c9ddec", alpha=0.38)
    axes[1].set_title("Absorption spectrum: narrow deficits removed from a continuum", loc="left")
    axes[1].annotate("absorption line", xy=(650, float(absorption[np.argmin(abs(wavelength - 650))])), xytext=(610, 0.28), arrowprops=dict(arrowstyle="->", color="#102f52"))
    axes[1].set_xlabel("Illustrative wavelength (nm) - conceptual, not an EXOhSPEC calibration")
    fig.suptitle("Emission and absorption are opposite signatures", fontsize=17, color="#102f52", fontweight="bold")
    fig.savefig(output, dpi=190, facecolor="white")
    plt.close(fig)


def _representative_profiles(
    exposures: np.ndarray,
    signals: list[np.ndarray],
    hdr: np.ndarray,
) -> tuple[np.ndarray, dict[str, np.ndarray], list[tuple[str, np.ndarray]]]:
    """Extract one comparable band and three illustrative detector-space bands."""

    positive = hdr[hdr > 0]
    feature_threshold = float(np.percentile(positive, 98.7))
    # Count significant structure rather than ranking rows by one dominant peak.
    # This favours bands that visually resemble a line forest.
    row_power = gaussian_filter1d(np.sum(hdr > feature_threshold, axis=1).astype(float), sigma=3.0)
    minimum_distance = max(25, hdr.shape[0] // 35)
    candidates, _ = find_peaks(row_power, distance=minimum_distance, prominence=np.std(row_power))
    if candidates.size < 3:
        candidates = np.argsort(row_power)[-3:]
    selected = candidates[np.argsort(row_power[candidates])[-3:]][::-1]

    half_width = max(3, hdr.shape[0] // 1200)

    def extract(image: np.ndarray, centre: int) -> np.ndarray:
        band = image[max(0, centre - half_width) : centre + half_width + 1]
        profile = np.sum(np.clip(band, 0.0, None), axis=0)
        return gaussian_filter1d(profile, sigma=1.1)

    strongest = int(selected[0])
    comparison = {
        f"{exposure:g} s": extract(signal / exposure, strongest)
        for exposure, signal in zip(exposures, signals)
    }
    comparison["HDR"] = extract(hdr, strongest)
    illustrative = [(f"Band {chr(65 + index)}", extract(hdr, int(centre))) for index, centre in enumerate(selected)]

    width = hdr.shape[1]
    target = min(900, width)
    edges = np.linspace(0, width, target + 1, dtype=int)

    def compress(values: np.ndarray) -> np.ndarray:
        return np.asarray([np.mean(values[edges[i] : edges[i + 1]]) for i in range(target)])

    comparison = {key: compress(value) for key, value in comparison.items()}
    illustrative = [(key, compress(value)) for key, value in illustrative]
    coordinate = (np.arange(target) + 0.5) / target
    scale = max(float(np.percentile(comparison["HDR"], 99.7)), 1e-8)
    comparison = {key: np.clip(value / scale, 0.0, 1.35) for key, value in comparison.items()}
    illustrative = [
        (key, np.clip(value / max(float(np.percentile(value, 99.7)), 1e-8), 0.0, 1.2))
        for key, value in illustrative
    ]
    return coordinate, comparison, illustrative


def _save_profiles(
    coordinate: np.ndarray,
    illustrative: list[tuple[str, np.ndarray]],
    output: Path,
) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(11, 7.8), sharex=True, constrained_layout=True)
    fig.patch.set_facecolor("white")
    colors = ["#163a63", "#b45309", "#0f766e"]
    for ax, (label, values), color in zip(axes, illustrative, colors):
        display_values = np.arcsinh(28.0 * values) / np.arcsinh(28.0)
        ax.plot(coordinate, display_values, color=color, lw=1.05)
        ax.fill_between(coordinate, display_values, color=color, alpha=0.12)
        ax.set_ylabel("Asinh-scaled\nintensity")
        ax.text(0.012, 0.86, label, transform=ax.transAxes, fontsize=10, fontweight="bold")
        ax.grid(color="#cbd5e1", linewidth=0.65, alpha=0.75)
        ax.spines[["top", "right"]].set_visible(False)
        ax.set_ylim(0, 1.12)
    axes[-1].set_xlabel("Normalized detector coordinate along representative band")
    fig.suptitle("Representative extracted detector-space profiles", fontsize=17, fontweight="bold")
    fig.savefig(output, dpi=190, facecolor="white")
    plt.close(fig)


def build_science_products(input_paths: Iterable[str | Path], output_root: str | Path) -> ScienceMetrics:
    paths = [Path(path).expanduser().resolve() for path in input_paths]
    if len(paths) != 4:
        raise ValueError("This report expects the four supplied exposure files")

    exposure_path: list[tuple[float, Path]] = []
    for path in paths:
        _image, seconds, _background, _sigma = _load_crop(path, (slice(0, 1), slice(0, 1)))
        exposure_path.append((seconds, path))
    exposure_path.sort()
    paths = [item[1] for item in exposure_path]

    crop = _locate_public_crop(paths[-1])
    loaded = [_load_crop(path, crop) for path in paths]
    exposures = np.asarray([item[1] for item in loaded])
    backgrounds = np.asarray([item[2] for item in loaded])
    sigmas = np.asarray([item[3] for item in loaded])
    images = [item[0] for item in loaded]
    signals = [image - background for image, background in zip(images, backgrounds)]

    # A common mask isolates real lamp structure while avoiding pixels that
    # approach the ceiling in any exposure. Dilation captures each feature's PSF.
    reference_rate = np.maximum(signals[-1], 0.0) / exposures[-1]
    source_mask = reference_rate > 0.65
    source_mask = binary_dilation(source_mask, iterations=2)
    unsaturated_mask = source_mask.copy()
    for image in images:
        unsaturated_mask &= image < 55000.0

    integrated = np.asarray([
        float(np.sum(np.maximum(signal[unsaturated_mask], 0.0))) for signal in signals
    ])
    normalized = integrated / integrated[0]
    slope = float(np.dot(exposures, normalized) / np.dot(exposures, exposures))
    fitted = slope * exposures
    residuals = normalized - fitted
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((normalized - np.mean(normalized)) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    reference_index = int(np.where(exposures == 120.0)[0][0])
    reference = np.maximum(signals[reference_index], 0.0)
    shifts = [list(_registration_shift(reference, np.maximum(signal, 0.0))) for signal in signals]
    shift_magnitudes = [float(np.hypot(*shift)) for shift in shifts]

    hdr, _used = _hdr_rate(paths, crop)
    peak_tuple = _candidate_peaks(hdr)

    fallback: dict[str, int] = {}
    still_unassigned = np.ones(images[0].shape, dtype=bool)
    for image, exposure in reversed(list(zip(images, exposures))):
        assigned = still_unassigned & (image < 60000.0)
        fallback[f"{exposure:g}"] = int(np.count_nonzero(assigned & source_mask))
        still_unassigned &= ~assigned

    metrics = ScienceMetrics(
        exposure_seconds=[float(value) for value in exposures],
        background_adu=[round(float(value), 3) for value in backgrounds],
        background_sigma_adu=[round(float(value), 3) for value in sigmas],
        bright_pixel_count=[int(np.count_nonzero(signal > 100.0)) for signal in signals],
        near_ceiling_pixel_count=[int(np.count_nonzero(image >= 60000.0)) for image in images],
        normalized_integrated_signal=[round(float(value), 5) for value in normalized],
        linearity_r_squared=round(float(r_squared), 6),
        linearity_max_fractional_residual=round(float(np.max(np.abs(residuals / fitted))), 6),
        registration_shift_relative_to_120_px=[[round(float(v), 3) for v in pair] for pair in shifts],
        registration_max_magnitude_px=round(max(shift_magnitudes), 3),
        hdr_fallback_pixel_count=fallback,
        candidate_feature_count=int(len(peak_tuple[0])),
        caveat="Detector-domain analysis only; candidates are not wavelength-calibrated atomic lines.",
    )

    root = Path(output_root).resolve()
    figures = root / "report" / "figures"
    data_dir = root / "report" / "data"
    figures.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    _save_ladder(exposures, signals, figures / "exposure-ladder.png")
    _save_diagnostics(metrics, figures / "detector-diagnostics.png")
    _save_registration(metrics, figures / "registration-shifts.png")
    _save_peak_map(hdr, peak_tuple, figures / "candidate-feature-map.png")
    coordinate, comparison, illustrative = _representative_profiles(exposures, signals, hdr)
    _save_profiles(coordinate, illustrative, figures / "representative-profiles.png")
    web_assets = root / "web" / "assets"
    web_assets.mkdir(parents=True, exist_ok=True)
    for name in (
        "exposure-ladder.png",
        "detector-diagnostics.png",
        "registration-shifts.png",
        "candidate-feature-map.png",
        "representative-profiles.png",
    ):
        shutil.copy2(figures / name, web_assets / name)
    web_profile_payload = {
        "axis": "normalized detector coordinate; not wavelength calibrated",
        "intensity": "relative signal rate",
        "coordinate": [round(float(value), 6) for value in coordinate],
        "series": {
            key: [round(float(value), 6) for value in values]
            for key, values in comparison.items()
        },
    }
    (root / "web" / "data" / "spectrum-profiles.json").write_text(
        json.dumps(web_profile_payload, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    web_assets = root / "web" / "assets"
    web_assets.mkdir(parents=True, exist_ok=True)
    for name in (
        "detector-diagnostics.png",
        "registration-shifts.png",
        "representative-profiles.png",
    ):
        shutil.copy2(figures / name, web_assets / name)
    metrics_payload = json.dumps(asdict(metrics), indent=2) + "\n"
    (data_dir / "science-metrics.json").write_text(metrics_payload, encoding="utf-8")
    (root / "web" / "data" / "science-metrics.json").write_text(
        metrics_payload, encoding="utf-8"
    )
    return metrics
