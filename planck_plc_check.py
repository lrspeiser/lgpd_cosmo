
#!/usr/bin/env python3
import os, sys, argparse, numpy as np
sys.path.insert(0, os.path.dirname(__file__))  # allow local import if needed

def main():
    ap = argparse.ArgumentParser(description="Sanity test: load PLC likelihood(s) and evaluate at a toy spectrum.")
    ap.add_argument("--highl", help="Path to high-l TTTEEE .clik", required=False)
    ap.add_argument("--lowl_tt", help="Path to low-l TT .clik", required=False)
    ap.add_argument("--lowl_ee", help="Path to low-l EE .clik", required=False)
    ap.add_argument("--lensing", help="Path to lensing .clik_lensing", required=False)
    args = ap.parse_args()

    try:
        from lgpd_cosmo.planck_plc import PlanckPLC
    except Exception:
        # fallback if user placed adapter next to this script
        from planck_plc import PlanckPLC

    like_paths = {}
    if args.highl: like_paths["highl_TTTEEE"] = args.highl
    if args.lowl_tt: like_paths["lowl_TT"] = args.lowl_tt
    if args.lowl_ee: like_paths["lowl_EE"] = args.lowl_ee
    if args.lensing: like_paths["lensing"] = args.lensing
    if not like_paths:
        raise SystemExit("Provide at least one likelihood path.")

    plc = PlanckPLC(like_paths, verbose=True)

    # Very small toy spectra just to exercise the code path; NOT for science.
    lmax = 4096
    ell = np.arange(0, lmax+1)
    tiny = 1e-20  # K^2
    cltt = tiny*np.ones_like(ell)
    clee = tiny*np.ones_like(ell)
    clte = np.zeros_like(ell)
    clbb = np.zeros_like(ell)
    clpp = tiny*np.ones_like(ell)

    cls = {"ell": ell, "TT": cltt, "EE": clee, "TE": clte, "BB": clbb, "PP": clpp}
    nll = plc.nll(cls, units="K")
    print(f"Total -2lnL (toy): {nll:.3f}")

if __name__ == "__main__":
    main()
