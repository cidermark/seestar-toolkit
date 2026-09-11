"""Reproduce the public synthetic Siril-style mosaic without reading capture data."""

from pathlib import Path

import numpy as np
from astropy.io import fits


def main() -> None:
    """Write a deterministic, asymmetric linear RGB fixture in FITS axis order."""
    channel, row, column = np.indices((3, 17, 11))
    data = ((channel * 256 + row * 12 + column) / 1024).astype(np.float32)
    header = fits.Header()
    header["PROGRAM"] = "Siril synthetic fixture"
    header["IMAGETYP"] = "Light"
    header["OBJECT"] = "Synthetic mosaic"
    header["CTYPE1"] = "RA---TAN"
    header["CTYPE2"] = "DEC--TAN"
    header["CUNIT1"] = "deg"
    header["CUNIT2"] = "deg"
    header["CRPIX1"] = 6.0
    header["CRPIX2"] = 9.0
    header["CRVAL1"] = 0.0
    header["CRVAL2"] = 0.0
    header["CDELT1"] = -0.001
    header["CDELT2"] = 0.001
    header["PC1_1"] = 0.8
    header["PC1_2"] = -0.6
    header["PC2_1"] = 0.6
    header["PC2_2"] = 0.8
    header["COMMENT"] = "Synthetic linear RGB; invented WCS; no capture metadata."
    destination = (
        Path(__file__).resolve().parents[1] / "tests/data/reference/siril_stacked_mosaic.fit"
    )
    hdu = fits.PrimaryHDU(data=data, header=header)
    hdu.header["BSCALE"] = 1.0
    hdu.header["BZERO"] = 0.0
    hdu.writeto(destination, overwrite=True)


if __name__ == "__main__":
    main()
