# Testing gravitational modifications at cosmic scales: constraints from CMB lensing and photon decoherence

Authors: Leonard Speiser, Collaborators  
Date: 2025-10-03

Abstract
The Planck CMB power spectra prefer a lensing amplitude exceeding the ΛCDM prediction (A_L > 1) at ~2–3σ, while lensing reconstruction and LSS are close to A_L ≃ 1. We test whether ultra-weak-gravity departures from GR—encoded by scale- and redshift-dependent response functions μ(k,z) and Σ(k,z)—together with a Low-Gravity Photonic Decoherence (LGPD) mechanism, can reconcile these datasets without spoiling strong-field tests. LGPD is modeled via a Lindblad operator that, in low-acceleration environments, drives the photon field toward a Planckian fixed point and introduces a small, frequency-independent damping envelope for anisotropies. We confront the model with Planck TT/TE/EE (+lensing), BAO, SNe, and fσ8. In a preliminary fit to synthetic bandpowers we find constraints consistent with ΛCDM (illustrative only), and outline a Boltzmann-consistent pipeline that will deliver bounds on (μ, Σ, Γ). We conclude with falsifiable predictions and discuss prospects for SO, CMB-S4, and Euclid.

1. Introduction
The CMB provides a precise window into the early Universe (Planck 2018). Within ΛCDM, we have a concordance cosmology, but tensions persist: H0, σ8, and particularly the A_L anomaly where Planck TT/TE/EE favor A_L > 1 at ~2.8σ. Explanations span systematics, modified neutrino physics, early dark energy, and modified gravity. We explore a phenomenological framework combining:
- Low-Gravity Photonic Decoherence (LGPD): environment-induced decoherence in ultra-weak gravity, introducing a small, frequency-independent anisotropy-damping envelope characterized by ξ_damp and a rate Γ(a).
- Modified linear response: scale- and redshift-dependent μ(k,z) and Σ(k,z) altering growth (μ) and the Weyl potential/lensing (Σ).
Key questions: Can these effects reconcile A_L with other observables? What are the tightest bounds from current data? Are they consistent with Solar System, BBN, and spectral-distortion limits? What do they predict for upcoming surveys?

2. Theory: LGPD and modified linear response
- LGPD: Photons as an open quantum system evolving under a Lindblad equation with a rate Γ(a) that activates only in ultra-weak gravity. In anisotropies, LGPD yields a frequency-independent damping envelope D_ℓ = exp[− ξ_damp ℓ(ℓ+1)/ℓ_d^2] with small ξ_damp to preserve TE/EE phases and the damping tail; ℓ_d ~ O(10^3–10^4). Consistency requires vanishing in strong fields and preserving the near-perfect blackbody spectrum (|μ|, |y| ≲ 1e−5).
- Modified gravity response: We parameterize departures from GR via
  - k^2 Φ = 4πG a^2 ρ Δ [1 + μ(k,z)]
  - Φ + Ψ = [1 + Σ(k,z)] (Φ + Ψ)_GR
  with smooth transitions in k and z controlled by parameters (μ0, Σ0, k0, m, z_t, n). Σ primarily impacts CMB lensing and A_L-like smoothing of acoustic peaks; μ alters growth and fσ8.

3. Data and likelihood
- CMB: Planck 2018 high-ℓ TT/TE/EE with covariances and window functions; low-ℓ polarization for τ; lensing reconstruction C_L^{φφ}.
- BAO/SNe/growth: BAO distances (6dFGS, MGS, BOSS/eBOSS), Pantheon(+), and fσ8 from RSD. We convolve theory with Planck window functions and adopt Gaussian likelihoods with priors/penalties including spectral-distortion safety for LGPD.

4. Methods and inference
- Parameters: Base cosmology plus Θ_MG = {μ0, Σ0, k0, m, z_t, n} and Θ_LGPD = {ξ_damp}. Optional (w0, wa) for sensitivity tests.
- Priors: Broad, conservative priors enforcing GR recovery and strong-field safety; ξ_damp small; spectral-distortion prior via mapping to μ/y constraints.
- Computation: Boltzmann code with (μ, Σ) in the hierarchy; lens spectra self-consistently; apply LGPD envelope; convolve to bandpowers. Compute background distances and fσ8.
- Sampling: Affine-invariant ensemble MCMC; multiple chains; convergence via split-R̂, autocorrelation, effective sample size.
- Validation: Recover ΛCDM when (μ0, Σ0, ξ_damp) = (0,0,0); then test Σ-only, then full set; robustness via priors, ℓ-cuts, dataset combinations.

5. Results
Preliminary constraints (synthetic bandpowers)
- Fit to synthetic Planck-like bandpowers (CAMB baseline, uniform ℓ-binning, diagonal errors):
  - μ0 = −0.016 [−0.203, 0.199]
  - Σ0 = 0.025 [−0.0058, 0.0624]
  - ξ_damp = 0.0036 [0.0010, 0.0075]
- Effective lensing amplitude proxy A_L^{eff} = 1.0047 [0.9989, 1.0114], consistent with unity. Constraints are largely prior-dominated; TE/EE adds modest power over TT-only.

Planck + BAO + SNe + growth (target analysis)
- To be filled with official likelihoods and covariances: marginalized constraints on (μ0, Σ0, k0, z_t, m, n, ξ_damp); Δχ² vs ΛCDM; AIC/BIC; Bayes factors; and A_L consistency between spectra and reconstruction.

6. Robustness and null tests
- ΛCDM recovery; prior sensitivity; multipole cuts; dataset combinations; growth-modeling sensitivity; spectral-distortion guardrail. Provide parameter-shift tables and residual plots.

7. Discussion and conclusions
- Physical interpretation: Σ0 enhances smoothing in lensed TT/TE/EE without necessarily shifting reconstruction by the same factor; μ0 modifies growth; ξ_damp encodes LGPD damping, constrained by spectral distortions and polarization phases.
- Comparison to alternatives: Massive neutrinos, EDE, and systematics can shift A_L; the (μ, Σ) approach isolates gravitational-response effects and tests consistency with reconstruction and growth, without necessarily altering early-time physics.
- Predictions and future tests: Frequency-independent EE suppression at low ℓ set by ξ_damp; small correlated deviations along deep-void sightlines; excess phase decoherence for FRBs/quasars through voids. Upcoming SO, CMB-S4, Euclid will tighten constraints.
- Conclusion: Preliminary synthetic tests show no spurious deviation from ΛCDM. With a Boltzmann-consistent pipeline and official Planck/BAO/SNe/growth likelihoods, we will deliver quantitative bounds on (μ0, Σ0, ξ_damp) and assess whether modified gravity and photonic decoherence can alleviate the A_L tension without harming other observables.

References
- Planck 2018 results; BAO (BOSS/eBOSS); Pantheon(+); RSD compilations; modified gravity parameterizations (μ, Σ); decoherence literature (Lindblad, gravitational decoherence).