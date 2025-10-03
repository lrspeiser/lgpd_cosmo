
# lgpd_cosmo

A lightweight research codebase to explore **Low-Gravity Photonic Decoherence (LGPD)** and related
"spacetime unravels in weak gravity" models:

- **LGPD**: gravity-triggered decoherence/thermalization of photons with a blackbody fixed point.
- **Condensate**: gravity-as-a-phase; modifies the Poisson equation via a scale/redshift response μ(k, z).
- **Cosmic Elasticity**: elastic spacetime with anisotropic stress Σ(k, z) and a yield-triggered negative pressure.
- **Threadbare Coherence**: finite metric coherence length ℓ_c controlling large-scale responses.

This repo provides:
- Phenomenological parameterizations — μ(k, z), Σ(k, z), Γ(z) — compatible with linear cosmology.
- A simple background integrator and growth calculator (Eisenstein & Hu–style approximations).
- A CMB module that **modulates baseline ΛCDM C_ℓ** (from CAMB/CLASS or provided .npz) to emulate the phenomenology.
- Likelihood stubs for Planck TT/TE/EE, BAO, SNe, and CMB lensing (**expects user-provided data files**).
- `emcee` MCMC driver and plotting utilities.

> **Note:** This is a *phenomenology* sandbox. For high-precision fits, connect to CLASS or CAMB
and implement the modified Boltzmann hierarchy directly. Hooks are provided.

## Install

```bash
pip install -e .
```

(Or just use the package in-place by setting `PYTHONPATH`.)

## Data layout

Place public data under `data/` with the following expected file patterns:

- `data/planck_baseline_cls.npz` : numpy `.npz` with arrays:
  - `ell` (ℓ), `cltt`, `clte`, `clee`, `clbb` (optional), `clpp` (lensing potential).
- (Optional simple likelihoods)
  - `data/planck_tt_binned.csv` : columns `ell, Dl, sigma`
  - `data/planck_te_binned.csv` : `ell, Dl, sigma`
  - `data/planck_ee_binned.csv` : `ell, Dl, sigma`
- BAO (ASCII/CSV): `z, DV_over_rd, sigma`
- SNe (Pantheon-like): `z, mu, sigma`
- Growth: `z, fsigma8, sigma`

You can generate a **synthetic** baseline with `examples/run_demo.py`.

## Quick start (synthetic demo)

```bash
python examples/run_demo.py
```

This will:
- generate a toy ΛCDM baseline C_ℓ,
- apply LGPD + μ/Σ modifications,
- plot comparative spectra,
- run a tiny MCMC against synthetic "Planck-like" binned data.

## Connecting to CLASS

If you have CLASS installed with Python bindings:

```python
from lgpd_cosmo.cmb import get_baseline_cls_from_class
ells, cls = get_baseline_cls_from_class(cosmoparams=dict(ombh2=0.0224, omch2=0.12, H0=67.7))
```

Then save with `np.savez` for repeatable runs.

## References

See `paper/lgpd_unraveling_cosmology.tex` for the conceptual framework and citations.
