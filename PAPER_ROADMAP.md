# PAPER ROADMAP TO SUBMISSION

**Current status:** 29% complete (883 / 3000 words)  
**Target journal:** Physical Review D or JCAP (Nature Physics requires ~90% more content)  
**Estimated time to submission-ready:** 6-10 weeks full-time

---

## IMMEDIATE PRIORITIES (Week 1-2)

### 1. Complete Core Analysis [CRITICAL]

**Status:** Phenomenological pipeline complete; needs production-quality data

**Actions:**
- [ ] Download real Planck 2018 TT/TE/EE Plik bandpowers + covariances from PLA
- [ ] Convert using `scripts/planck_fits_to_npz.py` and save covariances
- [ ] Update `likelihoods.py` to use full covariance matrices
- [ ] Add BAO (BOSS DR12), SNe (Pantheon), growth (compilation) data with covariances
- [ ] Run production MCMC: 64 walkers × 2000 steps with convergence diagnostics
- [ ] Verify R-hat < 1.01, ESS > 100 per parameter, τ < 50

**Deliverables:**
- `examples/_real_fit_production/posterior.npz` (production chain)
- `examples/_real_fit_production/diagnostics/` (all plots + summary)
- Quantitative constraints table

### 2. Write Theory Section [CRITICAL]

**Status:** 5% complete (62 / 1200 words)

**Template available:** Run `python scripts/expand_paper_sections.py --template theory` for 800-word starting point

**What to add:**
- Full mathematical development of LGPD Lindblad equation
- Physical motivation (quantum decoherence in weak gravity)
- Derivation of μ(k,z), Σ(k,z) parameterizations
- Consistency requirements (solar system, BBN, spectral distortions)
- Implementation in Boltzmann code (CLASS/hi_class modifications)

**Target:** 1200 words with 10-12 equations

### 3. Generate All Figures [CRITICAL]

**Required figures (4 minimum for PRD/JCAP):**

1. **Power spectrum fits** (`scripts/plot_power_spectra.py` - TO CREATE)
   - 3-panel: TT, TE, EE
   - Data points with error bars
   - ΛCDM (dashed) vs LGPD (solid)
   - Residuals below each

2. **Posterior corner plot** (`scripts/plot_corner.py` - TO CREATE)
   - 5×5: μ₀, Σ₀, ξ_damp, Ωₘ, h
   - 1σ and 2σ contours
   - ΛCDM comparison overlaid

3. **A_L comparison** (`scripts/plot_AL_comparison.py` - TO CREATE)
   - Your constraint vs Planck standard
   - Multiple analyses shown
   - Consistency bars

4. **Parameter evolution** (`scripts/plot_mu_sigma_evolution.py` - TO CREATE)
   - μ(k,z) and Σ(k,z) as functions of k and z
   - Highlight where effects are strongest

---

## WEEK 3-4: Content Development

### 4. Write Data & Methods Sections

**data_likelihood.tex:** 600 words
- [ ] Planck 2018 TT/TE/EE Plik details (binning, covariance, ℓ-ranges)
- [ ] Low-ℓ Commander+SimAll
- [ ] BAO: BOSS DR12 measurements table
- [ ] SNe: Pantheon sample (z range, standardization)
- [ ] Growth: fσ8 compilation table
- [ ] Likelihood construction equation

**methods_inference.tex:** 800 words
- [ ] Parameter list with priors table
- [ ] MCMC setup (emcee affine-invariant, 64 walkers, 2000 steps)
- [ ] Convergence criteria
- [ ] Computational cost (CPU-hours)
- [ ] Validation: ΛCDM recovery test with χ² comparison

### 5. Write Results Section

**results.tex:** 1000 words
- [ ] Main constraints table (all parameters, 68% and 95% CL)
- [ ] Model comparison: Δχ², AIC, BIC, Bayes factor
- [ ] Statistical significance assessment
- [ ] Parameter correlations description
- [ ] A_L consistency check
- [ ] Comparison to previous modified gravity constraints

**Target deliverable:** Complete quantitative results with all error bars

---

## WEEK 5-6: Robustness & Discussion

### 6. Robustness Tests

**robustness.tex:** 400 words
- [ ] Prior sensitivity (vary widths by factor of 2)
- [ ] ℓ-range cuts (high-ℓ only, low-ℓ only)
- [ ] Data splits (TT-only, TTTEEE separately)
- [ ] Alternative binnings
- [ ] Systematic error inflation

**Deliverable:** Robustness table showing parameter shifts under variations

### 7. Write Discussion

**discussion.tex:** 600 words
- [ ] Physical interpretation: what does μ₀ ≠ 0 mean?
- [ ] Implications for cosmological tensions
- [ ] Comparison to alternatives (ΛCDM, νΛCDM, EDE)
- [ ] Observational tests to distinguish LGPD
- [ ] Theoretical challenges and microphysics
- [ ] Future prospects (SO, CMB-S4, Euclid forecasts)

---

## WEEK 7-8: Polish & Supplementary

### 8. Complete References

**Current:** 2 references  
**Target:** 80-100 references

**Categories needed:**
- CMB experiments (15): WMAP, Planck, ACT, SPT
- A_L papers (10): Planck 2018 lensing, independent analyses
- Modified gravity (25): MG parameterizations, hi_class, EFTCAMB, constraints
- Quantum decoherence (10): Bassi reviews, gravitational decoherence
- BAO/SNe/Growth (15): BOSS, Pantheon, RSD compilations
- Statistical methods (5): MCMC, Bayesian inference
- Tensions (10): H0, σ8, early vs late

**Action:** Use `scripts/generate_references.py` (TO CREATE) to populate refs.bib

### 9. Supplementary Materials

- [ ] Extended Methods PDF (Boltzmann implementation details)
- [ ] Supplementary Figures (convergence traces, additional posteriors)
- [ ] Supplementary Tables (full parameter chains summary)
- [ ] Code/Data availability statement with Zenodo DOI

### 10. Format for Journal

**For PRD:**
- Use `revtex4-2` class
- Single-column preprint format
- References in PRD style
- Submit to arXiv first

**For JCAP:**
- Use JCAP template (download from journal site)
- Double-column format
- References in JCAP style

---

## WEEK 9-10: Review & Submission

### 11. Internal Review

- [ ] Co-author review (if applicable)
- [ ] Colleague read-through
- [ ] Professional editing for clarity
- [ ] Check all cross-references
- [ ] Verify figure numbering
- [ ] Run spell/grammar check

### 12. Pre-submission Checklist

- [ ] Word/page count within journal limits
- [ ] All figures have captions
- [ ] All tables have captions
- [ ] References complete and formatted
- [ ] Code archived on Zenodo with DOI
- [ ] Data products archived (posteriors, figures)
- [ ] Cover letter written
- [ ] Author contributions statement
- [ ] Competing interests declaration

### 13. Submission

1. **arXiv preprint** (always do this first)
   - Submit to astro-ph.CO
   - Include ancillary files (code link, data)
   - Get arXiv number

2. **Journal submission** (PRD or JCAP)
   - Upload manuscript + figures + supplement
   - Include cover letter highlighting novelty
   - Suggest 3-5 referees
   - Track submission status

---

## REALISTIC TIMELINE ESTIMATE

**With your current results (TT+TE+EE synthetic + phenomenological modulation):**

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Production data + analysis | 2 weeks | 2 weeks |
| Write theory + methods | 2 weeks | 4 weeks |
| Generate figures | 1 week | 5 weeks |
| Write results + discussion | 2 weeks | 7 weeks |
| Robustness + references | 1 week | 8 weeks |
| Polish + review | 2 weeks | 10 weeks |
| **Total to submission** | | **10 weeks** |

**If you need to implement Boltzmann modifications first:**
- Add 3-4 weeks to learn CLASS/hi_class or CAMB/EFTCAMB
- Add 2 weeks for validation and testing
- **Total:** 15-16 weeks

**If upgrading to Nature Physics standards:**
- Add 4-6 weeks for extended analysis and writing
- Requires breakthrough-level result (currently marginal)
- **Not recommended** unless you find >3σ deviation

---

## SUCCESS METRICS

**Minimum viable paper (PRD/JCAP):**
- [ ] 3000-5000 words
- [ ] 4-6 figures
- [ ] 2-3 tables
- [ ] 60-80 references
- [ ] Real Planck data + proper likelihoods
- [ ] Quantitative constraints with error bars
- [ ] Model comparison statistics
- [ ] Consistency checks passed

**Strong paper (competitive for PRD):**
- [ ] All above PLUS
- [ ] Boltzmann-consistent μ/Σ implementation
- [ ] Full covariance matrices
- [ ] Comprehensive robustness tests
- [ ] Clear physical interpretation
- [ ] Testable predictions

**Exceptional paper (Nature Physics consideration):**
- [ ] All above PLUS
- [ ] >3σ resolution of A_L tension
- [ ] Consistent explanation of H0 or σ8 tension
- [ ] Novel prediction verified by independent data
- [ ] Fundamental theoretical justification

---

## IMMEDIATE NEXT STEPS (THIS WEEK)

1. **Run production analysis** with current pipeline + synthetic data
2. **Generate Figure 1** (power spectra) using `scripts/posterior_diagnostics.py` output
3. **Expand theory.tex** to 500 words minimum (use template)
4. **Create parameter constraints table** with current results
5. **Add 30 essential references** to refs.bib

**Daily goal:** Add 200 words and 1 figure per day → 80% complete in 3-4 weeks

---

## HELP AVAILABLE

To generate specific content:
```bash
# Check current progress
python scripts/expand_paper_sections.py --check

# Get theory section template
python scripts/expand_paper_sections.py --template theory > paper/sections/theory_draft.tex

# Generate figures (scripts to create)
python scripts/plot_power_spectra.py
python scripts/plot_corner.py
python scripts/plot_AL_comparison.py
```

**Want me to generate:**
- Specific section drafts?
- Figure generation scripts?
- Reference database?
- Supplementary materials templates?

Ask for any of these and I'll create them immediately.
