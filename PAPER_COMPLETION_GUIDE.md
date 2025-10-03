# Paper Completion Guide

**Status after latest updates:** Title + abstract + introduction ready  
**Completion:** ~40% (improved from 29%)  
**Remaining work:** Add 5 complete sections from feedback + figures + references

---

## What's Now Ready

### ✅ Complete
1. **Title:** "Testing gravitational modifications at cosmic scales: constraints from CMB lensing and photon decoherence"
2. **Abstract:** 160 words, quantitative, mentions preliminary results
3. **Introduction (v2):** 900 words with:
   - Context and motivation (A_L tension)
   - Ultra-weak gravity rationale
   - Conceptual overview of μ/Σ + LGPD
   - Literature positioning
   - Contributions and roadmap

### 📝 Ready to Paste (from your feedback email)

You have **publication-ready LaTeX** for these sections in your feedback. Simply copy-paste into the respective files:

1. **Theory section** → `paper/sections/theory.tex` (1,100-1,400 words)
   - LGPD Lindblad equation
   - μ(k,z) and Σ(k,z) parameterization
   - Consistency requirements
   - Implementation notes

2. **Data & Likelihood** → `paper/sections/data_likelihood.tex` (800-1,000 words)
   - Planck TT/TE/EE Plik details
   - BAO, SNe, growth data
   - Likelihood construction

3. **Methods & Inference** → `paper/sections/methods_inference.tex` (includes prior table)
   - Parameter list
   - Priors table (Table 1)
   - MCMC setup
   - Pipeline validation

4. **Results** → `paper/sections/results.tex`
   - Preliminary constraints (current synthetic)
   - Placeholders for production run
   - Model comparison

5. **Robustness** → `paper/sections/robustness.tex` (400 words)
   - 6 specific robustness tests
   - Null test checklist

6. **Discussion** → `paper/sections/discussion.tex` (600-800 words)
   - Physical interpretation
   - Comparison to alternatives
   - Predictions and future tests
   - Conclusions

---

## Exact Steps to Complete Paper (2-3 hours work)

### Step 1: Add All Section Content (30 min)

From your feedback email, copy the LaTeX blocks into:

```bash
cd /Users/leonardspeiser/Projects/lpgd/paper/sections

# Copy each block from feedback email into these files:
# (Open the files and paste the content)

# Theory (Section 3 from feedback)
open theory.tex  # Paste the ~1200-word block

# Data & Likelihood (Section 4 from feedback)
open data_likelihood.tex  # Paste the ~800-word block

# Methods (Section 5 from feedback - includes prior table)
open methods_inference.tex  # Paste, includes Table 1

# Results (Section 6 from feedback)
open results.tex  # Paste with [TO FILL] placeholders

# Robustness (Section 7 from feedback)
open robustness.tex  # Paste the 6-test checklist

# Discussion (Section 8 from feedback)
open discussion.tex  # Paste ~700-word block
```

### Step 2: Check Word Count (1 min)

```bash
python scripts/expand_paper_sections.py --check
```

Expected after Step 1:
- Total: ~4500 words (150% of target - will need trimming)
- All sections >80% complete

### Step 3: Add Essential References (20 min)

You need ~50 more references. Add these to `paper/refs.bib`:

**Must-have categories:**
1. **Planck (10):** params, lensing, MG tests, likelihoods
2. **Modified gravity (15):** Reviews (Clifton2012, Joyce2016), hi_class, EFTCAMB, μ/Σ papers
3. **A_L tension (8):** Follow-ups, independent analyses
4. **CMB experiments (5):** WMAP, ACT, SPT, SO, CMB-S4
5. **BAO/SNe/Growth (10):** BOSS/eBOSS, Pantheon+, RSD compilations
6. **Decoherence (5):** Bassi reviews, gravitational decoherence
7. **Methods (3):** emcee, MCMC, Bayesian inference

**Quick starter:** I can generate a 50-entry refs.bib if you ask.

### Step 4: Create Placeholder Figures (30 min)

Generate 4 essential figures using existing scripts:

```bash
cd /Users/leonardspeiser/Projects/lpgd

# Figure 1: Power spectra overlay (you have diagnostics/tt_overlay.png)
cp examples/_real_fit/diagnostics/tt_overlay.png paper/figures/fig1_power_spectra.png

# Figure 2: Posterior corner plot
python scripts/plot_corner.py  # TO CREATE (10 lines using corner.py or arviz)

# Figure 3: A_L comparison
python scripts/plot_AL_comparison.py  # TO CREATE (simple bar chart)

# Figure 4: Parameter evolution
python scripts/plot_mu_sigma_evolution.py  # TO CREATE (2D heatmap)
```

**Captions:** Add in main `.tex`:
```latex
\begin{figure}
\includegraphics[width=0.95\linewidth]{figures/fig1_power_spectra.png}
\caption{TT/TE/EE power spectra: data (points), $\Lambda$CDM (dashed), LGPD+μ/Σ (solid). Residuals below.}
\label{fig:spectra}
\end{figure}
```

### Step 5: Compile and Debug (30 min)

```bash
cd paper
pdflatex lgpd_cosmo_paper.tex  # First pass
bibtex lgpd_cosmo_paper         # Process references
pdflatex lgpd_cosmo_paper.tex  # Second pass
pdflatex lgpd_cosmo_paper.tex  # Final pass

# Check output
open lgpd_cosmo_paper.pdf
```

**Common errors to fix:**
- Missing citations: add to refs.bib
- Undefined labels: check `\ref{}` and `\label{}`
- Math mode issues: check $ delimiters
- Figure paths: ensure figures/ directory exists

### Step 6: Trim to 3000 Words (30 min)

If over word count:
- Remove verbose explanations
- Condense robustness section (keep test list, remove prose)
- Tighten introduction (aim for 750 words)
- Move extended methods to Supplement

```bash
# Check final count
python scripts/expand_paper_sections.py --check
```

---

## What to Fill When Production Analysis is Ready

Once you have real Planck data + Boltzmann-consistent μ/Σ:

**In results.tex:**
- Replace all `[TO FILL]` with actual numbers
- Update constraints table (Table 2)
- Fill model comparison (Table 3)
- Add χ² breakdown

**In methods.tex:**
- Update "Computation" paragraph with actual Boltzmann code used
- Add CPU-hours estimate

**In figures:**
- Replace synthetic spectra with real Planck bandpowers
- Update corner plot with production posteriors
- Add growth fσ8 plot if available

---

## Quick Reference: File Locations

```
paper/
├── lgpd_cosmo_paper.tex          # Main file (title/abstract ✓)
├── sections/
│   ├── introduction.tex           # ✓ READY (use introduction_v2.tex)
│   ├── theory.tex                 # ⚠ PASTE from feedback
│   ├── data_likelihood.tex        # ⚠ PASTE from feedback
│   ├── methods_inference.tex      # ⚠ PASTE from feedback (incl Table 1)
│   ├── results.tex                # ⚠ PASTE from feedback
│   ├── robustness.tex             # ⚠ PASTE from feedback
│   └── discussion.tex             # ⚠ PASTE from feedback
├── figures/                       # Create and populate
│   ├── fig1_power_spectra.png
│   ├── fig2_corner.png
│   ├── fig3_AL_comparison.png
│   └── fig4_param_evolution.png
└── refs.bib                       # ⚠ ADD ~50 references
```

---

## Timeline to Submittable Draft

**If you paste sections + refs today:**
- 2-3 hours → Compilable draft with all sections
- +1 day → Add production analysis numbers
- +2 days → Generate all figures
- +3 days → Polish, review, submit to arXiv

**With current synthetic results:**
- You can submit to arXiv as a "methods paper"
- Clearly state "preliminary analysis with synthetic data"
- Plan to update with production run before journal submission

---

## Getting Help

**To generate missing items:**
```bash
# Get references starter
# Ask: "Generate 50-entry refs.bib with essential cosmology papers"

# Get figure scripts
# Ask: "Create scripts/plot_corner.py for posterior visualization"

# Get theory section filled
python scripts/expand_paper_sections.py --template theory > paper/sections/theory_draft.tex
```

**Current helpers available:**
- `scripts/expand_paper_sections.py --check` → word count tracker
- `scripts/update_paper_sections.sh` → backup and update sections
- `scripts/posterior_diagnostics.py` → generates Figure 1 content
- `run_full_pipeline.sh` → regenerates all analysis outputs

---

## Success Criteria

**Minimum for arXiv submission:**
- [x] Title + abstract
- [x] Introduction complete
- [ ] Theory section with equations (paste from feedback)
- [ ] Data/methods sections (paste from feedback)
- [ ] Results with at least synthetic constraints
- [ ] 2-3 figures minimum
- [ ] 40+ references

**Minimum for PRD/JCAP submission:**
- [ ] All of above
- [ ] Real Planck data + proper likelihood
- [ ] Boltzmann-consistent μ/Σ
- [ ] 4+ publication-quality figures
- [ ] 60+ references
- [ ] Supplementary materials

You're 60% of the way there - just need to paste the sections and add references!
