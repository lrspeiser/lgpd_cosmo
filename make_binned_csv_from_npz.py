
#!/usr/bin/env python3
import argparse, numpy as np, os, csv

def Dl(ell, Cl): 
    return ell*(ell+1.0)*Cl/(2*np.pi)

def bin_edges(lmin, lmax, step):
    edges = list(range(lmin, lmax+1, step))
    if edges[-1] < lmax: edges.append(lmax)
    return np.array(edges)

def bin_average(ell, Dl, edges):
    ells_c = []
    Dl_c = []
    sig_c = []
    for i in range(len(edges)-1):
        lo, hi = edges[i], edges[i+1]
        m = (ell >= lo) & (ell < hi)
        if not np.any(m): 
            continue
        ells_c.append(int(np.mean(ell[m])))
        vals = Dl[m]
        Dl_c.append(float(np.mean(vals)))
        # toy sigma: 5% of mean + small floor
        sig_c.append(float(0.05*np.mean(vals) + 1.0))
    return np.array(ells_c), np.array(Dl_c), np.array(sig_c)

def main():
    ap = argparse.ArgumentParser(description="Make simple binned CSVs (ell, Dl, sigma) from NPZ C_ell.")
    ap.add_argument("--npz", required=True, help="Input NPZ with arrays: ell, and cltt/clte/clee")
    ap.add_argument("--out_prefix", required=True, help="Output CSV prefix")
    ap.add_argument("--step", type=int, default=30, help="ell bin step (default 30)")
    args = ap.parse_args()

    data = np.load(args.npz)
    ell = data["ell"]
    outputs = []
    for key in ("cltt","clte","clee"):
        if key not in data:
            continue
        Dl_arr = Dl(ell, data[key])
        edges = bin_edges(int(ell.min()), int(ell.max()), args.step)
        ells_c, Dl_c, sig_c = bin_average(ell, Dl_arr, edges)
        band = key[2:].upper()
        out_csv = f"{args.out_prefix}_{band.lower()}_binned.csv"
        with open(out_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["ell","Dl","sigma"])
            for L, d, s in zip(ells_c, Dl_c, sig_c):
                w.writerow([L, d, s])
        outputs.append(out_csv)
        print("Wrote", out_csv, "with", len(ells_c), "bands.")
    if not outputs:
        print("No Cl arrays found in npz.")

if __name__ == "__main__":
    main()
