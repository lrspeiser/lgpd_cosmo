#!/usr/bin/env python3
"""
Redshift trend diagnostics for SNe, BAO, and growth datasets.

- Computes residuals (data - model) / sigma versus redshift
- Fits a weighted linear slope and computes Spearman rank correlation
- Supports constant or two-bin μ(a) models for growth predictions

Usage examples:
  python scripts/redshift_trend_diagnostics.py --quick
  python scripts/redshift_trend_diagnostics.py --posterior outputs/multiprobe/multiprobe_posterior.npz
  python scripts/redshift_trend_diagnostics.py --mu-model binned --z-split 0.5 --mu-low 0.0 --mu-high 0.1

Notes:
- BAO DV/rd uses an approximate DV(z) and a fixed sound horizon rd=147.1 Mpc as an effective constant.
  This is sufficient for trend testing (relative residuals vs z). For precision work, integrate a
  Boltzmann pipeline and calibrated rd.
- SNe residuals include a fitted offset (nuisance magnitude) that is marginalized analytically by
  minimizing chi^2 w.r.t. a constant offset.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

import sys
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from lgpd_cosmo.data import DataRepository
from lgpd_cosmo.background import LCDM
from lgpd_cosmo.linear import GrowthModel


def fit_offset(residuals, sigma):
    """Return best-fit constant offset for residuals with weights 1/sigma^2."""
    w = 1.0 / np.maximum(sigma, 1e-12) ** 2
    num = np.sum(w * residuals)
    den = np.sum(w)
    return num / max(den, 1e-12)


def bao_DV_over_rd(lcdm: LCDM, z):
    z = np.asarray(z)
    c = 299792.458
    Hz = np.array([lcdm.H(zi) for zi in z])
    chi = np.array([lcdm.comoving_distance(zi) for zi in z])
    DV = (c * z * (chi ** 2) / Hz) ** (1.0 / 3.0)
    rd = 147.1  # Mpc, effective constant for trend diagnostics
    return DV / rd


def sne_mu_model(lcdm: LCDM, z):
    z = np.asarray(z)
    DL = np.array([lcdm.luminosity_distance(zi) for zi in z])  # Mpc
    return 5.0 * np.log10(np.maximum(DL, 1e-8)) + 25.0


def build_mu_of_a(mu_model: str, z_split: float, mu0: float = 0.0, mu_low: float = 0.0, mu_high: float = 0.0):
    if mu_model == 'constant':
        return lambda a: mu0
    else:
        def fn(a):
            a = np.asarray(a)
            z = 1.0 / np.maximum(a, 1e-8) - 1.0
            return np.where(z <= z_split, mu_low, mu_high)
        return fn


def analyze_trend(z, residuals, sigma):
    z = np.asarray(z)
    r = np.asarray(residuals)
    s = np.asarray(sigma)
    w = 1.0 / np.maximum(s, 1e-12) ** 2

    # Weighted linear fit r = a + b z
    A = np.vstack([np.ones_like(z), z]).T
    W = np.diag(w)
    try:
        cov = np.linalg.inv(A.T @ W @ A)
        beta = cov @ (A.T @ W @ r)
        a0, b1 = beta[0], beta[1]
        b1_err = np.sqrt(np.maximum(cov[1, 1], 0.0))
    except np.linalg.LinAlgError:
        a0, b1, b1_err = np.nan, np.nan, np.nan

    # Spearman correlation
    rho, pval = spearmanr(z, r)
    return {
        'intercept': float(a0),
        'slope': float(b1),
        'slope_err': float(b1_err),
        'spearman_rho': float(rho) if np.isfinite(rho) else np.nan,
        'spearman_p': float(pval) if np.isfinite(pval) else np.nan,
    }


def main():
    ap = argparse.ArgumentParser(description='Redshift trend diagnostics for SNe, BAO, and growth')
    ap.add_argument('--posterior', default=None, help='Optional posterior .npz to seed μ parameters')
    ap.add_argument('--mu-model', choices=['constant', 'binned'], default='constant')
    ap.add_argument('--mu0', type=float, default=0.0)
    ap.add_argument('--mu-low', dest='mu_low', type=float, default=0.0)
    ap.add_argument('--mu-high', dest='mu_high', type=float, default=0.0)
    ap.add_argument('--z-split', type=float, default=0.5)
    ap.add_argument('--out', default=str(repo_root / 'outputs' / 'redshift_trends'))
    ap.add_argument('--quick', action='store_true', help='Run quickly (no functional change, reserved)')
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Data and cosmology
    repo = DataRepository(repo_root / 'data')
    lcdm = LCDM()

    # Configure μ(a)
    mu_model = args.mu_model
    mu0 = args.mu0
    mu_low = args.mu_low
    mu_high = args.mu_high
    z_split = args.z_split

    # If posterior provided, use medians
    if args.posterior:
        p = Path(args.posterior)
        if p.exists():
            data = np.load(p, allow_pickle=True)
            names = [str(x) for x in data['param_names']] if 'param_names' in data else None
            med = np.median(data['chain'], axis=0)
            if names is not None:
                if 'mu0' in names:
                    mu0 = float(med[names.index('mu0')])
                    mu_model = 'constant'
                elif 'mu_low' in names and 'mu_high' in names:
                    mu_low = float(med[names.index('mu_low')])
                    mu_high = float(med[names.index('mu_high')])
                    mu_model = 'binned'
            # If names absent, fall back to CLI values

    mu_of_a_fn = build_mu_of_a(mu_model, z_split, mu0=mu0, mu_low=mu_low, mu_high=mu_high)

    summary = {}

    # SNe
    sne_path = Path(repo.path('sne_pantheon.csv'))
    if sne_path.exists():
        sne = repo.load_sne('sne_pantheon.csv')
        z = sne[:, 0]
        mu_obs = sne[:, 1]
        sig = sne[:, 2]
        mu_th = sne_mu_model(lcdm, z)
        # Fit an offset to minimize chi2
        off = fit_offset(mu_obs - mu_th, sig)
        resid = (mu_obs - (mu_th + off)) / sig
        summary['SNe'] = analyze_trend(z, resid, np.ones_like(sig))
        # Save CSV
        np.savetxt(out_dir / 'sne_residuals.csv', np.vstack([z, resid]).T, delimiter=',', header='z,residual', comments='')

    # BAO
    for candidate in ['bao.csv', 'bao_boss.csv', 'bao_compilation.csv']:
        p = Path(repo.path(candidate))
        if p.exists():
            bao = repo.load_bao(candidate)
            z = bao[:, 0]
            y_obs = bao[:, 1]
            sig = bao[:, 2]
            y_th = bao_DV_over_rd(lcdm, z)
            # Fit a scale factor to account for rd mismatch (act like offset in log space)
            # Here we fit multiplicative factor A to minimize (y_obs - A y_th)^2 / sig^2
            w = 1.0 / np.maximum(sig, 1e-12) ** 2
            A = (np.sum(w * y_obs * y_th) / max(np.sum(w * y_th * y_th), 1e-12))
            resid = (y_obs - A * y_th) / sig
            summary['BAO'] = analyze_trend(z, resid, np.ones_like(sig))
            np.savetxt(out_dir / 'bao_residuals.csv', np.vstack([z, resid]).T, delimiter=',', header='z,residual', comments='')
            break

    # Growth
    growth_path = Path(repo.path('growth_fsigma8.csv'))
    if growth_path.exists():
        growth = repo.load_growth('growth_fsigma8.csv')
        z = growth[:, 0]
        y_obs = growth[:, 1]
        sig = growth[:, 2]
        GM = GrowthModel(lcdm, mu_of_a_fn=mu_of_a_fn)
        y_th = GM.fsigma8(z, sigma8_0=0.8)
        # No nuisance; compute residual in sigma units
        resid = (y_obs - y_th) / sig
        summary['Growth'] = analyze_trend(z, resid, np.ones_like(sig))
        np.savetxt(out_dir / 'growth_residuals.csv', np.vstack([z, resid]).T, delimiter=',', header='z,residual', comments='')

    # Save JSON summary
    with open(out_dir / 'trend_summary.json', 'w') as f:
        json.dump({
            'mu_model': mu_model,
            'params': {'mu0': mu0, 'mu_low': mu_low, 'mu_high': mu_high, 'z_split': z_split},
            'summary': summary
        }, f, indent=2)

    print('Wrote diagnostics to', out_dir)


if __name__ == '__main__':
    main()
