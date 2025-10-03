#!/usr/bin/env bash
set -euo pipefail

# End-to-end pipeline for lgpd_cosmo
# Assumes data is in place (see README_DATA.md for obtaining real Planck/BAO/SNe/growth data)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${REPO_ROOT}/.venv/bin/python"
PY="${PY:-$VENV_PYTHON}"

cd "$REPO_ROOT"

echo "=== lgpd_cosmo full pipeline ==="
echo "Using Python: $PY"
echo ""

echo "[1/6] Generate baseline C_ell (CAMB)"
if [ ! -f data/planck_baseline_cls.npz ]; then
  $PY scripts/make_planck_cls_camb.py --lmax 3000 --out data/planck_baseline_cls.npz
else
  echo "  data/planck_baseline_cls.npz already exists; skipping."
fi
echo ""

echo "[2/6] Make binned CSVs from NPZ (TT/TE/EE)"
if [ ! -f data/planck_tt_binned.csv ]; then
  $PY scripts/make_binned_csv_from_npz.py --npz data/planck_baseline_cls.npz --out_prefix data/planck --step 30
else
  echo "  data/planck_tt_binned.csv already exists; skipping."
fi
echo ""

echo "[3/6] Fit model to binned TT+TE+EE (with covariances if present)"
$PY examples/fit_with_real_data.py
echo ""

echo "[4/6] Compute A_L chain (lensing amplitude proxy)"
$PY scripts/compute_AL_chain.py --posterior examples/_real_fit/posterior.npz
echo ""

echo "[5/6] Diagnostics (convergence, summary, plots)"
$PY scripts/posterior_diagnostics.py --posterior examples/_real_fit/posterior.npz --baseline data/planck_baseline_cls.npz --outdir examples/_real_fit/diagnostics
echo ""

echo "[6/6] All done. Outputs:"
echo "  - Posterior: examples/_real_fit/posterior.npz"
echo "  - A_L chain: examples/_real_fit/posterior_with_AL.npz"
echo "  - Diagnostics: examples/_real_fit/diagnostics/"
echo "  - Summary CSV: examples/_real_fit/diagnostics/posterior_summary.csv"
echo ""
echo "Next steps:"
echo "  - Inspect histograms and TT overlay in examples/_real_fit/diagnostics/"
echo "  - Ensure R-hat < 1.01 and ESS > 100 per parameter (check diagnostics JSON if added)"
echo "  - Upgrade to real Planck data (see README_DATA.md)"
echo "  - Implement μ/Σ in Boltzmann code (CLASS/hi_class or CAMB/EFTCAMB)"
echo "  - Add BAO, SNe, growth data and likelihoods"
