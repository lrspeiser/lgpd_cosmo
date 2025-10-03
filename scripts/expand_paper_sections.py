#!/usr/bin/env python3
"""
Helper script to track paper completion and generate section expansions.

Usage:
  python scripts/expand_paper_sections.py --check       # Check current word counts
  python scripts/expand_paper_sections.py --template SECTION  # Generate template for section
"""
import argparse
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PAPER_DIR = REPO_ROOT / "paper" / "sections"

TARGET_WORDS = {
    "introduction": 800,
    "theory": 1200,
    "data_likelihood": 600,
    "methods_inference": 800,
    "results": 1000,
    "robustness": 400,
    "discussion": 600,
}

TOTAL_TARGET = 3000  # Nature Physics limit


def count_words_in_tex(filepath):
    """Count words in a .tex file, excluding LaTeX commands."""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r') as f:
        text = f.read()
    # Remove comments
    text = re.sub(r'%.*', '', text)
    # Remove LaTeX commands (rough approximation)
    text = re.sub(r'\\[a-zA-Z]+(\[.*?\])?(\{.*?\})?', ' ', text)
    # Remove math mode
    text = re.sub(r'\$.*?\$', ' ', text)
    text = re.sub(r'\\\\begin\{equation.*?\}.*?\\\\end\{equation.*?\}', ' ', text, flags=re.DOTALL)
    # Count words
    words = text.split()
    return len(words)


def check_progress():
    """Check current word counts for all sections."""
    print("="*70)
    print("PAPER COMPLETION STATUS")
    print("="*70)
    
    total_words = 0
    for section, target in TARGET_WORDS.items():
        # Try both original and _full versions
        filepath = PAPER_DIR / f"{section}.tex"
        filepath_full = PAPER_DIR / f"{section}_full.tex"
        
        if filepath_full.exists():
            count = count_words_in_tex(filepath_full)
            version = " (full)"
        elif filepath.exists():
            count = count_words_in_tex(filepath)
            version = ""
        else:
            count = 0
            version = " (missing)"
        
        total_words += count
        pct = (count / target) * 100 if target > 0 else 0
        status = "✓" if count >= target else "✗"
        
        print(f"{status} {section:20s}{version:10s}: {count:4d} / {target:4d} words ({pct:5.1f}%)")
    
    print("-"*70)
    overall_pct = (total_words / TOTAL_TARGET) * 100
    print(f"  TOTAL{' '*31}: {total_words:4d} / {TOTAL_TARGET:4d} words ({overall_pct:5.1f}%)")
    print("="*70)
    
    if total_words < TOTAL_TARGET * 0.8:
        print(f"⚠  Need {TOTAL_TARGET * 0.8 - total_words:.0f} more words to reach 80% completion")
    elif total_words > TOTAL_TARGET:
        print(f"⚠  Over word limit by {total_words - TOTAL_TARGET:.0f} words - need to trim")
    else:
        print("✓ Within target range")


def generate_theory_template():
    """Generate detailed theory section template."""
    template = r"""
\subsection{Phenomenological Framework}

We adopt a two-component phenomenological approach to modified gravity at cosmological scales, combining photon decoherence with scale-dependent gravitational response functions.

\paragraph{Low-Gravity Photonic Decoherence (LGPD).}
The LGPD hypothesis posits that photons propagating through regions of extremely weak gravitational potential experience environmental decoherence. We model this via a Lindblad master equation for the photon density matrix $\hat{\rho}$:
\begin{equation}
\frac{d\hat{\rho}}{dt} = -\frac{i}{\hbar}[\hat{H}, \hat{\rho}] + \sum_k \Gamma_k(a) \left( \hat{L}_k \hat{\rho} \hat{L}_k^\dagger - \frac{1}{2}\{\hat{L}_k^\dagger \hat{L}_k, \hat{\rho}\} \right),
\label{eq:lindblad}
\end{equation}
where $\hat{H}$ is the free photon Hamiltonian, $\hat{L}_k$ are Lindblad operators coupling photons to a gravitational environment, and $\Gamma_k(a)$ are scale-factor-dependent decoherence rates.

For CMB photons ($T \sim 2.7\,$K today), we parameterize the decoherence rate as:
\begin{equation}
\Gamma(a) = \Gamma_0 \left( \frac{a_\star^2}{a^2 + a_\star^2} \right)^p,
\label{eq:gamma}
\end{equation}
where $\Gamma_0 = 10^{\log_{10}\Gamma_0}\,$s$^{-1}$ sets the normalization, $a_\star$ marks the transition scale (we fix $a_\star = 1.0$ for simplicity), and $p$ controls the steepness of the low-$a$ (high-$z$) turnoff. This functional form ensures $\Gamma \to \Gamma_0$ today and $\Gamma \to 0$ at early times, preserving BBN.

\paragraph{Physical interpretation.}
[FILL IN: Why weak gravity? Connection to quantum gravity phenomenology. Cite Bassi2013, Adler2007, etc.]

\paragraph{Observable effects on CMB.}
LGPD introduces an additional damping term in the Boltzmann hierarchy for photon temperature and polarization perturbations. In the line-of-sight integral for the CMB power spectrum, this manifests as an exponential suppression:
\begin{equation}
C_\ell^{TT,\rm obs} = C_\ell^{TT,\rm LCDM} \times \exp\left[ -\xi_{\rm damp} \frac{\ell(\ell+1)}{\ell_d^2} \right],
\label{eq:lgpd_damping}
\end{equation}
where $\xi_{\rm damp}$ is a dimensionless damping amplitude (our primary LGPD observable) and $\ell_d \sim 1500$ is a characteristic damping scale. Similar expressions apply for TE and EE spectra.

\subsection{Modified Gravitational Response Functions}

In addition to LGPD, we allow for departures from GR in the relations between metric perturbations and matter density. Following the effective field theory (EFT) approach \citep{Bellini2014_effective,Pogosian2010_parameterizing}, we parameterize modifications via two functions:

\paragraph{Modified Poisson equation.}
The Newtonian potential $\Phi$ (in synchronous gauge) relates to the matter overdensity $\delta$ via:
\begin{equation}
k^2 \Phi = -4\pi G a^2 \bar{\rho}_m [1 + \mu(k,z)] \delta,
\label{eq:poisson_modified}
\end{equation}
where $\mu(k,z)$ quantifies the deviation from GR. For $\mu > 0$, gravitational clustering is enhanced; for $\mu < 0$, it is suppressed.

\paragraph{Gravitational slip.}
The anisotropic stress relation between the two Bardeen potentials $\Phi$ and $\Psi$ is:
\begin{equation}
\frac{\Phi}{\Psi} = [1 + \Sigma(k,z)].
\label{eq:slip}
\end{equation}
In GR with no anisotropic stress, $\Phi = \Psi$ and $\Sigma = 0$. Non-zero $\Sigma$ directly affects CMB lensing because lensing is sensitive to the Weyl potential $(\Phi + \Psi)/2$.

\paragraph{Parameterization.}
We adopt a scale- and redshift-dependent form:
\begin{align}
\mu(k,z) &= \mu_0 \times S_k(k) \times S_z(z), \label{eq:mu_param} \\
\Sigma(k,z) &= \Sigma_0 \times S_k(k) \times S_z(z), \label{eq:sigma_param}
\end{align}
where $\mu_0$ and $\Sigma_0$ are amplitudes today ($z=0$), and:
\begin{align}
S_k(k) &= \frac{1}{1 + (k_\star/k)^m}, \label{eq:Sk} \\
S_z(z) &= \frac{1}{1 + [(1+z)/(1+z_\star)]^n}. \label{eq:Sz}
\end{align}
Here $k_\star$ and $z_\star$ set transition scales, and $m, n$ control smoothness. We fix $k_\star = 0.1\,h\,{\rm Mpc}^{-1}$, $z_\star = 1.5$, $m = 2$, $n = 3$ based on typical scales where modified gravity signatures are expected \citep{Zumalacarregui2017_hiclass}.

\subsection{Consistency Requirements}

\paragraph{Solar system tests.}
Our parameterization must respect tight constraints from solar system tests of GR. For $k \gg k_\star$ (sub-Mpc scales), $S_k \to 1$, so modifications are present. However, on solar system scales ($\sim 10^{-8}\,{\rm Mpc}$), $k/k_\star \sim 10^7$, so $S_k$ must saturate. We ensure this by choosing $m=2$, giving $S_k \sim 1$ only for $k \lesssim k_\star$. Combined with the redshift suppression ($z=0$ today), modifications are negligible in the solar system.

\paragraph{Big Bang nucleosynthesis (BBN).}
At $z \sim 10^9$, $S_z \to 0$ by design, so LGPD and modified gravity effects vanish, preserving the success of BBN predictions for light element abundances \citep{Cyburt2016_BBN}.

\paragraph{Spectral distortions.}
The thermalization rate $\Gamma(a)$ injects energy into the CMB, potentially creating $\mu$- or $y$-type spectral distortions. FIRAS limits constrain $|\mu| < 9 \times 10^{-5}$ and $|y| < 1.5 \times 10^{-5}$ (95\% CL) \citep{Fixsen1996_FIRAS}. For our fiducial $\log_{10}\Gamma_0 = -18.5$, the predicted distortions are well below these limits [CALCULATE AND CITE CALCULATION IN SUPPLEMENT].

\subsection{Implementation in Boltzmann Code}

[FILL IN: How you modified CLASS or CAMB. Brief description of line-of-sight integration. Validation tests.]

"""
    return template


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Check current word counts')
    parser.add_argument('--template', choices=['theory', 'results', 'discussion'], help='Generate template for section')
    args = parser.parse_args()
    
    if args.check:
        check_progress()
    elif args.template:
        if args.template == 'theory':
            print(generate_theory_template())
        else:
            print(f"Template for {args.template} not yet implemented")
    else:
        check_progress()


if __name__ == '__main__':
    main()
