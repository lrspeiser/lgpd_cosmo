#!/usr/bin/env python3
"""
Convert an ASCII table of theory spectra (ℓ, C_ell columns) to NPZ in the format this repo expects.

Expected input: a text file with a header naming columns, e.g.
  ell  cltt  clte  clee  clbb
or comma-separated with the same names. Order is flexible if names are present.

Output NPZ keys:
  - ell, cltt, clte, clee, (optional) clbb

Usage:
  python scripts/planck_ascii_to_npz.py /path/to/planck_bestfit_cls.txt --out data/planck_baseline_cls.npz
"""
import argparse
import os
import numpy as np


def _normalize(name: str) -> str:
    return name.strip().lower().replace("_", "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("in_txt", help="Input ASCII file with header and columns like: ell cltt clte clee [clbb]")
    ap.add_argument("--out", default="data/planck_baseline_cls.npz", help="Output NPZ path")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    # Try to read with header names
    try:
        arr = np.genfromtxt(args.in_txt, names=True, dtype=float, delimiter=None)
        names = list(arr.dtype.names)
        names_norm = {_normalize(n): n for n in names}
        ell = np.asarray(arr[names_norm.get("ell") or names_norm.get("l")])
        m = ell >= 2
        out = {
            "ell": ell[m].astype(int),
        }
        # optional keys
        for src, dst in [("cltt", "cltt"), ("clte", "clte"), ("clee", "clee"), ("clbb", "clbb")]:
            key = names_norm.get(src)
            if key is not None:
                out[dst] = np.asarray(arr[key])[m]
    except Exception:
        # Fallback: assume whitespace no-header with columns: ell cltt clee clte [clbb]
        raw = np.loadtxt(args.in_txt)
        ell = raw[:, 0].astype(int)
        m = ell >= 2
        ell = ell[m]
        out = {
            "ell": ell,
            "cltt": raw[:, 1][m],
            "clee": raw[:, 2][m],
        }
        if raw.shape[1] >= 4:
            out["clte"] = raw[:, 3][m]
        if raw.shape[1] >= 5:
            out["clbb"] = raw[:, 4][m]

    np.savez(args.out, **out)
    print(f"Wrote {args.out} with ℓ up to {int(out['ell'][-1])}")


if __name__ == "__main__":
    main()
