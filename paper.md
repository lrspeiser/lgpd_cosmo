# LGPD: Unraveling Cosmology with Γ(a)

## Hypothesis
Test whether ΛCDM departures parameterized via LGPD Γ(a) and related μ/Σ mapping are detectable in synthetic CMB power spectra and growth observables using an MCMC approach.

## Methods
- Parameterization: Γ(a) with damping envelope; μ(k,z), Σ(k,z) mappings; linear growth model as implemented in lgpd_cosmo/.
- Likelihoods: synthetic Cℓ TT/TE/EE baseline with additive/modulative LGPD effects.
- Sampler: emcee; flat priors per code defaults; random-scan fallback disabled in favor of explicit errors if emcee unavailable.
- Logging: Verbose stdout captured to examples/_demo_outputs/*.log; no silent fallbacks.

## Implementation and Environment
- Code layout: lgpd_cosmo/ (core), examples/, data/, paper/.
- Python: 3.13.5 (local .venv)
- Key packages: numpy, scipy, matplotlib, emcee.
- Exact environment: requirements.freeze.txt (tracked in repo).

## Data
- Synthetic CMB Cℓ baseline generated in examples/run_demo.py.
- Real-data placeholder: data/planck_baseline_cls.npz expected with arrays: ell, cltt, clte, clee.

## Experiments
### Synthetic demo
- Command: python examples/run_demo.py
- Log: examples/_demo_outputs/run_demo.log
- Outputs:
  - examples/_demo_outputs/cls_demo.png
  - examples/_demo_outputs/gamma_demo.png
  - examples/_demo_outputs/mcmc_chain.npz

## Results and Interpretation
- Inspect TT/TE/EE comparison and Γ(a) evolution to verify qualitative signatures.
- Posterior sample (tiny, synthetic) saved for sanity; not a precision inference.

## Issues and Fixes
- Duplicate files at repo root (older copies of demo outputs and paper sources) moved into legacy_not_in_use/ to prevent confusion.

## Next Steps
- Add Planck-like baseline Cℓ generated via CLASS (preferred) or CAMB stand-in; commit via LFS.
- Run examples/fit_with_real_data.py and append fit logs/plots; describe parameter constraints.
- Explore sensitivity to Γ(a) shape parameters and μ/Σ couplings; document any degeneracies.