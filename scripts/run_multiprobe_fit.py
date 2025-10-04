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
import argparse
import json

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
    parser = argparse.ArgumentParser(description='Multi-probe LGPD fit (phenomenological)')
    parser.add_argument('--quick', action='store_true', help='Run a fast diagnostic (fewer steps, fixed seed)')
    parser.add_argument('--out', default=str(repo_root / 'outputs' / 'multiprobe'), help='Output directory')
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

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

        chi2_tt = chi2_te = chi2_ee = 0.0
        chi2_bao = chi2_sne = chi2_growth = 0.0

        if have_tt:
            ett, Dlt, sigt = repo.load_simple_binned('planck_tt_binned.csv')
            chi2_tt = L.add_planck_simple(ett, Dlt, sigt, ell, cl_to_dl(ell, cls_mod['TT']))
        if have_te:
            ete, Dlte, sigte = repo.load_simple_binned('planck_te_binned.csv')
            chi2_te = L.add_planck_simple(ete, Dlte, sigte, ell, cl_to_dl(ell, np.abs(cls_mod['TE'])))
        if have_ee:
            eee, Dlee, sigee = repo.load_simple_binned('planck_ee_binned.csv')
            chi2_ee = L.add_planck_simple(eee, Dlee, sigee, ell, cl_to_dl(ell, cls_mod['EE']))

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
            chi2_bao = L.add_bao(bao, DV_over_rd_model)

        if have_sne:
            sne = repo.load_sne("sne_pantheon.csv")
            def mu_model(z):
                z = np.asarray(z)
                DL = np.array([lcdm.luminosity_distance(zi) for zi in z])  # Mpc
                return 5.0*np.log10(np.maximum(DL, 1e-6)) + 25.0
            chi2_sne = L.add_sne(sne, mu_model)

        if have_growth:
            growth = repo.load_growth("growth_fsigma8.csv")
            GM = GrowthModel(lcdm, mu_of_a_fn=lambda a: mu0)  # crude mapping: constant mu
            chi2_growth = L.add_growth(growth, lambda z: GM.fsigma8(z, sigma8_0=0.8))

        chi2, dof, parts = L.summary()
        return -0.5*chi2

    # MCMC configuration
    theta0 = np.array([0.0, 0.0, 0.01])
    priors = [(-0.6, 0.6), (-0.6, 0.6), (0.0, 0.05)]
    nwalkers = 24
    nsteps = 400
    nburn = 100
    rng = None
    if args.quick:
        nwalkers = min(nwalkers, 24)
        nsteps = min(nsteps, 200)
        nburn = min(nburn, 80)
        rng = np.random.default_rng(12345)
        print("QUICK mode: nwalkers=", nwalkers, " nsteps=", nsteps, " nburn=", nburn)

    chain, lnp, sampler = run_emcee(
        loglike, theta0, priors, nwalkers=nwalkers, nsteps=nsteps, nburn=nburn,
        rng=rng if rng is not None else np.random.default_rng()
    )

    best_idx = int(np.argmax(lnp))
    best_theta = chain[best_idx]
    best_chi2 = float(-2*lnp[best_idx])

    # Save posterior for parsers
    np.savez(out_dir / 'multiprobe_posterior.npz', chain=chain, log_prob=lnp, param_names=np.array(['mu0','Sigma0','xi_damp']))

    # Recompute per-block chi2 at best-fit for parseable log lines
    mu0, Sigma0, xi = best_theta
    lg = LGPDParams(xi_damp=xi)
    cp = CondensateParams(mu0=mu0)
    ep = ElasticityParams(sigma0=Sigma0)
    T = LGPDTransfer(lg, cp, ep)
    cls_mod = apply_modifications(ell, cls0, T)
    Lbf = Likelihoods()
    cl_to_dl = lambda el, cl: el*(el+1.0)*cl/(2.0*np.pi)
    chi2_tt = chi2_te = chi2_ee = chi2_bao = chi2_sne = chi2_growth = 0.0
    if have_tt:
        ett, Dlt, sigt = repo.load_simple_binned('planck_tt_binned.csv')
        chi2_tt = Lbf.add_planck_simple(ett, Dlt, sigt, ell, cl_to_dl(ell, cls_mod['TT']))
    if have_te:
        ete, Dlte, sigte = repo.load_simple_binned('planck_te_binned.csv')
        chi2_te = Lbf.add_planck_simple(ete, Dlte, sigte, ell, cl_to_dl(ell, np.abs(cls_mod['TE'])))
    if have_ee:
        eee, Dlee, sigee = repo.load_simple_binned('planck_ee_binned.csv')
        chi2_ee = Lbf.add_planck_simple(eee, Dlee, sigee, ell, cl_to_dl(ell, cls_mod['EE']))
    if have_bao:
        # reload BAO like above
        for candidate in ["bao.csv", "bao_boss.csv", "bao_compilation.csv"]:
            p = Path(repo.path(candidate))
            if p.exists():
                bao = repo.load_bao(candidate)
                break
        def DV_over_rd_model(z):
            z = np.asarray(z)
            c = 299792.458
            Hz = np.array([lcdm.H(zi) for zi in z])
            chi = np.array([lcdm.comoving_distance(zi) for zi in z])
            DV = ((c*z*(chi**2)/Hz)**(1.0/3.0))
            rd = 147.1
            return DV/rd
        chi2_bao = Lbf.add_bao(bao, DV_over_rd_model)
    if have_sne:
        sne = repo.load_sne("sne_pantheon.csv")
        def mu_model(z):
            z = np.asarray(z)
            DL = np.array([lcdm.luminosity_distance(zi) for zi in z])
            return 5.0*np.log10(np.maximum(DL, 1e-6)) + 25.0
        chi2_sne = Lbf.add_sne(sne, mu_model)
    if have_growth:
        growth = repo.load_growth("growth_fsigma8.csv")
        GM = GrowthModel(lcdm, mu_of_a_fn=lambda a: mu0)
        chi2_growth = Lbf.add_growth(growth, lambda z: GM.fsigma8(z, sigma8_0=0.8))

    total_chi2, dof, parts = Lbf.summary()
    print(f"CHI2_TT={chi2_tt:.3f}")
    print(f"CHI2_TE={chi2_te:.3f}")
    print(f"CHI2_EE={chi2_ee:.3f}")
    print(f"CHI2_BAO={chi2_bao:.3f}")
    print(f"CHI2_SNE={chi2_sne:.3f}")
    print(f"CHI2_GROWTH={chi2_growth:.3f}")

    # Parseable summary lines
    print("PARAM_NAMES=mu0,Sigma0,xi_damp")
    print("BESTFIT chi2={:.3f} params={:.6f},{:.6f},{:.6f}".format(best_chi2, best_theta[0], best_theta[1], best_theta[2]))

if __name__ == "__main__":
    main()
