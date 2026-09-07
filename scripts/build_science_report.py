"""Generate the expanded detector-domain metrics and figures."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exohspec_thar.science import build_science_products  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fits", nargs=4)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = build_science_products(args.fits, args.output_root)
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()

