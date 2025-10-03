#!/usr/bin/env python3
"""
Compute effective lensing amplitude A_L proxy from the posterior and add to the NPZ.

Reads:
  - examples/_real_fit/posterior.npz: chain (N,3) with [mu0, sigma0, xi_damp]
Writes (overwrites the NPZ with an additional key):
  - A_L_chain: array of length N, with A_L ~ 1 + sigma(k=0.1 h/Mpc, z=2)

Usage:
  python scripts/compute_AL_chain.py --posterior examples/_real_fit/posterior.npz
"""
import argparse
import numpy as np

from lgpd_cosmo.models import ElasticityParams, sigma_kz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--posterior', default='examples/_real_fit/posterior.npz')
    args = ap.parse_args()

    post = np.load(args.posterior)
    chain = np.asarray(post['chain'])
    logp = np.asarray(post['logprob'])

    # chain order: [mu0, sigma0, xi_damp]
    # For A_L proxy we use sigma0 and the fixed params from fit_with_real_data.py:
    # ElasticityParams(sigma0=..., k0=0.1, m=2.0, zt=1.5, n=3.0)
    # and evaluate at k=0.1, z=2.0 to get an effective lensing amplitude
    k_ref = 0.1
    z_ref = 2.0
    A_L_chain = []
    for i in range(chain.shape[0]):
        sigma0 = chain[i, 1]
        elas = ElasticityParams(sigma0=sigma0, k0=0.1, m=2.0, zt=1.5, n=3.0)
        sig = sigma_kz(k_ref, z_ref, elas)
        A_L_chain.append(1.0 + sig)
    A_L_chain = np.array(A_L_chain)

    # Overwrite NPZ with the new key
    np.savez(args.posterior.replace('.npz', '_with_AL.npz'), chain=chain, logprob=logp, A_L_chain=A_L_chain)
    print(f"Added A_L_chain to {args.posterior.replace('.npz', '_with_AL.npz')}")
    print(f"A_L median={np.median(A_L_chain):.4f}, 68% CI=[{np.percentile(A_L_chain,16):.4f}, {np.percentile(A_L_chain,84):.4f}]")


if __name__ == '__main__':
    main()
