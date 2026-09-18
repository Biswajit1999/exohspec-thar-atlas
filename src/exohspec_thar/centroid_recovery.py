"""Synthetic injection-recovery for Th-Ar line-centroid measurements.

The experiment validates detector-domain estimators. It deliberately does
not infer a wavelength solution or an EXOhSPEC radial-velocity precision.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class CentroidConfig:
    exposures_seconds: tuple[float, ...] = (30.0, 60.0, 120.0, 180.0)
    trials_per_feature: int = 1000
    seed: int = 20260918
    background_adu: float = 505.0
    background_sigma_adu: float = 4.45
    saturation_adu: float = 65535.0
    selection_ceiling_adu: float = 60000.0
    gaussian_sigma_px: float = 1.15
    strongest_peak_rate_adu_per_second: float = 900.0


@dataclass(frozen=True)
class Feature:
    feature_id: str
    normalized_x: float
    relative_peak_signal: float


@dataclass(frozen=True)
class RecoveryRecord:
    feature_id: str
    relative_peak_signal: float
    strength_band: str
    strategy: str
    trials: int
    bias_px: float
    rmse_px: float
    median_absolute_error_px: float
    p95_absolute_error_px: float
    catastrophic_fraction: float


def load_features(path: str | Path) -> list[Feature]:
    """Load privacy-reviewed measured feature strengths and normalized positions."""

    with Path(path).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [
        Feature(
            feature_id=row["feature_id"],
            normalized_x=float(row["normalized_x"]),
            relative_peak_signal=float(row["relative_peak_signal"]),
        )
        for row in rows
    ]


def _strength_band(relative_peak_signal: float) -> str:
    if relative_peak_signal >= 0.8:
        return "strong"
    if relative_peak_signal <= 0.12:
        return "faint"
    return "intermediate"


def _centroid(coordinate_px: np.ndarray, signal: np.ndarray) -> float:
    weights = np.clip(np.asarray(signal, dtype=float), 0.0, None)
    denominator = float(np.sum(weights))
    if denominator <= 0.0:
        return float("nan")
    return float(np.sum(coordinate_px * weights) / denominator)


def _pixelwise_hdr(
    observed: np.ndarray,
    exposures_seconds: np.ndarray,
    background_adu: float,
    selection_ceiling_adu: float,
) -> np.ndarray:
    """Select the longest non-ceiling exposure independently for every pixel."""

    rates = np.maximum(observed - background_adu, 0.0) / exposures_seconds[:, None]
    result = np.zeros(observed.shape[1], dtype=float)
    for pixel in range(observed.shape[1]):
        valid = np.flatnonzero(observed[:, pixel] < selection_ceiling_adu)
        chosen = int(valid[-1]) if valid.size else 0
        result[pixel] = rates[chosen, pixel]
    return result


def _linewise_longest_unsaturated(
    observed: np.ndarray,
    exposures_seconds: np.ndarray,
    background_adu: float,
    selection_ceiling_adu: float,
) -> np.ndarray:
    valid = np.flatnonzero(np.max(observed, axis=1) < selection_ceiling_adu)
    chosen = int(valid[-1]) if valid.size else 0
    return np.maximum(observed[chosen] - background_adu, 0.0) / exposures_seconds[chosen]


def _feature_centres(features: list[Feature]) -> np.ndarray:
    """Map public normalized coordinates to reproducible sub-pixel phases."""

    return np.asarray(
        [0.8 * (((feature.normalized_x * 997.0) % 1.0) - 0.5) for feature in features]
    )


def run_recovery(
    features: list[Feature],
    config: CentroidConfig = CentroidConfig(),
) -> list[RecoveryRecord]:
    """Run deterministic line-centroid injection-recovery simulations."""

    if not features:
        raise ValueError("At least one feature is required")
    if config.trials_per_feature < 2:
        raise ValueError("At least two trials per feature are required")

    rng = np.random.default_rng(config.seed)
    exposures = np.asarray(config.exposures_seconds, dtype=float)
    coordinate = np.arange(-8.0, 9.0)
    centres = _feature_centres(features)
    records: list[RecoveryRecord] = []

    for feature, true_centre in zip(features, centres):
        profile = np.exp(-0.5 * ((coordinate - true_centre) / config.gaussian_sigma_px) ** 2)
        rate = config.strongest_peak_rate_adu_per_second * feature.relative_peak_signal
        errors: dict[str, list[float]] = {
            "fixed_120s": [],
            "fixed_180s": [],
            "longest_unsaturated": [],
            "pixelwise_hdr": [],
        }

        for _ in range(config.trials_per_feature):
            expected_signal = exposures[:, None] * rate * profile[None, :]
            shot_signal = rng.poisson(expected_signal)
            read_background = rng.normal(
                config.background_adu,
                config.background_sigma_adu,
                size=expected_signal.shape,
            )
            observed = np.clip(shot_signal + read_background, 0.0, config.saturation_adu)

            profiles = {
                "fixed_120s": np.maximum(observed[2] - config.background_adu, 0.0) / exposures[2],
                "fixed_180s": np.maximum(observed[3] - config.background_adu, 0.0) / exposures[3],
                "longest_unsaturated": _linewise_longest_unsaturated(
                    observed, exposures, config.background_adu, config.selection_ceiling_adu
                ),
                "pixelwise_hdr": _pixelwise_hdr(
                    observed, exposures, config.background_adu, config.selection_ceiling_adu
                ),
            }
            for strategy, recovered_profile in profiles.items():
                errors[strategy].append(_centroid(coordinate, recovered_profile) - true_centre)

        for strategy, values in errors.items():
            array = np.asarray(values)
            absolute = np.abs(array)
            records.append(
                RecoveryRecord(
                    feature_id=feature.feature_id,
                    relative_peak_signal=feature.relative_peak_signal,
                    strength_band=_strength_band(feature.relative_peak_signal),
                    strategy=strategy,
                    trials=config.trials_per_feature,
                    bias_px=float(np.mean(array)),
                    rmse_px=float(np.sqrt(np.mean(array**2))),
                    median_absolute_error_px=float(np.median(absolute)),
                    p95_absolute_error_px=float(np.percentile(absolute, 95)),
                    catastrophic_fraction=float(np.mean(absolute > 0.05)),
                )
            )
    return records


def aggregate_records(records: list[RecoveryRecord]) -> list[dict[str, object]]:
    """Aggregate trial-equivalent errors by strength band and strategy."""

    rows: list[dict[str, object]] = []
    strategies = sorted({record.strategy for record in records})
    for band in ("all", "strong", "intermediate", "faint"):
        for strategy in strategies:
            selected = [
                record
                for record in records
                if record.strategy == strategy and (band == "all" or record.strength_band == band)
            ]
            if not selected:
                continue
            total_trials = sum(record.trials for record in selected)
            bias = sum(record.bias_px * record.trials for record in selected) / total_trials
            mse = sum((record.rmse_px**2) * record.trials for record in selected) / total_trials
            catastrophic = (
                sum(record.catastrophic_fraction * record.trials for record in selected) / total_trials
            )
            rows.append(
                {
                    "strength_band": band,
                    "strategy": strategy,
                    "features": len(selected),
                    "trials": total_trials,
                    "bias_px": bias,
                    "rmse_px": float(np.sqrt(mse)),
                    "catastrophic_fraction": catastrophic,
                }
            )
    return rows
