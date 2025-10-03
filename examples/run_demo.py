
import numpy as np
import os
from lgpd_cosmo.models import LGPDParams, CondensateParams, ElasticityParams, ThreadbareParams, LGPDTransfer
from lgpd_cosmo.cmb import apply_modifications
from lgpd_cosmo.plotting import plot_cls, plot_gamma
from lgpd_cosmo.data import DataRepository
from lgpd_cosmo.mcmc import run_emcee
from lgpd_cosmo.likelihoods import Likelihoods

def toy_baseline_cls(lmax=2500):
    ell = np.arange(2, lmax+1)
    # crude toy TT with peaks using damped sin on log ell
    Dl_tt = 1000.0 * np.exp(- (ell/2500.0)**2) * (1 + 0.25*np.sin(np.log(ell)*3.5))
    Dl_ee = 50.0 * np.exp(- (ell/1800.0)**2) * (1 + 0.2*np.sin(np.log(ell)*3.2 + 0.5))
    Dl_te = 150.0 * np.exp(- (ell/2200.0)**2) * (1 + 0.2*np.sin(np.log(ell)*3.4 + 0.3)) * np.sign(np.sin(np.log(ell)))
    conv = (2*np.pi)/(ell*(ell+1.0))
    cls = {'TT': Dl_tt*conv, 'EE': Dl_ee*conv, 'TE': Dl_te*conv}
    return ell, cls

def main():
    outdir = 'examples/_demo_outputs'
    os.makedirs(outdir, exist_ok=True)

    # Baseline (synthetic if real not present)
    repo = DataRepository(root='data')
    try:
        ell, base_cls = repo.load_planck_baseline()
    except Exception:
        ell, base_cls = toy_baseline_cls()

    # Parameters (can tweak)
    lgpd = LGPDParams(log10_Gamma0=-18.0, a_star=1.0, p=2.0, T_lgpd=2.725, xi_damp=0.2)
    cond = CondensateParams(mu0=0.1, k0=0.07, m=2.0, zt=1.5, n=3.0)
    elas = ElasticityParams(sigma0=0.1, k0=0.1, m=2.0, zt=1.5, n=3.0)
    thread = ThreadbareParams(lc0=300.0, nu=1.0, zt=1.0, n=2.0)
    transfer = LGPDTransfer(lgpd, cond, elas, thread)

    mod_cls = apply_modifications(ell, base_cls, transfer)
    plot_cls(ell, base_cls, mod_cls, os.path.join(outdir, 'cls_demo.png'))

    # Plot Gamma(a)
    a = np.logspace(-3, 0, 300)
    from lgpd_cosmo.models import gamma_of_a
    Gam = gamma_of_a(a, lgpd)
    plot_gamma(a, Gam, os.path.join(outdir, 'gamma_demo.png'))

    # Tiny MCMC on synthetic binned TT
    Dl_tt_base = ell*(ell+1.0)*base_cls['TT']/(2*np.pi)
    # synth "data"
    Dl_data = Dl_tt_base * (1.0 + 0.0*np.random.normal(size=len(ell)))
    sigma = 0.05*Dl_tt_base + 1.0
    # Use only every 20th point to speed
    sel = (ell % 20)==0
    ells_b = ell[sel]; Dl_dat = Dl_data[sel]; sig = sigma[sel]
    L = Likelihoods()

    def loglike(theta):
        # theta: [mu0, sigma0, xi_damp]
        m0, s0, xd = theta
        lgpd2 = LGPDParams(log10_Gamma0=-18.0, a_star=1.0, p=2.0, T_lgpd=2.725, xi_damp=xd)
        cond2 = CondensateParams(mu0=m0, k0=0.07, m=2.0, zt=1.5, n=3.0)
        elas2 = ElasticityParams(sigma0=s0, k0=0.1, m=2.0, zt=1.5, n=3.0)
        tr2 = LGPDTransfer(lgpd2, cond2, elas2)
        mod2 = apply_modifications(ell, base_cls, tr2)
        Dl_model = ell*(ell+1.0)*mod2['TT']/(2*np.pi)
        like = -0.5 * L.add_planck_simple(ells_b, Dl_dat, sig, ell, Dl_model)
        L.parts = []  # reset
        return like

    from lgpd_cosmo.mcmc import run_emcee
    theta0 = np.array([0.05, 0.05, 0.1])
    priors = [(-0.3, 0.3), (-0.3, 0.3), (0.0, 1.0)]
    chain, lnp = run_emcee(loglike, theta0, priors, nwalkers=16, nsteps=200, nburn=100)
    np.savez(os.path.join(outdir, 'mcmc_chain.npz'), chain=chain, logprob=lnp)
    print("Demo complete. Outputs in", outdir)

if __name__ == "__main__":
    main()
