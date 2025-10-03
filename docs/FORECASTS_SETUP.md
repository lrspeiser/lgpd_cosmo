# Forecasts Setup (SO / CMB-S4 / Euclid / DESI / Rubin)

Purpose
- Provide a clear path to survey-realistic forecasts once a Boltzmann-consistent implementation is available.

High-level plan
1) Boltzmann-consistent spectra and growth
   - Implement μ/Σ/LGPD in CLASS/CAMB or via EFT interfaces (EFTCAMB/hi_class)
   - Validate linear theory against internal checks and limiting cases

2) Survey specifications and noise models
   - CMB (SO, CMB-S4): beams, noise curves (TT/EE), sky fraction, multipole ranges, foreground residual models
   - LSS (DESI, Euclid, Rubin): n(z), bias models, shot noise, systematics priors

3) Fisher or simulation-based pipelines
   - Build Fisher matrices for (μ0, Σ0, ξ_damp) or binned μ(a,k), Σ(a,k)
   - For LSS, include scale cuts consistent with theory accuracy
   - Optionally, end-to-end mocks for a few configurations

4) Outputs
   - Forecasted errors and parameter correlations
   - Figures demonstrating detectability and degeneracies

Repository organization
- docs/FORECASTS_SETUP.md (this file)
- scripts/forecasts/ (future): instrument configs and Fisher scripts

Notes
- Avoid over-claiming forecasted precision until Boltzmann-consistent implementation is in place.
- Keep forecast assumptions transparent and version-controlled.