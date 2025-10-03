# README_DATA.md

Comprehensive guide to obtaining and converting observational data for the lgpd_cosmo pipeline.

---

## Overview

This repo expects data files under `data/` with the following structure:

- `data/planck_baseline_cls.npz` — baseline ΛCDM Cℓ from CAMB/CLASS (required)
- `data/planck_tt_binned.csv`, `data/planck_te_binned.csv`, `data/planck_ee_binned.csv` — binned CMB bandpowers (optional; can be synthetic or real)
- `data/planck_*_cov.csv` — covariance matrices for the above (recommended for proper likelihood)
- `data/bao_*.csv`, `data/sne_*.csv`, `data/growth_*.csv` — late-time probes with columns `z, observable, sigma` (and optional covariance files)

Below are detailed instructions for obtaining each dataset and converting it to the expected format.

---

## 1. Baseline ΛCDM Cℓ (theory)

### Option A: CAMB (easiest)

```bash
# Already set up in the repo
python scripts/make_planck_cls_camb.py --lmax 3000 --out data/planck_baseline_cls.npz
```

This generates: `ell, cltt, clte, clee, clbb` in the NPZ.

### Option B: CLASS

Install CLASS with Python bindings (classy), then:

```bash
python scripts/make_planck_cls_class.py --lmax 3000 --out data/planck_baseline_cls.npz
```

Adjust cosmological parameters in the script (default: Planck 2018 TT,TE,EE+lowE+lensing best-fit).

---

## 2. Planck CMB bandpowers (real data)

### Sources

Official Planck 2018 products are available from the [Planck Legacy Archive (PLA)](https://pla.esac.esa.int/).

**High-ℓ likelihoods:**
- **Plik** (TT, TE, EE): `COM_Likelihood_Data-baseline_R3.00.tar.gz`
- **CamSpec** (alternative): available via separate release

**Low-ℓ likelihoods:**
- Commander (TT at ℓ < 30)
- SimAll (EE at ℓ < 30)

**Lensing:**
- `COM_Lensing_Szdeproj-smica_R3.00.tar.gz` for lensing potential power spectrum

### Convert FITS → NPZ

For Plik TT/TE/EE bandpowers:

1. Download and extract Plik FITS products from PLA.
2. Identify the FITS file containing bandpowers (e.g., `cl_cmb_plik_v22_TT.fits`).
3. Convert:

```bash
pip install astropy  # if not already installed
python scripts/planck_fits_to_npz.py \
  COM_PowerSpect_CMB-TT-loL-full_R3.01.fits \
  --out data/planck_tt.npz
```

Repeat for TE and EE.

### Convert NPZ → binned CSV

```bash
python scripts/make_binned_csv_from_npz.py \
  --npz data/planck_tt.npz \
  --out_prefix data/planck_tt \
  --step 30
```

This produces `data/planck_tt_binned.csv` with columns: `ell, Dl, sigma`.

### Covariance matrices

Planck releases include covariance matrices. Typical structure:

- TT: (N_bins_TT, N_bins_TT)
- TE: (N_bins_TE, N_bins_TE) or joint (TT+TE)
- EE: (N_bins_EE, N_bins_EE)

Convert FITS covariance → CSV:

```bash
# Pseudo-code example
python -c "
from astropy.io import fits
import numpy as np
data = fits.open('covariance_plik_TT.fits')[1].data
cov = np.array(data['COVARIANCE'])
np.savetxt('data/planck_tt_cov.csv', cov, delimiter=',')
"
```

Then use `scripts/likelihood_binned_cov.py` (or extend `likelihoods.py`) to compute χ² with full covariance.

---

## 3. BAO (Baryon Acoustic Oscillations)

### Sources

**BOSS DR12:**
- [https://data.sdss.org/sas/dr12/boss/lss/](https://data.sdss.org/sas/dr12/boss/lss/)
- Compressed distance measurements: `DV/rd`, `DA/rd`, `H*rd` at various z

**eBOSS DR16:**
- [https://data.sdss.org/sas/dr16/eboss/lss/](https://data.sdss.org/sas/dr16/eboss/lss/)

**DESI (2024 onward):**
- [https://data.desi.lbl.gov/public/](https://data.desi.lbl.gov/public/)

### Expected format

CSV with columns: `z, DV_over_rd, sigma` (or similar depending on observable).

Example:

```csv
z,DV_over_rd,sigma
0.38,1512.3,25.0
0.51,1975.2,30.0
0.61,2140.5,35.0
```

For covariance: if the release provides a covariance matrix across z bins, save as `data/bao_cov.csv`.

### Conversion

If you have a FITS table:

```bash
python scripts/planck_ascii_to_npz.py \
  bao_dr12.dat \
  --out data/bao_dr12.csv
# Manually edit CSV header to match expected columns if needed
```

---

## 4. SNe (Type Ia Supernovae)

### Sources

**Pantheon:**
- [https://github.com/dscolnic/Pantheon](https://github.com/dscolnic/Pantheon)
- File: `lcparam_full_long.txt` (distance moduli with covariance)

**Pantheon+:**
- [https://pantheonplussh0es.github.io/](https://pantheonplussh0es.github.io/)

**Union2.1 / Union3:**
- [https://supernova.lbl.gov/union/](https://supernova.lbl.gov/union/)

### Expected format

CSV: `z, mu, sigma` (distance modulus and 1σ uncertainty).

Example:

```csv
z,mu,sigma
0.010,33.24,0.15
0.015,34.56,0.18
...
```

Covariance (if available): `data/sne_cov.csv` (N_sne × N_sne).

### Conversion

Pantheon includes a covariance matrix (`sys_full_long.txt`). Extract z, mu, diag(cov) for a simple diagonal likelihood, or use the full covariance for proper analysis:

```bash
# Example pseudo-code
python -c "
import pandas as pd
import numpy as np
df = pd.read_csv('lcparam_full_long.txt', delim_whitespace=True)
df[['zHD','MU','MUERR']].to_csv('data/sne_pantheon.csv', header=['z','mu','sigma'], index=False)
"
```

---

## 5. Growth (fσ8)

### Sources

**Compilations:**
- Sánchez et al. (2017): [arXiv:1607.03155](https://arxiv.org/abs/1607.03155)
- Howlett et al. (2018): [arXiv:1801.09534](https://arxiv.org/abs/1801.09534)
- BOSS/eBOSS: [https://data.sdss.org/sas/dr16/eboss/lss/](https://data.sdss.org/sas/dr16/eboss/lss/)

### Expected format

CSV: `z, fsigma8, sigma`.

Example:

```csv
z,fsigma8,sigma
0.15,0.490,0.045
0.38,0.497,0.045
0.51,0.458,0.038
0.61,0.436,0.034
```

Covariance (if available): `data/growth_cov.csv`.

### Conversion

If you have a table from a paper or a FITS file:

```bash
# Manually create CSV from the published table, or use a converter
python -c "
import numpy as np
# Example data from Sánchez+2017
data = [
    (0.15, 0.490, 0.045),
    (0.38, 0.497, 0.045),
    (0.51, 0.458, 0.038),
    (0.61, 0.436, 0.034),
]
np.savetxt('data/growth_compilation.csv', data, delimiter=',', header='z,fsigma8,sigma', comments='')
"
```

---

## 6. Planck lensing

### Sources

- `COM_Lensing_Szdeproj-smica_R3.00.tar.gz` from PLA
- File: `dat_klm.fits` (lensing potential power spectrum Cℓ^ϕϕ)

### Expected format

NPZ: `ell, cl_pp` (or CSV: `ell, Cl, sigma`).

### Conversion

```bash
python -c "
from astropy.io import fits
import numpy as np
hdul = fits.open('dat_klm.fits')
data = hdul[1].data
ell = data['ELL']
clpp = data['CLPP']
np.savez('data/planck_lensing.npz', ell=ell, clpp=clpp)
"
```

---

## Summary checklist

- [ ] `data/planck_baseline_cls.npz` (CAMB or CLASS)
- [ ] `data/planck_tt_binned.csv`, `data/planck_te_binned.csv`, `data/planck_ee_binned.csv` (real Planck bandpowers)
- [ ] `data/planck_tt_cov.csv`, `data/planck_te_cov.csv`, `data/planck_ee_cov.csv` (covariances)
- [ ] `data/bao_*.csv` (BOSS/eBOSS/DESI BAO measurements)
- [ ] `data/sne_*.csv` (Pantheon/Pantheon+ SNe)
- [ ] `data/growth_*.csv` (fσ8 compilation)
- [ ] `data/planck_lensing.npz` (optional: lensing potential)

Once these files are in place, the pipeline scripts (`examples/fit_with_real_data.py`, `run_full_pipeline.sh`) will automatically use them.

---

## References

- Planck Legacy Archive: [https://pla.esac.esa.int/](https://pla.esac.esa.int/)
- CAMB: [https://camb.info/](https://camb.info/)
- CLASS: [http://class-code.net/](http://class-code.net/)
- BOSS/eBOSS: [https://www.sdss.org/dr16/](https://www.sdss.org/dr16/)
- Pantheon: [https://github.com/dscolnic/Pantheon](https://github.com/dscolnic/Pantheon)
- Pantheon+: [https://pantheonplussh0es.github.io/](https://pantheonplussh0es.github.io/)
