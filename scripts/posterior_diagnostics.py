#!/usr/bin/env python3
"""
Posterior diagnostics and quick posterior-predictive overlay for lgpd_cosmo.

- Loads posterior (examples/_real_fit/posterior.npz) with arrays: chain (N,3), logprob (N,)
  parameter order assumed: [mu0, sigma0, xi_damp]
- Loads baseline C_ell from data/planck_baseline_cls.npz (ell, cltt, clte, clee, optional clbb)
- Writes to examples/_real_fit/diagnostics:
  - posterior_summary.csv (median, 16th, 84th percentiles)
  - hist_mu0.png, hist_sigma0.png, hist_xi_damp.png
  - scatter_mu0_sigma0.png
  - tt_overlay.png (baseline vs LGPD-modified at posterior medians)

Usage:
  python scripts/posterior_diagnostics.py \
    --posterior examples/_real_fit/posterior.npz \
    --baseline data/planck_baseline_cls.npz \
    --outdir examples/_real_fit/diagnostics
"""
import argparse
import os
import json
import numpy as np
import matplotlib.pyplot as plt

from lgpd_cosmo.models import (
    LGPDParams, CondensateParams, ElasticityParams, LGPDTransfer
)
from lgpd_cosmo.cmb import apply_modifications


def q68(x):
    x = np.asarray(x)
    return np.percentile(x, [16, 50, 84])


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)


def Dl_from_Cl(ell, Cl):
    ell = np.asarray(ell)
    return ell * (ell + 1.0) * np.asarray(Cl) / (2.0 * np.pi)


def overlay_tt(ell, base_cls, theta_med, out_png):
    mu0, sigma0, xi = theta_med
    # Match the choices in examples/fit_with_real_data.py
    lgpd = LGPDParams(log10_Gamma0=-18.5, a_star=1.0, p=2.0, T_lgpd=2.7255, xi_damp=xi)
    cond = CondensateParams(mu0=mu0, k0=0.07, m=2.0, zt=1.5, n=3.0)
    elas = ElasticityParams(sigma0=sigma0, k0=0.1, m=2.0, zt=1.5, n=3.0)
    tr = LGPDTransfer(lgpd, cond, elas)
    mod = apply_modifications(ell, base_cls, tr)

    Dl0 = Dl_from_Cl(ell, base_cls['TT'])
    Dl1 = Dl_from_Cl(ell, mod['TT'])

    plt.figure(figsize=(8,5))
    plt.loglog(ell, Dl0, label='TT baseline', color='tab:blue')
    plt.loglog(ell, Dl1, label='TT modified (median θ)', color='tab:orange')
    plt.xlabel(r'$\ell$')
    plt.ylabel(r'$D_\ell$')
    plt.legend()
    plt.grid(True, which='both', ls='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--posterior', default='examples/_real_fit/posterior.npz')
    ap.add_argument('--baseline', default='data/planck_baseline_cls.npz')
    ap.add_argument('--outdir', default='examples/_real_fit/diagnostics')
    args = ap.parse_args()

    ensure_dir(args.outdir)

    # Load posterior
    post = np.load(args.posterior)
    chain = np.asarray(post['chain'])
    logp = np.asarray(post['logprob'])
    if chain.ndim != 2 or chain.shape[1] != 3:
        raise SystemExit(f'Unexpected chain shape: {chain.shape}. Expected (N,3).')

    names = ['mu0','sigma0','xi_damp']
    stats = {}
    for i, n in enumerate(names):
        lo, med, hi = q68(chain[:, i])
        stats[n] = {
            'p16': float(lo), 'p50': float(med), 'p84': float(hi),
        }

    # Save CSV summary
    csv_path = os.path.join(args.outdir, 'posterior_summary.csv')
    with open(csv_path, 'w') as f:
        f.write('param,p16,p50,p84\n')
        for n in names:
            s = stats[n]
            f.write(f"{n},{s['p16']},{s['p50']},{s['p84']}\n")

    # Save JSON summary
    with open(os.path.join(args.outdir, 'posterior_summary.json'), 'w') as f:
        json.dump({
            'stats': stats,
            'logprob': {
                'mean': float(logp.mean()),
                'min': float(logp.min()),
                'max': float(logp.max()),
            }
        }, f, indent=2)

    # Plots: histograms
    bins = 60
    colors = dict(mu0='#f39c12', sigma0='#27ae60', xi_damp='#2980b9')
    for i, n in enumerate(names):
        plt.figure(figsize=(8,5))
        plt.hist(chain[:, i], bins=bins, color=colors[n], alpha=0.9, density=True)
        plt.title(f'Posterior histogram: {n}')
        plt.xlabel(n)
        plt.ylabel('density')
        plt.grid(True, ls='--', alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(args.outdir, f'hist_{n}.png'), dpi=150)
        plt.close()

    # Scatter: mu0 vs sigma0
    plt.figure(figsize=(8,5))
    plt.scatter(chain[:,0], chain[:,1], s=5, c='#f39c12', alpha=0.35)
    plt.title('Posterior scatter: mu0 vs sigma0')
    plt.xlabel('mu0')
    plt.ylabel('sigma0')
    plt.grid(True, ls='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(args.outdir, 'scatter_mu0_sigma0.png'), dpi=150)
    plt.close()

    # Overlay TT using median parameters
    base = np.load(args.baseline)
    ell = base['ell']
    # Map NPZ keys (cltt, clte, clee, clbb, clpp) to the keys expected by apply_modifications (TT, TE, EE, BB, PP)
    base_cls = {}
    if 'cltt' in base: base_cls['TT'] = base['cltt']
    if 'clte' in base: base_cls['TE'] = base['clte']
    if 'clee' in base: base_cls['EE'] = base['clee']
    if 'clbb' in base: base_cls['BB'] = base['clbb']
    if 'clpp' in base: base_cls['PP'] = base['clpp']
    theta_med = np.array([stats['mu0']['p50'], stats['sigma0']['p50'], stats['xi_damp']['p50']])
    overlay_tt(ell, base_cls, theta_med, os.path.join(args.outdir, 'tt_overlay.png'))

    print('Diagnostics written to', args.outdir)


if __name__ == '__main__':
    main()
