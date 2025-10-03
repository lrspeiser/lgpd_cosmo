
#!/usr/bin/env python3

import numpy as np, argparse, json, os, sys

def load_csv(path):
    # expect header: ell, Dl, sigma  OR arbitrary 3 cols
    arr = np.loadtxt(path, delimiter=",", skiprows=1)
    return arr[:,0], arr[:,1], arr[:,2]

def load_cov(path):
    # simple CSV covariance matrix (NxN)
    return np.loadtxt(path, delimiter=",", skiprows=0)

def chi2_block(Dl_model_interp, Dl_data, cov=None, sigma=None):
    if cov is not None:
        resid = (Dl_data - Dl_model_interp)
        try:
            icov = np.linalg.inv(cov)
        except np.linalg.LinAlgError:
            icov = np.linalg.pinv(cov)
        return float(resid @ icov @ resid)
    elif sigma is not None:
        return float(np.sum(((Dl_data - Dl_model_interp)/sigma)**2))
    else:
        raise ValueError("Provide either cov or sigma.")

def main():
    ap = argparse.ArgumentParser(description="Compute chi2 for binned bandpowers with covariance.")
    ap.add_argument("--csv", required=True, help="binned CSV: ell,Dl,sigma")
    ap.add_argument("--model_csv", required=True, help="model CSV: ell,Dl (same bins)")
    ap.add_argument("--cov", default=None, help="optional covariance CSV (NxN)")
    args = ap.parse_args()
    le, de, se = load_csv(args.csv)
    lm, dm, _ = load_csv(args.model_csv)
    if not np.allclose(le, lm):
        raise SystemExit("Model ℓ grid must match data bins.")
    cov = load_cov(args.cov) if args.cov else None
    chi2 = chi2_block(dm, de, cov=cov, sigma=se if cov is None else None)
    print(json.dumps({"chi2": chi2, "Ndof": int(len(le))}, indent=2))

if __name__ == "__main__":
    main()
