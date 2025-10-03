#!/usr/bin/env python3
"""
Generate baseline C_ell using CAMB and save to data/planck_baseline_cls.npz.

Writes keys expected by this repo:
  - ell
  - cltt, clte, clee
  - optional: clbb

Note: CAMB get_cmb_power_spectra with CMB_unit="muK" returns D_ell in μK^2.
We convert D_ell -> C_ell via C_ell = 2π D_ell / [ℓ(ℓ+1)]. Units remain μK^2 for C_ell, which is fine for this repo.

Usage:
  python scripts/make_planck_cls_camb.py --lmax 3000 --out data/planck_baseline_cls.npz

Requires:
  pip install camb
"""
import argparse
import os
import numpy as np
import camb

# Planck 2018-like baseline parameters
h = 0.6736
ombh2 = 0.02237
omch2 = 0.1200
ns = 0.9649
tau = 0.0544
ln10As = 3.044
As = float(np.exp(ln10As) * 1e-10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/planck_baseline_cls.npz", help="Output NPZ path")
    ap.add_argument("--lmax", type=int, default=3000, help="Maximum multipole ℓ")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    pars = camb.CAMBparams()
    pars.set_cosmology(H0=h * 100, ombh2=ombh2, omch2=omch2, tau=tau)
    pars.InitPower.set_params(As=As, ns=ns)
    pars.set_for_lmax(args.lmax, lens_potential_accuracy=1)
    pars.WantCls = True
    pars.DoLensing = True

    results = camb.get_results(pars)
    cl = results.get_cmb_power_spectra(pars, CMB_unit="muK")

    # 'total' is lensed; columns: TT, EE, BB, TE; values are D_ell in μK^2
    tot = cl["total"]
    ell = np.arange(tot.shape[0])
    mask = ell >= 2
    ell = ell[mask]

    conv = 2.0 * np.pi / (ell * (ell + 1.0))
    cltt = tot[:, 0][mask] * conv
    clee = tot[:, 1][mask] * conv
    clbb = tot[:, 2][mask] * conv
    clte = tot[:, 3][mask] * conv

    np.savez(
        args.out,
        ell=ell,
        cltt=cltt,
        clte=clte,
        clee=clee,
        clbb=clbb,
    )
    print(f"Wrote {args.out} with ℓ up to {int(ell[-1])}")


if __name__ == "__main__":
    main()
