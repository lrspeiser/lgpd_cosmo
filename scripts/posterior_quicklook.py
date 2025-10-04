#!/usr/bin/env python3
"""
Posterior quick-look: prints medians and 68% CI from an .npz file with 'chain'.

Usage:
  python scripts/posterior_quicklook.py \
    --posterior outputs/multiprobe_posterior.npz \
    [--param_names mu0,Sigma0,xi_damp] \
    [--out outputs/multiprobe_posterior_summary.json]
"""
import argparse
import json
import numpy as np
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--posterior', required=True)
    ap.add_argument('--param_names', default=None, help='Comma-separated names to label parameters (optional)')
    ap.add_argument('--out', default=None, help='Optional JSON output path')
    args = ap.parse_args()

    p = Path(args.posterior)
    data = np.load(p, allow_pickle=True)
    chain = data['chain']
    names = None
    if 'param_names' in data:
        names = [str(x) for x in data['param_names']]
    if args.param_names:
        names = args.param_names.split(',')

    med = np.median(chain, axis=0)
    lo = np.percentile(chain, 16, axis=0)
    hi = np.percentile(chain, 84, axis=0)

    print('Posterior summary:')
    for i in range(chain.shape[1]):
        label = names[i] if names and i < len(names) else f'p{i}'
        print(f"  {label}: {med[i]:.6f} [{lo[i]:.6f}, {hi[i]:.6f}]")

    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        json.dump({
            'param_names': names,
            'median': med.tolist(),
            'p16': lo.tolist(),
            'p84': hi.tolist(),
        }, open(outp, 'w'), indent=2)
        print('Wrote', outp)

if __name__ == '__main__':
    main()
