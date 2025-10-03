#!/usr/bin/env python3
"""
Generate all publication-quality figures for LGPD paper.
Reads posterior samples and baseline data, produces:
1. TT/TE/EE power spectra with LGPD best-fit and uncertainty bands
2. Corner plot of posterior (mu0, Sigma0, xi_damp)
3. Constraint plane (mu0, Sigma0) with contours
4. A_L proxy distribution
5. Residuals plot
"""
import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Ensure repo root is in path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from lgpd_cosmo.data import DataRepository
from lgpd_cosmo.models import LGPDParams, CondensateParams, ElasticityParams, LGPDTransfer
from lgpd_cosmo.cmb import apply_modifications

# Publication-quality matplotlib settings
plt.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
    'figure.figsize': (6, 4),
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'text.usetex': False,  # Set True if LaTeX available
})

def load_posterior():
    """Load posterior samples from MCMC chain."""
    chain_file = repo_root / "outputs" / "posterior_chain.npz"
    if not chain_file.exists():
        raise FileNotFoundError(f"Posterior chain not found at {chain_file}")
    data = np.load(chain_file)
    samples = data['samples']  # shape (nsteps, nparams)
    param_names = data['param_names'].tolist()
    log_prob = data['log_prob']
    return samples, param_names, log_prob

def compute_bestfit_and_percentiles(samples):
    """Get best-fit (median) and 68% credible intervals."""
    median = np.median(samples, axis=0)
    lower = np.percentile(samples, 16, axis=0)
    upper = np.percentile(samples, 84, axis=0)
    return median, lower, upper

def generate_modified_spectra(mu0, Sigma0, xi_damp, baseline_cls):
    """Generate modified Cls given parameters."""
    lgpd_p = LGPDParams(xi_damp=xi_damp)
    cond_p = CondensateParams(mu0=mu0)
    elast_p = ElasticityParams(sigma0=Sigma0)
    transfer = LGPDTransfer(lgpd_p, cond_p, elast_p)
    
    ell, cltt, clte, clee = baseline_cls
    mod_cls = apply_modifications(ell, cltt, clte, clee, transfer, apply_lgpd=True, apply_mu_sigma=True)
    return mod_cls

def plot_power_spectra_with_bands(baseline_cls, samples, param_names, output_dir):
    """
    Figure 1: TT/TE/EE power spectra showing baseline, best-fit, and 68% posterior bands.
    """
    ell, cltt_base, clte_base, clee_base = baseline_cls
    
    # Get parameter columns
    mu0_idx = param_names.index('mu_0')
    Sigma0_idx = param_names.index('Sigma_0')
    xi_idx = param_names.index('xi_damp')
    
    # Best-fit (median)
    median_params = np.median(samples, axis=0)
    mu0_bf, Sigma0_bf, xi_bf = median_params[[mu0_idx, Sigma0_idx, xi_idx]]
    
    # Generate best-fit modified spectra
    mod_cls_bf = generate_modified_spectra(mu0_bf, Sigma0_bf, xi_bf, baseline_cls)
    ell_mod, cltt_mod, clte_mod, clee_mod = mod_cls_bf
    
    # Generate posterior bands (sample random subset for speed)
    n_band_samples = min(200, len(samples))
    rand_idx = np.random.choice(len(samples), n_band_samples, replace=False)
    
    cltt_band = []
    clte_band = []
    clee_band = []
    
    for idx in rand_idx:
        mu0_s, Sigma0_s, xi_s = samples[idx, [mu0_idx, Sigma0_idx, xi_idx]]
        mod_s = generate_modified_spectra(mu0_s, Sigma0_s, xi_s, baseline_cls)
        cltt_band.append(mod_s[1])
        clte_band.append(mod_s[2])
        clee_band.append(mod_s[3])
    
    # Convert to Dl = l(l+1)Cl/(2π)
    def cl_to_dl(ell, cl):
        return ell * (ell + 1) * cl / (2 * np.pi)
    
    # Plot TT/TE/EE
    fig, axes = plt.subplots(3, 1, figsize=(7, 9), sharex=True)
    
    # TT
    ax = axes[0]
    ax.plot(ell, cl_to_dl(ell, cltt_base), 'k-', lw=1.5, label='ΛCDM (baseline)', alpha=0.8)
    ax.plot(ell_mod, cl_to_dl(ell_mod, cltt_mod), 'r-', lw=1.5, label='LGPD best-fit')
    
    # Posterior band
    cltt_band_arr = np.array(cltt_band)
    cltt_lower = np.percentile(cltt_band_arr, 16, axis=0)
    cltt_upper = np.percentile(cltt_band_arr, 84, axis=0)
    ax.fill_between(ell_mod, cl_to_dl(ell_mod, cltt_lower), cl_to_dl(ell_mod, cltt_upper), 
                     color='red', alpha=0.2, label='68% posterior')
    
    ax.set_ylabel(r'$D_\ell^{TT}$ [$\mu$K$^2$]')
    ax.legend(loc='best', frameon=False)
    ax.set_xlim(2, 2500)
    ax.grid(alpha=0.3)
    
    # TE
    ax = axes[1]
    ax.plot(ell, cl_to_dl(ell, np.abs(clte_base)), 'k-', lw=1.5, alpha=0.8)
    ax.plot(ell_mod, cl_to_dl(ell_mod, np.abs(clte_mod)), 'r-', lw=1.5)
    
    clte_band_arr = np.array(clte_band)
    clte_lower = np.percentile(np.abs(clte_band_arr), 16, axis=0)
    clte_upper = np.percentile(np.abs(clte_band_arr), 84, axis=0)
    ax.fill_between(ell_mod, cl_to_dl(ell_mod, clte_lower), cl_to_dl(ell_mod, clte_upper), 
                     color='red', alpha=0.2)
    
    ax.set_ylabel(r'$|D_\ell^{TE}|$ [$\mu$K$^2$]')
    ax.set_yscale('log')
    ax.grid(alpha=0.3)
    
    # EE
    ax = axes[2]
    ax.plot(ell, cl_to_dl(ell, clee_base), 'k-', lw=1.5, alpha=0.8)
    ax.plot(ell_mod, cl_to_dl(ell_mod, clee_mod), 'r-', lw=1.5)
    
    clee_band_arr = np.array(clee_band)
    clee_lower = np.percentile(clee_band_arr, 16, axis=0)
    clee_upper = np.percentile(clee_band_arr, 84, axis=0)
    ax.fill_between(ell_mod, cl_to_dl(ell_mod, clee_lower), cl_to_dl(ell_mod, clee_upper), 
                     color='red', alpha=0.2)
    
    ax.set_ylabel(r'$D_\ell^{EE}$ [$\mu$K$^2$]')
    ax.set_xlabel(r'Multipole $\ell$')
    ax.set_yscale('log')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    fig_path = output_dir / "fig1_power_spectra.png"
    plt.savefig(fig_path)
    print(f"Saved: {fig_path}")
    plt.close()

def plot_corner(samples, param_names, output_dir):
    """
    Figure 2: Corner plot showing posterior distributions and correlations.
    """
    try:
        import corner
    except ImportError:
        print("Warning: 'corner' package not installed. Skipping corner plot.")
        print("Install with: pip install corner")
        return
    
    # Extract main parameters
    mu0_idx = param_names.index('mu_0')
    Sigma0_idx = param_names.index('Sigma_0')
    xi_idx = param_names.index('xi_damp')
    
    plot_samples = samples[:, [mu0_idx, Sigma0_idx, xi_idx]]
    labels = [r'$\mu_0$', r'$\Sigma_0$', r'$\xi_{\rm damp}$']
    
    fig = corner.corner(plot_samples, labels=labels, 
                       quantiles=[0.16, 0.5, 0.84],
                       show_titles=True, title_fmt='.3f',
                       title_kwargs={"fontsize": 11})
    
    fig_path = output_dir / "fig2_corner_plot.png"
    plt.savefig(fig_path, dpi=300)
    print(f"Saved: {fig_path}")
    plt.close()

def plot_constraint_plane(samples, param_names, output_dir):
    """
    Figure 3: 2D constraint plane for (mu0, Sigma0) with 68% and 95% contours.
    """
    mu0_idx = param_names.index('mu_0')
    Sigma0_idx = param_names.index('Sigma_0')
    
    mu0_samples = samples[:, mu0_idx]
    Sigma0_samples = samples[:, Sigma0_idx]
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # 2D histogram
    H, xedges, yedges = np.histogram2d(mu0_samples, Sigma0_samples, bins=40)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    # Contour levels for 68% and 95%
    sorted_H = np.sort(H.flatten())[::-1]
    cumsum = np.cumsum(sorted_H) / np.sum(sorted_H)
    level_68 = sorted_H[np.searchsorted(cumsum, 0.68)]
    level_95 = sorted_H[np.searchsorted(cumsum, 0.95)]
    
    ax.contour(H.T, extent=extent, levels=[level_95, level_68], 
               colors=['blue', 'red'], linewidths=[1.5, 2])
    ax.contourf(H.T, extent=extent, levels=[level_95, level_68, H.max()], 
                colors=['lightblue', 'pink'], alpha=0.3)
    
    # Mark GR point
    ax.plot(0, 0, 'kx', ms=10, mew=2, label='GR (μ₀=Σ₀=0)')
    
    # Mark best-fit
    mu0_bf = np.median(mu0_samples)
    Sigma0_bf = np.median(Sigma0_samples)
    ax.plot(mu0_bf, Sigma0_bf, 'r+', ms=12, mew=2, label='Best-fit (median)')
    
    ax.set_xlabel(r'$\mu_0$')
    ax.set_ylabel(r'$\Sigma_0$')
    ax.legend(loc='best', frameon=False)
    ax.grid(alpha=0.3)
    
    fig_path = output_dir / "fig3_constraint_plane.png"
    plt.savefig(fig_path)
    print(f"Saved: {fig_path}")
    plt.close()

def plot_AL_distribution(samples, param_names, output_dir):
    """
    Figure 4: Distribution of effective A_L proxy from posterior.
    """
    # Compute A_L^eff = 1 + Sigma(k=0.1, z=2) for each sample
    Sigma0_idx = param_names.index('Sigma_0')
    Sigma0_samples = samples[:, Sigma0_idx]
    
    # Simple proxy: A_L^eff ≈ 1 + Sigma0 (at our pivot)
    AL_eff = 1.0 + Sigma0_samples
    
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(AL_eff, bins=50, color='steelblue', alpha=0.7, edgecolor='black')
    
    # Mark median and 68% interval
    median_AL = np.median(AL_eff)
    lower_AL = np.percentile(AL_eff, 16)
    upper_AL = np.percentile(AL_eff, 84)
    
    ax.axvline(median_AL, color='red', lw=2, label=f'Median: {median_AL:.4f}')
    ax.axvline(lower_AL, color='red', lw=1, ls='--')
    ax.axvline(upper_AL, color='red', lw=1, ls='--', label=f'68% CI: [{lower_AL:.4f}, {upper_AL:.4f}]')
    
    # Mark Planck preference and ΛCDM
    ax.axvline(1.0, color='black', lw=2, ls=':', label='ΛCDM (A_L=1)')
    ax.axvline(1.18, color='orange', lw=2, ls='-.', alpha=0.7, label='Planck TT/TE/EE (A_L~1.18)')
    
    ax.set_xlabel(r'$A_L^{\rm eff}$')
    ax.set_ylabel('Counts')
    ax.legend(loc='best', frameon=False, fontsize=8)
    ax.grid(alpha=0.3)
    
    fig_path = output_dir / "fig4_AL_distribution.png"
    plt.savefig(fig_path)
    print(f"Saved: {fig_path}")
    plt.close()

def main():
    print("Generating all paper figures...")
    
    # Setup
    output_dir = repo_root / "outputs" / "figures"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Load data
    print("Loading posterior samples...")
    samples, param_names, log_prob = load_posterior()
    print(f"  Loaded {len(samples)} samples with {len(param_names)} parameters")
    
    print("Loading baseline Cls...")
    repo = DataRepository(repo_root / "data")
    ell, cls_dict = repo.load_planck_baseline()
    baseline_cls = (ell, cls_dict['TT'], cls_dict['TE'], cls_dict['EE'])
    
    # Generate figures
    print("\n[1/4] Generating power spectra figure...")
    plot_power_spectra_with_bands(baseline_cls, samples, param_names, output_dir)
    
    print("[2/4] Generating corner plot...")
    plot_corner(samples, param_names, output_dir)
    
    print("[3/4] Generating constraint plane...")
    plot_constraint_plane(samples, param_names, output_dir)
    
    print("[4/4] Generating A_L distribution...")
    plot_AL_distribution(samples, param_names, output_dir)
    
    print(f"\n✓ All figures saved to {output_dir}/")
    print("Ready for paper inclusion!")

if __name__ == "__main__":
    main()
