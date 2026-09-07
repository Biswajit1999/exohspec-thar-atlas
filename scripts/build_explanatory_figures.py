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


def main() -> None:
    figures = ROOT / "report" / "figures"
    web_assets = ROOT / "web" / "assets"
    figures.mkdir(parents=True, exist_ok=True)
    web_assets.mkdir(parents=True, exist_ok=True)

    # This display-ready image is already a privacy-reviewed derivative of the
    # measured HDR signal-rate product; no raw FITS header or geometry is used.
    with Image.open(web_assets / "hdr-spectrum.webp") as source:
        grayscale = np.asarray(source.convert("L"), dtype=np.float32) / 255.0
    # Remove the embedded display label and convert top-origin raster rows to
    # the lower-origin detector convention used by the annotation routine.
    grayscale = np.flipud(grayscale[:-90, :])

    _save_annotated_detector(grayscale, figures / "annotated-detector-map.png")
    _save_emission_absorption_concept(figures / "emission-vs-absorption.png")

    payload = json.loads((ROOT / "report" / "data" / "science-metrics.json").read_text(encoding="utf-8"))
    metrics = ScienceMetrics(**payload)
    _save_diagnostics(metrics, figures / "detector-diagnostics.png")
    _save_registration(metrics, figures / "registration-shifts.png")

    for name in (
        "annotated-detector-map.png",
        "emission-vs-absorption.png",
        "detector-diagnostics.png",
        "registration-shifts.png",
    ):
        shutil.copy2(figures / name, web_assets / name)

    plt.close("all")


if __name__ == "__main__":
    main()
