#!/usr/bin/env python3
"""
Convert Planck best-fit theory spectra from FITS to NPZ in the format expected by this repo.

Input FITS must contain a table with columns like:
  - ELL (or L)
  - CL_TT, CL_TE, CL_EE, CL_BB (names can vary; case-insensitive match)

Output NPZ keys:
  - ell, cltt, clte, clee, (optional) clbb

Usage:
  python scripts/planck_fits_to_npz.py /path/to/planck_bestfit_cls.fits --out data/planck_baseline_cls.npz

Requires:
  pip install astropy
"""
import argparse
import os
import numpy as np
from astropy.io import fits


CANDIDATES = {
    "ell": ["ELL", "L", "ell", "l"],
    "cltt": ["CL_TT", "CLTT", "cl_tt", "cltt"],
    "clte": ["CL_TE", "CLTE", "cl_te", "clte"],
    "clee": ["CL_EE", "CLEE", "cl_ee", "clee"],
    "clbb": ["CL_BB", "CLBB", "cl_bb", "clbb"],
}


def pick_column(names, candidates):
    low = {n.lower(): n for n in names}
    for cand in candidates:
        if cand.lower() in low:
            return low[cand.lower()]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("in_fits", help="Input Planck theory FITS file")
    ap.add_argument("--out", default="data/planck_baseline_cls.npz", help="Output NPZ path")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    with fits.open(args.in_fits) as hdul:
        # try first table HDU
        hdu = None
        for i in range(1, len(hdul)):
            if hasattr(hdul[i], "data") and hdul[i].data is not None:
                hdu = hdul[i]
                break
        if hdu is None:
            raise SystemExit("No table HDU with data found in FITS")
        data = hdu.data
        names = list(data.columns.names)

        col_ell = pick_column(names, CANDIDATES["ell"]) or names[0]
        ell = np.asarray(data[col_ell]).astype(int)
        m = ell >= 2
        ell = ell[m]

        out = {"ell": ell}
        for key, cands in [("cltt", CANDIDATES["cltt"]), ("clte", CANDIDATES["clte"]), ("clee", CANDIDATES["clee"]), ("clbb", CANDIDATES["clbb"])]:
            col = pick_column(names, cands)
            if col is not None:
                out[key] = np.asarray(data[col])[m]

    np.savez(args.out, **out)
    print(f"Wrote {args.out} with ℓ up to {int(ell[-1])}")


if __name__ == "__main__":
    main()
