"""Build a visible-range, species-coded Th-Ar reference-line guide.

Use ``--refresh`` to query the NIST Atomic Spectra Database.  The selected
reference lines are cached as CSV so ordinary report builds remain offline.
"""

from __future__ import annotations

import argparse
import csv
import re
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "derived" / "nist-visible-reference-lines.csv"
FIGURE_PATHS = [
    ROOT / "report" / "figures" / "thar-visible-reference-lines.png",
    ROOT / "web" / "assets" / "thar-visible-reference-lines.png",
]


def _number(value: object) -> float | None:
    match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value))
    return float(match.group()) if match else None


def _select_lines(table: object, species: str, counts: tuple[int, int, int]) -> list[dict[str, object]]:
    regions = [(380.0, 500.0), (500.0, 600.0), (600.0, 750.0)]
    candidates: list[tuple[float, float]] = []
    prefer_ritz = species.startswith("Th") or species == "Ar II"
    for row in table:
        primary = row["Ritz"] if prefer_ritz else row["Observed"]
        fallback = row["Observed"] if prefer_ritz else row["Ritz"]
        wavelength = _number(primary) or _number(fallback)
        intensity = _number(row["Rel."])
        if wavelength and intensity and 380.0 <= wavelength <= 750.0:
            candidates.append((wavelength, intensity))

    selected: list[dict[str, object]] = []
    for (low, high), count in zip(regions, counts):
        ranked = sorted(
            ((w, i) for w, i in candidates if low <= w < high),
            key=lambda item: item[1],
            reverse=True,
        )
        accepted: list[tuple[float, float]] = []
        for wavelength, intensity in ranked:
            if all(abs(wavelength - other[0]) >= 3.0 for other in accepted):
                accepted.append((wavelength, intensity))
            if len(accepted) == count:
                break
        selected.extend(
            {
                "species": species,
                "wavelength_nm": round(wavelength, 6),
                "relative_intensity": intensity,
                "region": "blue" if high == 500.0 else "green-yellow" if high == 600.0 else "red",
            }
            for wavelength, intensity in accepted
        )
    return selected


def refresh_cache() -> None:
    import astropy.units as u
    from astroquery.nist import Nist

    plan = {"Th I": (4, 3, 3), "Th II": (4, 3, 3), "Ar I": (3, 3, 4), "Ar II": (3, 3, 4)}
    rows: list[dict[str, object]] = []
    for species, counts in plan.items():
        table = Nist.query(380 * u.nm, 750 * u.nm, linename=species, wavelength_type="vacuum")
        rows.extend(_select_lines(table, species, counts))
    rows.sort(key=lambda row: float(row["wavelength_nm"]))

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["species", "wavelength_nm", "relative_intensity", "region", "source", "retrieved"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "source": "NIST ASD", "retrieved": date.today().isoformat()})


def _visible_rgb(wavelength_nm: np.ndarray) -> np.ndarray:
    anchors = np.array([380, 440, 490, 510, 570, 590, 645, 750], dtype=float)
    colors = np.array(
        [
            [0.36, 0.20, 0.75], [0.15, 0.27, 0.88], [0.10, 0.70, 0.95],
            [0.12, 0.72, 0.42], [0.82, 0.82, 0.12], [0.96, 0.55, 0.08],
            [0.90, 0.12, 0.08], [0.48, 0.03, 0.05],
        ]
    )
    return np.column_stack(
        [np.interp(wavelength_nm, anchors, colors[:, channel]) for channel in range(3)]
    )


def build_figure() -> None:
    with CSV_PATH.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    fig, axes = plt.subplots(2, 1, figsize=(13, 7.8), sharex=True, constrained_layout=True)
    fig.patch.set_facecolor("white")
    groups = [("Thorium reference lines (Th I and Th II)", ("Th I", "Th II"), "#155e75"),
              ("Argon reference lines (Ar I and Ar II)", ("Ar I", "Ar II"), "#c2410c")]
    for ax, (title, species_group, color) in zip(axes, groups):
        subset = [row for row in rows if row["species"] in species_group]
        intensities = np.array([float(row["relative_intensity"]) for row in subset])
        heights = 0.28 + 0.72 * np.sqrt(intensities / intensities.max())
        for row, height in zip(subset, heights):
            wavelength = float(row["wavelength_nm"])
            ax.vlines(wavelength, 0, height, color=color, linewidth=1.5)
            ax.text(
                wavelength,
                height + 0.035,
                f"{row['species']}\n{wavelength:.2f}",
                rotation=90,
                ha="center",
                va="bottom",
                fontsize=6.5,
                color="#17324d",
            )
        ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color="#102f52")
        ax.set_ylabel("Normalized\nreference strength")
        ax.set_ylim(0, 1.36)
        ax.grid(axis="x", color="#cbd5e1", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)

    wavelengths = np.linspace(380, 750, 1000)
    gradient = _visible_rgb(wavelengths)[None, :, :]
    axes[-1].imshow(gradient, extent=[380, 750, -0.18, -0.06], aspect="auto", clip_on=False)
    axes[-1].text(385, -0.29, "violet / blue", fontsize=9, color="#334155")
    axes[-1].text(535, -0.29, "green / yellow", fontsize=9, color="#334155", ha="center")
    axes[-1].text(742, -0.29, "red", fontsize=9, color="#334155", ha="right")
    axes[-1].set_xlim(380, 750)
    axes[-1].set_xlabel("Vacuum wavelength (nm) — NIST atomic reference data")
    fig.suptitle("Selected prominent Th-Ar reference lines across the visible range", fontsize=17, fontweight="bold")
    fig.text(
        0.5,
        -0.02,
        "Line strengths are normalized within each species panel and do not predict brightness in a particular lamp or detector exposure.",
        ha="center",
        fontsize=9,
        color="#475569",
    )
    for path in FIGURE_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=190, facecolor="white", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true", help="refresh selected lines from NIST ASD")
    args = parser.parse_args()
    if args.refresh or not CSV_PATH.exists():
        refresh_cache()
    build_figure()


if __name__ == "__main__":
    main()
