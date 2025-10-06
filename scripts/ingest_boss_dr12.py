#!/usr/bin/env python3
"""
Ingest BOSS DR12 consensus BAO and growth (fσ8) into lpgd/data/ in simple CSV format.

Reads:
- final_consensus_results_dV_FAP_fsig.txt (central values)
- final_consensus_covtot_dV_FAP_fsig.txt (9x9 covariance)
Assumes ordering per redshift bin: [dV/rs, F_AP, fσ8] at z = [0.38, 0.51, 0.61].

Writes:
- data/bao_compilation.csv with header: z,DV_over_rd,sigma
- data/growth_fsigma8.csv with header: z,fsigma8,sigma

Notes:
- This ignores cross-covariances and uses diagonal entries only to define per-point sigma.
  This is consistent with the current phenomenological pipeline and is not a substitute for
  a full covariance treatment.
"""
import numpy as np
from pathlib import Path
import argparse

REPO = Path(__file__).resolve().parents[1]


def parse_results_and_cov(results_path: Path, cov_path: Path):
    # Parse central values
    z_values = []
    dv_over_rs = {}
    f_ap = {}
    fsig8 = {}
    with results_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) != 3:
                continue
            z = float(parts[0]); kind = parts[1]; val = float(parts[2])
            if kind.lower().startswith('dv'):
                dv_over_rs[z] = val
                if z not in z_values:
                    z_values.append(z)
            elif kind.lower().startswith('f_ap'):
                f_ap[z] = val
                if z not in z_values:
                    z_values.append(z)
            elif kind.lower().startswith('fsig'):
                fsig8[z] = val
                if z not in z_values:
                    z_values.append(z)
    z_values = sorted(set(z_values))

    # Parse covariance (9x9) into matrix
    cov = np.loadtxt(cov_path)
    if cov.shape != (9, 9):
        raise ValueError(f"Unexpected covariance shape {cov.shape}; expected 9x9")

    # Indices: for each bin i=0,1,2 => positions (3*i + 0: dV/rs, 3*i + 1: F_AP, 3*i + 2: fsig8)
    sigma_dv = [np.sqrt(max(cov[3*i + 0, 3*i + 0], 0.0)) for i in range(3)]
    sigma_fs8 = [np.sqrt(max(cov[3*i + 2, 3*i + 2], 0.0)) for i in range(3)]

    bao_rows = []
    growth_rows = []
    for i, z in enumerate(z_values[:3]):
        if z not in dv_over_rs or z not in fsig8:
            continue
        bao_rows.append((z, dv_over_rs[z], sigma_dv[i]))
        growth_rows.append((z, fsig8[z], sigma_fs8[i]))
    return bao_rows, growth_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-root', default=str(Path('/Users/leonardspeiser/Projects/GravityCalculator') / 'data' / 'BOSS' / 'DR12_consensus' / 'COMBINEDDR12_final_consensus_dV_FAP'))
    ap.add_argument('--out-bao', default=str(REPO / 'data' / 'bao_compilation.csv'))
    ap.add_argument('--out-growth', default=str(REPO / 'data' / 'growth_fsigma8.csv'))
    args = ap.parse_args()

    results_path = Path(args.source_root) / 'final_consensus_results_dV_FAP_fsig.txt'
    cov_path = Path(args.source_root) / 'final_consensus_covtot_dV_FAP_fsig.txt'

    if not results_path.exists() or not cov_path.exists():
        raise FileNotFoundError(f"Missing source files: {results_path} or {cov_path}")

    bao_rows, growth_rows = parse_results_and_cov(results_path, cov_path)

    out_bao = Path(args.out_bao)
    out_bao.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(out_bao, np.array(bao_rows), delimiter=',', header='z,DV_over_rd,sigma', comments='')

    out_growth = Path(args.out_growth)
    out_growth.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(out_growth, np.array(growth_rows), delimiter=',', header='z,fsigma8,sigma', comments='')

    print('Wrote', out_bao)
    print('Wrote', out_growth)


if __name__ == '__main__':
    main()
