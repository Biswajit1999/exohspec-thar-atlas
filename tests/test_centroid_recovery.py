from __future__ import annotations

import numpy as np

from exohspec_thar.centroid_recovery import (
    CentroidConfig,
    Feature,
    _centroid,
    _pixelwise_hdr,
    aggregate_records,
    run_recovery,
)


def test_centroid_recovers_symmetric_profile() -> None:
    coordinate = np.arange(-4.0, 5.0)
    profile = np.exp(-0.5 * (coordinate / 1.2) ** 2)
    assert abs(_centroid(coordinate, profile)) < 1e-12


def test_pixelwise_hdr_uses_short_exposure_for_saturated_core() -> None:
    observed = np.array([[505.0, 30000.0, 505.0], [505.0, 65535.0, 505.0]])
    result = _pixelwise_hdr(observed, np.array([30.0, 180.0]), 505.0, 60000.0)
    assert result[1] == (30000.0 - 505.0) / 30.0
    assert result[0] == 0.0


def test_recovery_is_deterministic_and_complete() -> None:
    features = [Feature("strong", 0.31, 1.0), Feature("faint", 0.63, 0.1)]
    config = CentroidConfig(trials_per_feature=20, seed=7)
    first = run_recovery(features, config)
    second = run_recovery(features, config)
    assert first == second
    assert len(first) == 8
    assert {record.strategy for record in first} == {
        "fixed_120s",
        "fixed_180s",
        "longest_unsaturated",
        "pixelwise_hdr",
    }
    assert all(np.isfinite(record.rmse_px) for record in first)
    assert any(row["strength_band"] == "all" for row in aggregate_records(first))
