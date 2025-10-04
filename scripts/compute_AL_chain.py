#!/usr/bin/env python3
"""
Compute effective lensing amplitude A_L proxy from the posterior and write a new NPZ.

Reads:
  - posterior .npz with keys:
      chain: (N,3) [mu0, sigma0, xi_damp]
      log_prob or logprob: sampler log-probabilities (optional)
Writes:
  - output .npz with keys: chain, log_prob, A_L_chain

Usage:
  python scripts/compute_AL_chain.py --posterior outputs/multiprobe/multiprobe_posterior.npz --out outputs/multiprobe/posterior_with_AL.npz
"""
import argparse
import numpy as np

from lgpd_cosmo.models import ElasticityParams, sigma_kz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--posterior', required=True, help='Input posterior .npz with chain')
    ap.add_argument('--out', required=True, help='Output .npz to write (with A_L_chain)')
    args = ap.parse_args()

    post = np.load(args.posterior, allow_pickle=True)
    chain = np.asarray(post['chain'])
    # support both log_prob and logprob
    logp = None
    if 'log_prob' in post:
        logp = np.asarray(post['log_prob'])
    elif 'logprob' in post:
        logp = np.asarray(post['logprob'])

    # chain order: [mu0, sigma0, xi_damp]
    # A_L proxy: 1 + Sigma(k=0.1 h/Mpc, z=2)
    k_ref = 0.1
    z_ref = 2.0
    A_L_chain = []
    for i in range(chain.shape[0]):
        sigma0 = chain[i, 1]
        elas = ElasticityParams(sigma0=sigma0, k0=0.1, m=2.0, zt=1.5, n=3.0)
        sig = sigma_kz(k_ref, z_ref, elas)
        A_L_chain.append(1.0 + sig)
    A_L_chain = np.array(A_L_chain)

    save_kwargs = {'chain': chain, 'A_L_chain': A_L_chain}
    if logp is not None:
        save_kwargs['log_prob'] = logp

    np.savez(args.out, **save_kwargs)
    print(f"Added A_L_chain to {args.out}")
    print(f"A_L median={np.median(A_L_chain):.4f}, 68% CI=[{np.percentile(A_L_chain,16):.4f}, {np.percentile(A_L_chain,84):.4f}]")


if __name__ == '__main__':
    main()
