#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from astropy.io import fits


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Display the HDU structure of a FITS file."
    )

    parser.add_argument(
        "fits_file",
        type=Path,
        help="Path to the FITS file.",
    )

    args = parser.parse_args()

    with fits.open(args.fits_file, memmap=False) as hdus:
        print(f"Number of HDUs: {len(hdus)}")

        for index, hdu in enumerate(hdus):
            print()
            print(f"HDU {index}")
            print(f"  Type       : {type(hdu).__name__}")
            print(f"  Name       : {hdu.name}")

            if hdu.data is None:
                print("  Data       : None")
                continue

            print(f"  Shape      : {hdu.data.shape}")
            print(f"  Dimensions : {hdu.data.ndim}")
            print(f"  Dtype      : {hdu.data.dtype}")


if __name__ == "__main__":
    main()