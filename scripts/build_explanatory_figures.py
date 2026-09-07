"""Build light-theme explanatory figures from privacy-reviewed derivatives."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exohspec_thar.science import (  # noqa: E402
    ScienceMetrics,
    _save_annotated_detector,
    _save_diagnostics,
    _save_emission_absorption_concept,
    _save_registration,
)


def _save_orientation_figure(display_image: np.ndarray, output: Path) -> None:
    """Rotate the public derivative and explain the two detector directions."""

    oriented = np.rot90(display_image, k=1)
    fig, ax = plt.subplots(figsize=(12.5, 6.8), constrained_layout=True)
    fig.patch.set_facecolor("white")
    ax.imshow(oriented, cmap="gray", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(
        "Provisional orientation of the measured EXOhSPEC spectral format",
        color="#102f52",
        fontsize=17,
        fontweight="bold",
    )
    box = dict(boxstyle="round,pad=0.4", fc="white", ec="#102f52", alpha=0.94)
    arrow = dict(arrowstyle="-|>", color="#18a7b5", lw=2.4)
    ax.annotate(
        "Dispersion direction\n(along a traced order)",
        xy=(0.72, 0.13), xytext=(0.20, 0.13),
        xycoords="axes fraction", textcoords="axes fraction",
        color="#102f52", fontsize=11, bbox=box, arrowprops=arrow,
        ha="center", va="center",
    )
    ax.annotate(
        "Cross-dispersion\n(between neighbouring orders)",
        xy=(0.88, 0.58), xytext=(0.88, 0.20),
        xycoords="axes fraction", textcoords="axes fraction",
        color="#102f52", fontsize=11, bbox=box, arrowprops=arrow,
        ha="center", va="center",
    )
    ax.text(
        0.02, 0.96,
        "Display rotation only; the sign of increasing wavelength is not assigned",
        transform=ax.transAxes, va="top", color="#102f52", fontsize=10, bbox=box,
    )
    fig.savefig(output, dpi=190, facecolor="white")
    plt.close(fig)


def main() -> None:
    figures = ROOT / "report" / "figures"
    web_assets = ROOT / "web" / "assets"
    figures.mkdir(parents=True, exist_ok=True)
    web_assets.mkdir(parents=True, exist_ok=True)

    # This display-ready image is already a privacy-reviewed derivative of the
    # measured HDR signal-rate product; no raw FITS header or geometry is used.
    with Image.open(web_assets / "hdr-spectrum.webp") as source:
        grayscale_top_origin = np.asarray(source.convert("L"), dtype=np.float32) / 255.0
    # Remove the embedded display label and convert top-origin raster rows to
    # the lower-origin detector convention used by the annotation routine.
    grayscale_top_origin = grayscale_top_origin[:-90, :]
    grayscale = np.flipud(grayscale_top_origin)

    _save_annotated_detector(grayscale, figures / "annotated-detector-map.png")
    _save_orientation_figure(grayscale_top_origin, figures / "detector-orientation.png")
    _save_emission_absorption_concept(figures / "emission-vs-absorption.png")

    payload = json.loads((ROOT / "report" / "data" / "science-metrics.json").read_text(encoding="utf-8"))
    metrics = ScienceMetrics(**payload)
    _save_diagnostics(metrics, figures / "detector-diagnostics.png")
    _save_registration(metrics, figures / "registration-shifts.png")

    for name in (
        "annotated-detector-map.png",
        "detector-orientation.png",
        "emission-vs-absorption.png",
        "detector-diagnostics.png",
        "registration-shifts.png",
    ):
        shutil.copy2(figures / name, web_assets / name)

    plt.close("all")


if __name__ == "__main__":
    main()
