# Nonlinear Predictions Roadmap

This document outlines a plan to support nonlinear predictions under LGPD-like modifications.

Goals
- Provide P(k) in the nonlinear regime for comparison to weak lensing and clustering observables
- Calibrate or bound the validity of any surrogate (Halofit/Emulator) used under modified gravity

Recommended path
1) Literature review: MGHalofit and emulators
   - Assess availability of modified-gravity Halofit variants for μ/Σ-like models (e.g., MGHalofit)
   - Survey emulators (Euclid Emulator, Mira-Titan, BACCO) for extensibility to phenomenological μ/Σ

2) Define a controlled surrogate
   - Start with LCDM Halofit as an upper bound on applicability
   - Introduce a conservative prior on nonlinear boost factors driven by Σ, with an explicit “validity window”
   - Implement a runtime switch: nonlinear=off|lcdm|mg_surrogate (default off)

3) Validation strategy
   - Compare surrogate predictions against (limited) MG simulations in the literature where mappings exist
   - Quantify errors as a function of scale and redshift; expose them via error bands in plots

4) Integration points
   - lgpd_cosmo/linear.py: add hook to call a nonlinear P(k) module when enabled
   - New module: lgpd_cosmo/nonlinear.py with clear, documented interfaces

5) Deliverables
   - docs/NONLINEAR_ROADMAP.md (this file)
   - lgpd_cosmo/nonlinear.py (skeleton)
   - Command-line toggle in scripts/run_multiprobe_fit.py

Caveats
- Without MG N-body calibration, predictions beyond k~0.3 h/Mpc will carry large, model-dependent uncertainties. We will default to the safe linear-only path in all main results.
