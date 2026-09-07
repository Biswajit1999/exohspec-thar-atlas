"""Command-line entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analysis import build_public_products


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Build privacy-reviewed EXOhSPEC Th-Ar public data products."
    )
    result.add_argument("fits", nargs="+", help="Two or more local Th-Ar FITS exposures")
    result.add_argument(
        "--output-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root receiving web/assets, web/data, and data/derived",
    )
    return result


def main() -> None:
    args = parser().parse_args()
    rows = build_public_products(args.fits, args.output_root)
    for row in rows:
        print(
            f"{row.exposure_seconds:>5g} s | background {row.background_adu:>7.2f} ADU | "
            f"full-scale {row.full_scale_pixels:>4d} | {row.display_role}"
        )


if __name__ == "__main__":
    main()

