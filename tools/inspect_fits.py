#!/usr/bin/env python3
"""
inspect_fits.py

Developer utility for inspecting Seestar FITS files.

Displays:
- File information
- FITS HDU structure
- Toolkit metadata (where possible)
- Raw FITS header
"""

from __future__ import annotations

import argparse
from pathlib import Path

from astropy.io import fits

from seestar_toolkit.fits.inspector import inspect_fits
from seestar_toolkit.fits.reader import read_fits_image

# ----------------------------------------------------------------------
# Formatting helpers
# ----------------------------------------------------------------------


def print_heading(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_field(name: str, value) -> None:
    print(f"{name:<15} : {value}")


# ----------------------------------------------------------------------
# Inspection
# ----------------------------------------------------------------------


def inspect_file(path: Path) -> None:
    print_heading("FILE INFORMATION")

    print_field("File", path)

    # ------------------------------------------------------------------
    # HDU Structure
    # ------------------------------------------------------------------

    print_heading("HDU STRUCTURE")

    with fits.open(path) as hdul:
        print_field("Number of HDUs", len(hdul))

        for index, hdu in enumerate(hdul):
            print()

            print(f"HDU {index}")
            print(f"  Type       : {type(hdu).__name__}")

            if hdu.data is None:
                print("  Data       : None")
            else:
                print(f"  Shape      : {hdu.data.shape}")
                print(f"  Dtype      : {hdu.data.dtype}")
                print(f"  Dimensions : {hdu.data.ndim}")

    # ------------------------------------------------------------------
    # Toolkit metadata
    # ------------------------------------------------------------------

    print_heading("TOOLKIT METADATA")

    try:
        image = read_fits_image(path)
        metadata = inspect_fits(path)

        print_field("HDU", image.hdu_index)
        print_field(
            "Dimensions",
            f"{image.width} × {image.height}",
        )
        print_field("Data Type", image.data.dtype)
        print_field("Bit Depth", image.bit_depth)

        print()

        print_field("Exposure", metadata.exposure_seconds)
        print_field("Gain", metadata.gain)
        print_field("Bayer", metadata.bayer_pattern)
        print_field("Object", metadata.object_name)
        print_field("Filter", metadata.filter_name)
        print_field("Telescope", metadata.telescope)
        print_field("Instrument", metadata.instrument)
        print_field("Captured", metadata.captured_at)

    except Exception as exc:
        print(f"Toolkit inspection failed: {exc}")

    # ------------------------------------------------------------------
    # Raw FITS header
    # ------------------------------------------------------------------

    with fits.open(path) as hdul:
        header = hdul[0].header

        print_heading(f"RAW FITS HEADER ({len(header)} keywords)")

        for keyword in header:
            print_field(keyword, header[keyword])


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect a FITS file."
    )

    parser.add_argument(
        "fits_file",
        type=Path,
        help="Path to FITS file",
    )

    args = parser.parse_args()

    inspect_file(args.fits_file)


if __name__ == "__main__":
    main()