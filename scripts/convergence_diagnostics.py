#!/usr/bin/env python3
"""
MCMC Convergence Diagnostics

Generates comprehensive convergence diagnostics for LGPD MCMC chains:
- Trace plots for all parameters
- R-hat (Gelman-Rubin) statistics  
- Autocorrelation analysis
- Effective sample sizes
- Summary statistics table

REPRODUCIBILITY:
- Reads posterior_chain.npz from outputs/
- All diagnostics saved to outputs/convergence/
- Uses standard emcee diagnostics where applicable

Usage:
    python scripts/convergence_diagnostics.py
    
Output:
    outputs/convergence/
        trace_plots.png           - Parameter traces over MCMC steps
        autocorr_plots.png        - Autocorrelation functions
        diagnostics_table.txt     - Summary statistics
        diagnostics_table.tex     - LaTeX version
        
Author: Leonard Speiser
Date: 2025-10-03
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'figure.dpi': 150,
    'savefig.dpi': 300,
})


def compute_rhat(chains_list):
    """
    Compute Gelman-Rubin R-hat statistic.
    
    Parameters
    ----------
    chains_list : list of arrays
        Each array is (N_samples, N_params)
    
    Returns
    -------
    rhat : array
        R-hat for each parameter
    """
    if len(chains_list) < 2:
        return None
    
    M = len(chains_list)
    N = min(c.shape[0] for c in chains_list)
    ndim = chains_list[0].shape[1]
    
    # Trim to same length
    chains = np.array([c[:N, :] for c in chains_list])  # (M, N, ndim)
    
    # Within-chain variance
    W = np.mean(np.var(chains, axis=1, ddof=1), axis=0)
    
    # Between-chain variance
    chain_means = np.mean(chains, axis=1)  # (M, ndim)
    B = N * np.var(chain_means, axis=0, ddof=1)
    
    # Pooled variance
    var_plus = ((N - 1) * W + B) / N
    
    # R-hat
    rhat = np.sqrt(var_plus / (W + 1e-12))
    return rhat


def compute_autocorr(chain, maxlag=200):
    """
    Compute autocorrelation function.
    
    Parameters
    ----------
    chain : array (N,)
        1D chain
    maxlag : int
        Maximum lag
    
    Returns
    -------
    lags : array
        Lag values
    acf : array
        Autocorrelation values
    """
    chain = chain - np.mean(chain)
    c0 = np.dot(chain, chain) / len(chain)
    
    acf = []
    lags = np.arange(0, min(maxlag, len(chain)//2))
    
    for lag in lags:
        if lag == 0:
            acf.append(1.0)
        else:
            c = np.dot(chain[:-lag], chain[lag:]) / (len(chain) - lag)
            acf.append(c / c0)
    
    return lags, np.array(acf)


def integrated_autocorr_time(acf, c=5):
    """
    Estimate integrated autocorrelation time.
    
    Uses the automated windowing procedure from Sokal (1989).
    
    Parameters
    ----------
    acf : array
        Autocorrelation function
    c : float
        Window parameter (typically 5)
    
    Returns
    -------
    tau : float
        Integrated autocorrelation time
    """
    tau = 2 * np.cumsum(acf) - 1
    for M in range(len(acf)):
        if M >= c * tau[M]:
            return tau[M]
    return tau[-1]


def plot_traces(chain, param_names, output_file):
    """Generate trace plots for all parameters."""
    fig, axes = plt.subplots(len(param_names), 1, figsize=(10, 2*len(param_names)))
    if len(param_names) == 1:
        axes = [axes]
    
    for i, (ax, name) in enumerate(zip(axes, param_names)):
        ax.plot(chain[:, i], 'k-', alpha=0.5, lw=0.5)
        ax.set_ylabel(name)
        ax.grid(alpha=0.3)
        
        # Add running mean
        window = 100
        if len(chain) > window:
            running_mean = np.convolve(chain[:, i], np.ones(window)/window, mode='valid')
            ax.plot(np.arange(window//2, len(chain)-window//2+1), running_mean, 'r-', lw=1.5, alpha=0.7)
    
    axes[-1].set_xlabel('Step')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Trace plots saved to {output_file}")


def plot_autocorr(chain, param_names, output_file):
    """Generate autocorrelation plots."""
    fig, axes = plt.subplots(len(param_names), 1, figsize=(8, 2*len(param_names)))
    if len(param_names) == 1:
        axes = [axes]
    
    for i, (ax, name) in enumerate(zip(axes, param_names)):
        lags, acf = compute_autocorr(chain[:, i])
        ax.plot(lags, acf, 'k-', lw=1.5)
        ax.axhline(0, color='gray', ls='--', lw=1)
        ax.axhline(1/np.e, color='red', ls='--', lw=1, alpha=0.5, label='1/e')
        ax.set_ylabel(f'ACF({name})')
        ax.set_xlim(0, len(lags))
        ax.set_ylim(-0.2, 1.0)
        ax.grid(alpha=0.3)
        if i == 0:
            ax.legend(loc='upper right')
    
    axes[-1].set_xlabel('Lag')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Autocorrelation plots saved to {output_file}")


def generate_diagnostics_table(chain, param_names, output_dir):
    """Generate convergence diagnostics summary table."""
    # Compute statistics
    medians = np.median(chain, axis=0)
    stds = np.std(chain, axis=0)
    
    # Autocorrelation times
    tau = []
    for i in range(chain.shape[1]):
        lags, acf = compute_autocorr(chain[:, i])
        tau_i = integrated_autocorr_time(acf)
        tau.append(tau_i)
    tau = np.array(tau)
    
    # Effective sample sizes
    n_total = len(chain)
    n_eff = n_total / (2 * tau)
    
    # R-hat (split chain into 4 segments)
    n_per_segment = n_total // 4
    if n_per_segment > 100:
        segments = [chain[i*n_per_segment:(i+1)*n_per_segment] 
                   for i in range(4)]
        rhat = compute_rhat(segments)
    else:
        rhat = None
    
    # Text table
    txt_file = output_dir / "diagnostics_table.txt"
    with open(txt_file, 'w') as f:
        f.write("MCMC CONVERGENCE DIAGNOSTICS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total samples: {n_total}\n")
        f.write(f"Burn-in: assumed in posterior_chain.npz (already removed)\n\n")
        
        f.write(f"{'Parameter':<15} {'Median':<10} {'Std':<10} {'τ_int':<10} {'N_eff':<10} {'R̂':<10}\n")
        f.write("-"*70 + "\n")
        
        for i, name in enumerate(param_names):
            rhat_str = f"{rhat[i]:.4f}" if rhat is not None else "N/A"
            f.write(f"{name:<15} {medians[i]:<10.4f} {stds[i]:<10.4f} "
                   f"{tau[i]:<10.1f} {n_eff[i]:<10.0f} {rhat_str:<10}\n")
        
        f.write("\n" + "="*70 + "\n")
        f.write("\nDiagnostic criteria:\n")
        f.write("  ✓ R̂ < 1.01: Excellent convergence\n")
        f.write("  ✓ N_eff > 400: Sufficient for reliable posteriors\n")
        f.write("  ✓ τ_int < 50: Good mixing\n\n")
        
        # Assess convergence
        if rhat is not None:
            max_rhat = np.max(rhat)
            f.write(f"Max R̂ = {max_rhat:.4f}")
            if max_rhat < 1.01:
                f.write(" → EXCELLENT convergence\n")
            elif max_rhat < 1.05:
                f.write(" → GOOD convergence\n")
            else:
                f.write(" → WARNING: May need more samples\n")
        
        min_neff = np.min(n_eff)
        f.write(f"Min N_eff = {min_neff:.0f}")
        if min_neff > 1000:
            f.write(" → EXCELLENT\n")
        elif min_neff > 400:
            f.write(" → GOOD\n")
        else:
            f.write(" → WARNING: Consider longer run\n")
    
    print(f"  ✓ Text diagnostics saved to {txt_file}")
    
    # LaTeX table
    tex_file = output_dir / "diagnostics_table.tex"
    with open(tex_file, 'w') as f:
        f.write("\\begin{table}[t]\n")
        f.write("\\centering\n")
        f.write("\\caption{MCMC convergence diagnostics. $\\tau_{\\rm int}$ is the integrated autocorrelation time; "
               "$N_{\\rm eff} = N_{\\rm total}/(2\\tau_{\\rm int})$ is the effective sample size; "
               "$\\hat{R}$ is the Gelman-Rubin statistic.}\n")
        f.write("\\label{tab:convergence}\n")
        f.write("\\begin{tabular}{lcccccc}\n")
        f.write("\\hline\n")
        f.write("Parameter & Median & Std & $\\tau_{\\rm int}$ & $N_{\\rm eff}$ & $\\hat{R}$ \\\\\n")
        f.write("\\hline\n")
        
        for i, name in enumerate(param_names):
            rhat_str = f"{rhat[i]:.3f}" if rhat is not None else "--"
            # LaTeX-safe parameter names
            name_tex = name.replace('_', '\\_')
            f.write(f"${name_tex}$ & {medians[i]:.4f} & {stds[i]:.4f} & "
                   f"{tau[i]:.1f} & {n_eff[i]:.0f} & {rhat_str} \\\\\n")
        
        f.write("\\hline\n")
        f.write("\\end{tabular}\n")
        f.write("\\end{table}\n")
    
    print(f"  ✓ LaTeX table saved to {tex_file}")


def main():
    print("\n" + "="*60)
    print("MCMC CONVERGENCE DIAGNOSTICS")
    print("="*60)
    
    # Load chain
    print("\nLoading posterior chain...")
    chain_file = repo_root / "outputs" / "posterior_chain.npz"
    data = np.load(chain_file)
    chain = data['samples']
    param_names = list(data['param_names'])
    
    print(f"  Chain shape: {chain.shape}")
    print(f"  Parameters: {param_names}")
    
    # Setup output
    output_dir = repo_root / "outputs" / "convergence"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate diagnostics
    print("\nGenerating diagnostics...")
    plot_traces(chain, param_names, output_dir / "trace_plots.png")
    plot_autocorr(chain, param_names, output_dir / "autocorr_plots.png")
    generate_diagnostics_table(chain, param_names, output_dir)
    
    print("\n" + "="*60)
    print("✓ CONVERGENCE DIAGNOSTICS COMPLETE")
    print("="*60)
    print(f"\nResults saved to: {output_dir}/")
    print("\nNext steps:")
    print("  - Review outputs/convergence/diagnostics_table.txt")
    print("  - Include trace/autocorr plots in supplement")
    print("  - Cite R̂ and N_eff in methods section")


if __name__ == "__main__":
    main()
