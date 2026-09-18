"""Generate the public Th-Ar line-centroid injection-recovery evidence."""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exohspec_thar.centroid_recovery import (  # noqa: E402
    CentroidConfig,
    aggregate_records,
    load_features,
    run_recovery,
)


def _rounded(row: dict[str, object]) -> dict[str, object]:
    return {key: round(value, 8) if isinstance(value, float) else value for key, value in row.items()}


def main() -> None:
    config_path = ROOT / "research" / "centroid-recovery-config.json"
    config_data = json.loads(config_path.read_text(encoding="utf-8"))
    config = CentroidConfig(
        exposures_seconds=tuple(config_data["exposures_seconds"]),
        trials_per_feature=config_data["trials_per_feature"],
        seed=config_data["seed"],
        background_adu=config_data["background_adu"],
        background_sigma_adu=config_data["background_sigma_adu"],
        saturation_adu=config_data["saturation_adu"],
        selection_ceiling_adu=config_data["selection_ceiling_adu"],
        gaussian_sigma_px=config_data["gaussian_sigma_px"],
        strongest_peak_rate_adu_per_second=config_data["strongest_peak_rate_adu_per_second"],
    )
    features = load_features(ROOT / "data" / "derived" / "measured-line-candidates-120s.csv")
    records = run_recovery(features, config)
    aggregate = aggregate_records(records)
    output = ROOT / "results" / "centroid-recovery"
    output.mkdir(parents=True, exist_ok=True)

    per_feature_rows = [_rounded(asdict(record)) for record in records]
    with (output / "per-feature.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=per_feature_rows[0].keys())
        writer.writeheader()
        writer.writerows(per_feature_rows)

    aggregate_rows = [_rounded(row) for row in aggregate]
    with (output / "summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=aggregate_rows[0].keys())
        writer.writeheader()
        writer.writerows(aggregate_rows)

    def row(band: str, strategy: str) -> dict[str, object]:
        return next(
            item
            for item in aggregate_rows
            if item["strength_band"] == band and item["strategy"] == strategy
        )

    strong_fixed = row("strong", "fixed_180s")
    strong_hdr = row("strong", "pixelwise_hdr")
    faint_fixed = row("faint", "fixed_180s")
    faint_hdr = row("faint", "pixelwise_hdr")
    strong_improvement = 1.0 - float(strong_hdr["rmse_px"]) / float(strong_fixed["rmse_px"])
    faint_ratio = float(faint_hdr["rmse_px"]) / float(faint_fixed["rmse_px"])
    hypothesis = {
        "null": "Pixelwise HDR reduces strong-line centroid RMSE by less than 50 percent relative to a fixed 180 s exposure.",
        "rejection_rule": "Reject when the relative RMSE reduction is at least 0.50.",
        "strong_line_rmse_reduction_fraction": round(strong_improvement, 8),
        "null_rejected": strong_improvement >= 0.50,
        "faint_line_hdr_to_fixed_180_rmse_ratio": round(faint_ratio, 8),
        "faint_line_guardrail": "HDR/fixed-180 RMSE ratio must remain at or below 1.10.",
        "faint_line_guardrail_passed": faint_ratio <= 1.10,
    }
    report = {
        "schema_version": 1,
        "study": "Synthetic detector-domain Th-Ar centroid injection-recovery",
        "inference_boundary": "No wavelength solution, atomic identification, or instrument RV precision is inferred.",
        "config": asdict(config),
        "feature_count": len(features),
        "total_injections": len(features) * config.trials_per_feature,
        "strategies": ["fixed_120s", "fixed_180s", "longest_unsaturated", "pixelwise_hdr"],
        "hypothesis": hypothesis,
        "aggregate_results": aggregate_rows,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(hypothesis, indent=2))


if __name__ == "__main__":
    main()
