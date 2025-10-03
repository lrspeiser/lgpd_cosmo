#!/usr/bin/env python3
"""
Generate baseline C_ell using CLASS via the repo helper and save to data/planck_baseline_cls.npz.

Writes keys expected by this repo:
  - ell
  - cltt, clte, clee
  - optional: clbb, clpp

Usage:
  python scripts/make_planck_cls_class.py --lmax 3000 --out data/planck_baseline_cls.npz

Requires:
  - CLASS with Python bindings (classy) available in the current environment.
"""
import argparse
import os
import numpy as np

from lgpd_cosmo.cmb import get_baseline_cls_from_class

# Planck 2018-like baseline cosmology (adjust as needed)
DEFAULT_PARAMS = dict(
    h=0.6736,
    omega_b=0.02237,
    omega_cdm=0.1200,
    A_s=float(np.exp(3.044) * 1e-10),  # ln(10^10 As)=3.044
    n_s=0.9649,
    tau_reio=0.0544,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/planck_baseline_cls.npz", help="Output NPZ path")
    ap.add_argument("--lmax", type=int, default=3000, help="Maximum multipole ℓ")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    ells, data = get_baseline_cls_from_class(cosmoparams=DEFAULT_PARAMS, lmax=args.lmax)
    if ells is None or data is None:
        raise SystemExit("CLASS (classy) not available. Install CLASS with Python bindings and retry.")

    npz_kwargs = {
        "ell": ells,
        "cltt": data["cltt"],
        "clte": data["clte"],
        "clee": data["clee"],
    }
    if "clbb" in data and data["clbb"] is not None:
        npz_kwargs["clbb"] = data["clbb"]
    if "clpp" in data and data["clpp"] is not None:
        npz_kwargs["clpp"] = data["clpp"]

    np.savez(args.out, **npz_kwargs)
    print(f"Wrote {args.out} with ℓ up to {int(ells[-1])}")


if __name__ == "__main__":
    main()
