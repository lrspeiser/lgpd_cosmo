#!/usr/bin/env python3
"""
Run a quick multi-probe fit using any available datasets in data/.

Includes:
- CMB binned TT/TE/EE (if present)
- BAO DV/rd (if present)
- SNe mu(z) (if present)
- Growth fσ8(z) (if present)

This is a phenomenological pipeline: background is LCDM, spectra are modified
via lgpd_cosmo transfer functions. It is NOT Boltzmann-consistent; results are
for exploration and robustness only.

Logs are verbose by design to avoid silent fallbacks.
"""
import numpy as np
from pathlib import Path
import sys

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from lgpd_cosmo.data import DataRepository
from lgpd_cosmo.background import LCDM
from lgpd_cosmo.models import LGPDParams, CondensateParams, ElasticityParams, LGPDTransfer
from lgpd_cosmo.cmb import apply_modifications
from lgpd_cosmo.likelihoods import Likelihoods
from lgpd_cosmo.linear import GrowthModel
from lgpd_cosmo.mcmc import run_emcee


def main():
    repo = DataRepository(repo_root / "data")
    lcdm = LCDM()

    # Detect datasets
    have_tt = Path(repo.path('planck_tt_binned.csv')).exists()
    have_te = Path(repo.path('planck_te_binned.csv')).exists()
    have_ee = Path(repo.path('planck_ee_binned.csv')).exists()

    have_bao = any(Path(repo.path(n)).exists() for n in ["bao.csv", "bao_boss.csv", "bao_compilation.csv"])  # user to provide
    have_sne = Path(repo.path("sne_pantheon.csv")).exists()
    have_growth = Path(repo.path("growth_fsigma8.csv")).exists()

    print("Detected datasets:")
    print("  Planck TT:", have_tt, "TE:", have_te, "EE:", have_ee)
    print("  BAO:", have_bao, "SNe:", have_sne, "Growth:", have_growth)

    ell, cls0 = repo.load_planck_baseline()

    def loglike(theta):
        mu0, Sigma0, xi = theta
        lg = LGPDParams(xi_damp=xi)
        cp = CondensateParams(mu0=mu0)
        ep = ElasticityParams(sigma0=Sigma0)
        T = LGPDTransfer(lg, cp, ep)

        # spectra
        cls_mod = apply_modifications(ell, cls0, T)

        # likelihood
        L = Likelihoods()
        # helper
        cl_to_dl = lambda el, cl: el*(el+1.0)*cl/(2.0*np.pi)

        if have_tt:
            ett, Dlt, sigt = repo.load_simple_binned('planck_tt_binned.csv')
            L.add_planck_simple(ett, Dlt, sigt, ell, cl_to_dl(ell, cls_mod['TT']))
        if have_te:
            ete, Dlte, sigte = repo.load_simple_binned('planck_te_binned.csv')
            L.add_planck_simple(ete, Dlte, sigte, ell, cl_to_dl(ell, np.abs(cls_mod['TE'])))
        if have_ee:
            eee, Dlee, sigee = repo.load_simple_binned('planck_ee_binned.csv')
            L.add_planck_simple(eee, Dlee, sigee, ell, cl_to_dl(ell, cls_mod['EE']))

        # BAO/SNe/Growth
        if have_bao:
            # Load a generic BAO file (assume first found is fine for now)
            for candidate in ["bao.csv", "bao_boss.csv", "bao_compilation.csv"]:
                p = Path(repo.path(candidate))
                if p.exists():
                    bao = repo.load_bao(candidate)
                    break
            # Model DV/rd using LCDM distances (phenomenological stage)
            def DV_over_rd_model(z):
                # Very simplified DV/rd; assumes rd fixed; relative chi2 still useful.
                z = np.asarray(z)
                # Use standard DV definition approx (not exact). For exploration only.
                c = 299792.458
                Hz = np.array([lcdm.H(zi) for zi in z])
                chi = np.array([lcdm.comoving_distance(zi) for zi in z])
                DV = ((c*z*(chi**2)/Hz)**(1.0/3.0))
                rd = 147.1  # Mpc (placeholder constant); treat as effective rd; document in README
                return DV/rd
            L.add_bao(bao, DV_over_rd_model)

        if have_sne:
            sne = repo.load_sne("sne_pantheon.csv")
            def mu_model(z):
                z = np.asarray(z)
                DL = np.array([lcdm.luminosity_distance(zi) for zi in z])  # Mpc
                return 5.0*np.log10(np.maximum(DL, 1e-6)) + 25.0
            L.add_sne(sne, mu_model)

        if have_growth:
            growth = repo.load_growth("growth_fsigma8.csv")
            GM = GrowthModel(lcdm, mu_of_a_fn=lambda a: mu0)  # crude mapping: constant mu
            L.add_growth(growth, lambda z: GM.fsigma8(z, sigma8_0=0.8))

        chi2, dof, parts = L.summary()
        # Verbose breakdown printed occasionally is useful
        return -0.5*chi2

    # Quick run settings
    theta0 = np.array([0.0, 0.0, 0.01])
    priors = [(-0.6, 0.6), (-0.6, 0.6), (0.0, 0.05)]
    chain, lnp, sampler = run_emcee(loglike, theta0, priors, nwalkers=24, nsteps=400, nburn=100)

    best = np.argmax(lnp)
    print("Best-fit:", chain[best], "  chi2=", -2*lnp[best])

if __name__ == "__main__":
    main()
