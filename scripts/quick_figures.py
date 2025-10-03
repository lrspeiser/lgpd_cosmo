#!/usr/bin/env python3
"""Quick figure generation for paper."""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

repo_root = Path(__file__).parent.parent

# Load posterior
data = np.load(repo_root / "outputs" / "posterior_chain.npz")
samples = data['samples']
param_names = data['param_names'].tolist()

print(f"Loaded {len(samples)} samples")

# Make output dir
output_dir = repo_root / "outputs" / "figures"
output_dir.mkdir(exist_ok=True, parents=True)

# Figure 1: Corner plot
try:
    import corner
    
    mu0_idx = param_names.index('mu_0')
    Sigma0_idx = param_names.index('Sigma_0')
    xi_idx = param_names.index('xi_damp')
    
    plot_samples = samples[:, [mu0_idx, Sigma0_idx, xi_idx]]
    labels = [r'$\mu_0$', r'$\Sigma_0$', r'$\xi_{\rm damp}$']
    
    fig = corner.corner(plot_samples, labels=labels, 
                       quantiles=[0.16, 0.5, 0.84],
                       show_titles=True, title_fmt='.3f')
    
    fig.savefig(output_dir / "fig2_corner_plot.png", dpi=300)
    print("✓ Saved corner plot")
    plt.close()
except Exception as e:
    print(f"Corner plot failed: {e}")

# Figure 2: Constraint plane
mu0_samples = samples[:, param_names.index('mu_0')]
Sigma0_samples = samples[:, param_names.index('Sigma_0')]

fig, ax = plt.subplots(figsize=(6, 5))
H, xedges, yedges = np.histogram2d(mu0_samples, Sigma0_samples, bins=40)
extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

sorted_H = np.sort(H.flatten())[::-1]
cumsum = np.cumsum(sorted_H) / np.sum(sorted_H)
level_68 = sorted_H[np.searchsorted(cumsum, 0.68)]
level_95 = sorted_H[np.searchsorted(cumsum, 0.95)]

ax.contour(H.T, extent=extent, levels=[level_95, level_68], 
           colors=['blue', 'red'], linewidths=[1.5, 2])
ax.contourf(H.T, extent=extent, levels=[level_95, level_68, H.max()], 
            colors=['lightblue', 'pink'], alpha=0.3)

ax.plot(0, 0, 'kx', ms=10, mew=2, label='GR')
ax.plot(np.median(mu0_samples), np.median(Sigma0_samples), 'r+', ms=12, mew=2, label='Best-fit')

ax.set_xlabel(r'$\mu_0$')
ax.set_ylabel(r'$\Sigma_0$')
ax.legend()
ax.grid(alpha=0.3)

plt.savefig(output_dir / "fig3_constraint_plane.png", dpi=300, bbox_inches='tight')
print("✓ Saved constraint plane")
plt.close()

# Figure 3: A_L distribution
AL_eff = 1.0 + Sigma0_samples

fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(AL_eff, bins=50, color='steelblue', alpha=0.7, edgecolor='black')

median_AL = np.median(AL_eff)
lower_AL = np.percentile(AL_eff, 16)
upper_AL = np.percentile(AL_eff, 84)

ax.axvline(median_AL, color='red', lw=2, label=f'Median: {median_AL:.4f}')
ax.axvline(lower_AL, color='red', lw=1, ls='--')
ax.axvline(upper_AL, color='red', lw=1, ls='--', label=f'68% CI: [{lower_AL:.4f}, {upper_AL:.4f}]')

ax.axvline(1.0, color='black', lw=2, ls=':', label='ΛCDM (A_L=1)')
ax.axvline(1.18, color='orange', lw=2, ls='-.', alpha=0.7, label='Planck (A_L~1.18)')

ax.set_xlabel(r'$A_L^{\rm eff}$')
ax.set_ylabel('Counts')
ax.legend(fontsize=8)
ax.grid(alpha=0.3)

plt.savefig(output_dir / "fig4_AL_distribution.png", dpi=300, bbox_inches='tight')
print("✓ Saved A_L distribution")
plt.close()

print(f"\n✓ All figures saved to {output_dir}/")
