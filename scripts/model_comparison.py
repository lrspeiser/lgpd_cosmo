#!/usr/bin/env python3
"""
Compute simple model comparison metrics (AIC/BIC) for stored chains.

Usage:
  python scripts/model_comparison.py --chain outputs/robustness/full.npz --n N_DATA

- N_DATA: total number of independent data points (e.g., total bins across TT/TE/EE + others)
  If omitted, the script will try to infer N from the chain's metadata or from
  detected binned files; this is approximate.

This is an interim utility while we plan nested sampling for robust evidences.
"""
import argparse
import numpy as np
from pathlib import Path
import sys

repo_root = Path(__file__).parent.parent


def infer_n_data(default=0):
    # Try to count rows in known binned CSVs
    data_dir = repo_root / 'data'
    n = 0
    for name in ['planck_tt_binned.csv', 'planck_te_binned.csv', 'planck_ee_binned.csv']:
        p = data_dir / name
        if p.exists():
            try:
                n += max(0, np.loadtxt(p, delimiter=',', skiprows=1).shape[0])
            except Exception:
                pass
    return n if n > 0 else default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chain', required=True, help='Path to .npz chain file')
    ap.add_argument('--n', type=int, default=None, help='Number of data points')
    args = ap.parse_args()

    data = np.load(args.chain, allow_pickle=True)
    log_prob = data['log_prob']
    k = len(data['param_names']) if 'param_names' in data else 3
    n = args.n if args.n is not None else infer_n_data()

    if n == 0:
        print('Warning: could not infer N_DATA; BIC will be unreliable.')
        n = 1

    lnL_max = float(np.max(log_prob))
    AIC = 2*k - 2*lnL_max
    BIC = k*np.log(n) - 2*lnL_max

    print('Model comparison metrics:')
    print('  k (parameters):', k)
    print('  n (data points):', n)
    print('  lnL_max:', lnL_max)
    print('  AIC:', AIC)
    print('  BIC:', BIC)

if __name__ == '__main__':
    main()
