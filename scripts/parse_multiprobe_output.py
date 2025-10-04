#!/usr/bin/env python3
"""
Parse multiprobe log and posterior to produce human-readable and JSON summaries.

Usage:
  python scripts/parse_multiprobe_output.py \
    --log outputs/multiprobe.log \
    --posterior outputs/multiprobe_posterior.npz \
    --out_txt outputs/multiprobe_summary.txt \
    --out_json outputs/multiprobe_summary.json
"""
import argparse
import json
import re
import numpy as np
from pathlib import Path

def parse_log(log_path: Path):
    bestfit = None
    chi2_blocks = {}
    param_names = None
    if not log_path.exists():
        return bestfit, chi2_blocks, param_names
    bf_pat = re.compile(r"BESTFIT\s+chi2=([0-9eE+\-.]+)\s+params=([0-9eE+\-.,]+)")
    name_pat = re.compile(r"PARAM_NAMES=([A-Za-z0-9_,]+)")
    chi2_pat = re.compile(r"CHI2_([A-Z]+)=([0-9eE+\-.]+)")
    with log_path.open() as f:
        for line in f:
            line = line.strip()
            m = bf_pat.search(line)
            if m:
                chi2 = float(m.group(1))
                params = [float(x) for x in m.group(2).split(',')]
                bestfit = {'chi2': chi2, 'params': params}
                continue
            m = name_pat.search(line)
            if m:
                param_names = m.group(1).split(',')
                continue
            m = chi2_pat.search(line)
            if m:
                chi2_blocks[m.group(1)] = float(m.group(2))
    return bestfit, chi2_blocks, param_names


def summarize_posterior(posterior_path: Path):
    if not posterior_path.exists():
        return None
    data = np.load(posterior_path, allow_pickle=True)
    chain = data['chain']
    names = data['param_names'] if 'param_names' in data else None
    med = np.median(chain, axis=0)
    lo = np.percentile(chain, 16, axis=0)
    hi = np.percentile(chain, 84, axis=0)
    return {
        'param_names': [str(x) for x in names] if names is not None else None,
        'median': med.tolist(),
        'p16': lo.tolist(),
        'p84': hi.tolist(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--log', required=True)
    ap.add_argument('--posterior', required=False)
    ap.add_argument('--out_txt', required=True)
    ap.add_argument('--out_json', required=True)
    args = ap.parse_args()

    log_path = Path(args.log)
    post_path = Path(args.posterior) if args.posterior else Path()

    bestfit, chi2_blocks, param_names = parse_log(log_path)
    posterior = summarize_posterior(post_path) if post_path and post_path.exists() else None

    # Write TXT
    out_txt = Path(args.out_txt)
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    with out_txt.open('w') as f:
        f.write('MULTIPROBE SUMMARY\n')
        f.write('===================\n\n')
        if bestfit:
            f.write(f"Best-fit chi2: {bestfit['chi2']:.3f}\n")
            if param_names:
                f.write('Best-fit params: ' + ', '.join(f"{n}={v:.6f}" for n, v in zip(param_names, bestfit['params'])) + '\n')
            else:
                f.write('Best-fit params: ' + ', '.join(f"{v:.6f}" for v in bestfit['params']) + '\n')
        else:
            f.write('Best-fit not found in log.\n')
        if chi2_blocks:
            f.write('\nPer-block chi2:\n')
            for k in sorted(chi2_blocks.keys()):
                f.write(f"  {k}: {chi2_blocks[k]:.3f}\n")
        if posterior:
            f.write('\nPosterior (median [16,84]):\n')
            names = posterior['param_names'] or [f'p{i}' for i in range(len(posterior['median']))]
            for i, n in enumerate(names):
                f.write(f"  {n}: {posterior['median'][i]:.6f} [{posterior['p16'][i]:.6f}, {posterior['p84'][i]:.6f}]\n")

    # Write JSON
    out_json = Path(args.out_json)
    with out_json.open('w') as fo:
        json.dump({'bestfit': bestfit, 'chi2_blocks': chi2_blocks, 'param_names': param_names, 'posterior': posterior}, fo, indent=2)

    print('Wrote', out_txt)
    print('Wrote', out_json)

if __name__ == '__main__':
    main()
