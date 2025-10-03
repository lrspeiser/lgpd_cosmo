# Solar-system and Strong-field Constraints (PPN)

This module will collect Post-Newtonian (PPN) and strong-field consistency checks
for the LGPD phenomenology.

Status
- Mapping from (μ, Σ, ξ_damp, etc.) to PPN parameters (γ, β) is model-dependent
  and requires a microphysical or EFT mapping. We document placeholders and
  raise NotImplementedError where appropriate to avoid silent assumptions.

References
- Will (2014) Living Reviews in Relativity: The Confrontation between GR and Experiment
- Cassini bound on γ−1 ~ 10^−5; LLR, ephemerides constraints on β, Nordtvedt parameter

Usage
- Import and call the exposed functions once a mapping is defined.
