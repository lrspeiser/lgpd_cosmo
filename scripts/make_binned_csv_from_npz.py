#!/usr/bin/env python3
"""
Make simple binned CSVs (TT/TE/EE) from an NPZ containing C_ell arrays.

Input NPZ keys:
  - ell (int), cltt, clte, clee (and optionally clbb)

Output CSVs (if the key exists):
  - data/planck_tt_binned.csv
  - data/planck_te_binned.csv
  - data/planck_ee_binned.csv
Each CSV has header: ell,Dl,sigma

Binning is simple: average D_ell in uniform ell bins of width --step
and set sigma = frac * |Dl| + noise_floor.

Usage:
  python scripts/make_binned_csv_from_npz.py --npz data/planck_baseline_cls.npz --out_prefix data/planck --step 30

Note: These are synthetic bandpowers if the NPZ is theory C_ell.
For real Planck bandpowers, convert the official products first, then bin.
"""
import argparse
import os
import numpy as np


def Dl_from_Cl(ell, Cl):
    ell = np.asarray(ell)
    return ell * (ell + 1.0) * np.asarray(Cl) / (2.0 * np.pi)


def bin_uniform(ell, y, step):
    ell = np.asarray(ell)
    y = np.asarray(y)
    e_min, e_max = int(ell.min()), int(ell.max())
    edges = np.arange(e_min, e_max + step, step)
    centers = []
    vals = []
    for i in range(len(edges) - 1):
        m = (ell >= edges[i]) & (ell < edges[i + 1])
        if not np.any(m):
            continue
        centers.append(float(ell[m].mean()))
        vals.append(float(y[m].mean()))
    return np.array(centers), np.array(vals)


def write_csv(path, ell, Dl, frac, noise_floor):
    sig = frac * np.abs(Dl) + noise_floor
    arr = np.column_stack([ell, Dl, sig])
    np.savetxt(path, arr, delimiter=',', header='ell,Dl,sigma', comments='')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--npz', default='data/planck_baseline_cls.npz', help='Input NPZ with ell and cl* arrays')
    ap.add_argument('--out_prefix', default='data/planck', help='Prefix for output CSVs')
    ap.add_argument('--step', type=int, default=30, help='Bin width in ell')
    ap.add_argument('--frac', type=float, default=0.05, help='Fractional error model for sigma')
    ap.add_argument('--noise_floor', type=float, default=1.0, help='Additive floor for sigma')
    args = ap.parse_args()

    d = np.load(args.npz)
    ell = d['ell']
    os.makedirs(os.path.dirname(args.out_prefix), exist_ok=True)

    def do(key, name):
        if key in d:
            Dl = Dl_from_Cl(ell, d[key])
            E, V = bin_uniform(ell, Dl, args.step)
            write_csv(f"{args.out_prefix}_{name}_binned.csv", E, V, args.frac, args.noise_floor)
            print(f"Wrote {args.out_prefix}_{name}_binned.csv")

    do('cltt', 'tt')
    do('clte', 'te')
    do('clee', 'ee')


if __name__ == '__main__':
    main()
