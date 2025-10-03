# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Repository overview
- Language: Python
- Package: lgpd_cosmo
- Purpose: Phenomenology sandbox for Low-Gravity Photonic Decoherence (LGPD) and related modified-gravity models. Provides parameterizations (μ, Σ, Γ), background/growth utilities, CMB spectrum modulation, simple likelihoods, an emcee-based MCMC driver, and plotting helpers.

Quick commands
- Create a virtual environment and install in editable mode
  - python -m venv .venv
  - source .venv/bin/activate
  - pip install -e .
  - Optional (reproduce a pinned environment): pip install -r requirements.freeze.txt

- Run the synthetic demo (generates toy baseline, applies LGPD/μ/Σ, plots, and runs a small MCMC)
  - python examples/run_demo.py

- Run against real data (expects files in data/; see Data layout below)
  - python examples/fit_with_real_data.py

- Build distribution artifacts (no pyproject; uses setup.py)
  - python -m pip install build
  - python -m build
  - Or: python setup.py sdist bdist_wheel

- Lint and tests
  - Lint: not configured in this repo
  - Tests: no tests/ folder or pytest configuration present; use the examples as smoke tests

Data layout (expected files)
- Place public data under data/
  - planck_baseline_cls.npz with arrays: ell, cltt, clte, clee (optional: clbb, clpp)
  - Optional simple binned spectra (CSV with header): planck_tt_binned.csv, planck_te_binned.csv, planck_ee_binned.csv with columns ell, Dl, sigma
  - BAO (CSV): z, DV_over_rd, sigma
  - SNe (CSV): z, mu, sigma
  - Growth (CSV): z, fsigma8, sigma
- You can generate a synthetic baseline by running the demo (see above)

Big-picture architecture and flow
- Parameterizations (lgpd_cosmo/models.py)
  - LGPDParams: decoherence parameters (Γ(a), damping envelope via xi_damp)
  - CondensateParams: μ(k, z), modifies Newtonian potential
  - ElasticityParams: Σ(k, z), effective lensing/anisotropic stress
  - ThreadbareParams: coherence length ℓ_c(z)
  - Utility functions: mu_kz, sigma_kz, gamma_of_a, coherence_length
  - LGPDTransfer: collects parameters and exposes transfer functions used by observables (e.g., Dl_mod_factor, lensing_amp)

- Background and growth (lgpd_cosmo/background.py, lgpd_cosmo/linear.py)
  - LCDM: H(z), distances, and CPL-like w(a) via w_eff; linear.py provides a GrowthModel (D(a), fσ8) used by simple likelihoods

- CMB modulation (lgpd_cosmo/cmb.py)
  - load_baseline_cls: loads baseline Cl from .npz (or use get_baseline_cls_from_class if CLASS is available)
  - apply_modifications: applies phenomenological LGPD + μ/Σ effects to produce modified Cl; internally works in Dl and converts back to Cl

- Data IO and likelihoods (lgpd_cosmo/data.py, lgpd_cosmo/likelihoods.py)
  - DataRepository: typed loaders for baseline Cls and CSV datasets (binned TT/TE/EE, BAO, SNe, growth)
  - Likelihoods: accumulator computing simple χ² terms (Planck-simple, BAO, SNe, growth) and providing summaries

- Inference and plotting (lgpd_cosmo/mcmc.py, lgpd_cosmo/plotting.py)
  - run_emcee: convenience wrapper to run emcee given a log-like function, priors, and initial state
  - plotting: helpers to visualize Cl spectra and Γ(a)

Typical pipeline (as used in examples)
1) Load baseline Cℓ (DataRepository.load_planck_baseline or a synthetic baseline from the demo)
2) Construct LGPDParams, CondensateParams, ElasticityParams (optionally ThreadbareParams) and bundle them in LGPDTransfer
3) Apply the transfer to baseline Cℓ with apply_modifications to get modified spectra
4) Form a simple likelihood (e.g., Planck TT binned) via Likelihoods and define a log-like
5) Run MCMC with run_emcee; save and/or plot results

Notes and pitfalls
- emcee: If not installed, a crude random prior scan path is used as a fallback in mcmc.py; for reproducible and statistically meaningful inference, install emcee (pip install emcee)
- CLASS: Optional; get_baseline_cls_from_class will warn and return (None, None) if CLASS is unavailable. Precompute and cache baseline Cℓ with numpy if you want repeatable runs without CLASS.
- No CI or linting config is present; style and checks are ad-hoc. Use the examples as smoke tests after changes.
