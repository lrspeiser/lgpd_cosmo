
import os, numpy as np
from lgpd_cosmo.data import DataRepository
from lgpd_cosmo.models import LGPDParams, CondensateParams, ElasticityParams, LGPDTransfer
from lgpd_cosmo.cmb import apply_modifications, load_baseline_cls
from lgpd_cosmo.likelihoods import Likelihoods
from lgpd_cosmo.mcmc import run_emcee

def main():
    repo = DataRepository(root='data')
    ell, base = repo.load_planck_baseline('planck_baseline_cls.npz')

    # Optional: load binned TT/TE/EE for simple chi2
    tt_file = 'planck_tt_binned.csv'
    te_file = 'planck_te_binned.csv'
    ee_file = 'planck_ee_binned.csv'
    have_tt = os.path.exists(repo.path(tt_file))
    have_te = os.path.exists(repo.path(te_file))
    have_ee = os.path.exists(repo.path(ee_file))
    if have_tt:
        ell_tt, Dl_tt, sig_tt = repo.load_simple_binned(tt_file)
    if have_te:
        ell_te, Dl_te, sig_te = repo.load_simple_binned(te_file)
    if have_ee:
        ell_ee, Dl_ee, sig_ee = repo.load_simple_binned(ee_file)

    # Initial parameters
    lgpd = LGPDParams(log10_Gamma0=-18.5, a_star=1.0, p=2.0, T_lgpd=2.7255, xi_damp=0.1)
    cond = CondensateParams(mu0=0.05, k0=0.07, m=2.0, zt=1.5, n=3.0)
    elas = ElasticityParams(sigma0=0.05, k0=0.1, m=2.0, zt=1.5, n=3.0)
    transfer = LGPDTransfer(lgpd, cond, elas)

    def loglike(theta):
        m0, s0, xd = theta
        lgpd2 = LGPDParams(log10_Gamma0=-18.5, a_star=1.0, p=2.0, T_lgpd=2.7255, xi_damp=xd)
        cond2 = CondensateParams(mu0=m0, k0=0.07, m=2.0, zt=1.5, n=3.0)
        elas2 = ElasticityParams(sigma0=s0, k0=0.1, m=2.0, zt=1.5, n=3.0)
        mod = apply_modifications(ell, base, LGPDTransfer(lgpd2, cond2, elas2))
        L = Likelihoods()
        total_chi2 = 0.0
        if have_tt:
            Dl_model_tt = ell*(ell+1.0)*mod['TT']/(2*np.pi)
            total_chi2 += L.add_planck_simple(ell_tt, Dl_tt, sig_tt, ell, Dl_model_tt)
        if have_te:
            Dl_model_te = ell*(ell+1.0)*mod['TE']/(2*np.pi)
            total_chi2 += L.add_planck_simple(ell_te, Dl_te, sig_te, ell, Dl_model_te)
        if have_ee:
            Dl_model_ee = ell*(ell+1.0)*mod['EE']/(2*np.pi)
            total_chi2 += L.add_planck_simple(ell_ee, Dl_ee, sig_ee, ell, Dl_model_ee)
        if not (have_tt or have_te or have_ee):
            # Fallback: compare TT to baseline as pseudo-data
            Dl_model = ell*(ell+1.0)*mod['TT']/(2*np.pi)
            Dl_data  = ell*(ell+1.0)*base['TT']/(2*np.pi)
            sig = 0.05*Dl_data + 1.0
            total_chi2 = L.add_planck_simple(ell[::10], Dl_data[::10], sig[::10], ell, Dl_model)
        return -0.5*total_chi2

    # Priors: (mu0, sigma0, xi_damp)
    priors = [(-0.3, 0.3), (-0.3, 0.3), (0.0, 1.0)]
    theta0 = np.array([0.05, 0.05, 0.1])
    chain, lnp = run_emcee(loglike, theta0, priors, nwalkers=32, nsteps=400, nburn=200)
    os.makedirs('examples/_real_fit', exist_ok=True)
    np.savez('examples/_real_fit/posterior.npz', chain=chain, logprob=lnp)
    print('Done. Saved posterior to examples/_real_fit/posterior.npz')

if __name__ == "__main__":
    main()
