
#!/usr/bin/env python3

import argparse, numpy as np, json, os, sys

def load_chain(path):
    dat = np.load(path)
    chain = dat["chain"]  # (Nsamp, Npar) OR (Nwalkers, Nsteps, Npar) -- we support flat (Nsamp, Npar)
    logp  = dat.get("logprob", None)
    return chain, logp

def split_rhat(chain):
    """
    Approximate split-Rhat using one chain split into 2 halves.
    If you have multiple parallel chains, concatenate them along axis=0 first.
    chain: (Nsamp, D)
    """
    chain = np.asarray(chain)
    Ns, D = chain.shape
    half = Ns//2
    A = chain[:half, :]
    B = chain[half:2*half, :]
    def _rhat_2(A, B):
        # Gelman-Rubin for 2 chains
        m = 2
        n = A.shape[0]
        mA = A.mean(axis=0)
        mB = B.mean(axis=0)
        mbar = (mA + mB)/2.0
        W = ( ((A - mA)**2).sum(axis=0) + ((B - mB)**2).sum(axis=0) ) / (m*(n-1))
        Bn = n * ( (mA - mbar)**2 + (mB - mbar)**2 )
        var_hat = ((n-1)/n)*W + (1/n)*Bn
        Rhat = np.sqrt(var_hat / W)
        return Rhat
    return _rhat_2(A, B)

def autocorr_time(chain):
    """
    Try emcee's integrated autocorrelation time; fallback to a simple estimate if not available.
    """
    try:
        import emcee
        # emcee expects (nsteps, nwalkers, ndim) typically; we only have flattened samples.
        # We'll just return NaNs to avoid misleading values.
        return np.full(chain.shape[1], np.nan)
    except Exception:
        return np.full(chain.shape[1], np.nan)

def main():
    ap = argparse.ArgumentParser(description="Posterior diagnostics: split-Rhat, logprob stats")
    ap.add_argument("--posterior", required=True, help="path to posterior.npz")
    ap.add_argument("--out", default=None, help="json output path (default: alongside posterior)")
    args = ap.parse_args()

    chain, logp = load_chain(args.posterior)
    rhat = split_rhat(chain)
    out = {
        "Nsamp": int(chain.shape[0]),
        "Npar": int(chain.shape[1]),
        "split_Rhat": rhat.tolist(),
    }
    if logp is not None:
        out["logprob"] = {
            "mean": float(np.mean(logp)),
            "max": float(np.max(logp)),
            "min": float(np.min(logp))
        }
    p = args.out or os.path.join(os.path.dirname(args.posterior), "diagnostics.json")
    with open(p, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
