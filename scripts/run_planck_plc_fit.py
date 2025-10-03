#!/usr/bin/env python3
"""
Run an LGPD fit against the official Planck PLC (clik) likelihoods.

- Reads likelihood file paths from configs/planck_plc_paths.json
- Evaluates -2 ln L via the root-level planck_plc.PlanckPLC adapter
- Uses the current phenomenological transfer (NOT Boltzmann-consistent yet)

Usage:
  source ./planck_env.sh   # set PLC_ROOT and env
  python scripts/run_planck_plc_fit.py --config configs/planck_plc_paths.json [--quick]

Outputs:
  outputs/plc/posterior_plc.npz
  outputs/plc/summary.txt

Notes:
  - Ensure data/planck_baseline_cls.npz exists; contains lensed TT/TE/EE, optionally clpp
  - Units: we pass μK^2 to the adapter (units="muK"); phi-phi is dimensionless
  - Quick mode runs fewer steps for a smoke test
"""
import argparse
import json
import os
from pathlib import Path
import numpy as np

# Repo root
REPO_ROOT = Path(__file__).parent.parent

# Local imports from package
from lgpd_cosmo.models import LGPDParams, CondensateParams, ElasticityParams, LGPDTransfer
from lgpd_cosmo.cmb import apply_modifications
from lgpd_cosmo.data import DataRepository
from lgpd_cosmo.mcmc import run_emcee
from planck_plc import PlanckPLC


def load_plc(config_path: Path) -> PlanckPLC:
    with open(config_path, 'r') as f:
        cfg = json.load(f)
    # Keep only provided keys
    like_paths = {k: v for k, v in cfg.items() if v and os.path.exists(v)}
    if not like_paths:
        raise FileNotFoundError("No valid PLC paths found in config. Edit configs/planck_plc_paths.json")
    return PlanckPLC(like_paths, verbose=False)


def build_cls_dict(repo: DataRepository):
    ell, cls = repo.load_planck_baseline()
    out = {"ell": ell, "TT": cls['TT'], "TE": cls['TE'], "EE": cls['EE']}
    # Optional lensing PP if present in NPZ
    try:
        data = np.load(repo.path('planck_baseline_cls.npz'))
        if 'clpp' in data:
            out['PP'] = data['clpp']
    except Exception:
        pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default=str(REPO_ROOT / 'configs' / 'planck_plc_paths.json'),
                    help='Path to JSON file with PLC likelihood paths')
    ap.add_argument('--quick', action='store_true', help='Run fewer steps for a smoke test')
    args = ap.parse_args()

    out_dir = REPO_ROOT / 'outputs' / 'plc'
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load likelihood and baseline
    plc = load_plc(Path(args.config))
    repo = DataRepository(REPO_ROOT / 'data')
    baseline = build_cls_dict(repo)

    # Baseline evaluation (θ = 0,0,0)
    base_nll = plc.nll(baseline, units='muK')

    # Define loglike with current phenomenological modifications
    def loglike(theta):
        mu0, Sigma0, xi = theta
        lg = LGPDParams(xi_damp=xi)
        cp = CondensateParams(mu0=mu0)
        ep = ElasticityParams(sigma0=Sigma0)
        T = LGPDTransfer(lg, cp, ep)
        cls_mod = apply_modifications(baseline['ell'], {k: baseline[k] for k in ['TT','TE','EE']}, T)
        cls_for_plc = {"ell": baseline['ell'], "TT": cls_mod['TT'], "TE": cls_mod['TE'], "EE": cls_mod['EE']}
        if 'PP' in baseline:
            cls_for_plc['PP'] = baseline['PP']
        nll = plc.nll(cls_for_plc, units='muK')
        return -0.5 * nll

    # MCMC settings
    theta0 = np.array([0.0, 0.0, 0.01])
    priors = [(-0.6, 0.6), (-0.6, 0.6), (0.0, 0.05)]
    nsteps = 300 if args.quick else 800

    chain, lnp, sampler = run_emcee(loglike, theta0, priors, nwalkers=24, nsteps=nsteps, nburn=100)
    best = int(np.argmax(lnp))
    best_theta = chain[best]
    best_nll = -2 * lnp[best]

    # Save outputs
    np.savez(out_dir / 'posterior_plc.npz', chain=chain, log_prob=lnp, param_names=np.array(['mu0','Sigma0','xi_damp']),
             base_nll=base_nll, best_theta=best_theta, best_nll=best_nll)

    with open(out_dir / 'summary.txt', 'w') as f:
        f.write("PLANCK PLC FIT SUMMARY\n")
        f.write("========================\n\n")
        f.write(f"Baseline -2lnL (theta=0,0,0): {base_nll:.2f}\n")
        f.write(f"Best -2lnL: {best_nll:.2f}\n")
        f.write(f"Best theta: mu0={best_theta[0]:.4f}, Sigma0={best_theta[1]:.4f}, xi={best_theta[2]:.4f}\n")

    print("Done. Results in:", out_dir)

if __name__ == '__main__':
    main()
