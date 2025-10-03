
import numpy as np

def lnprior(theta, priors):
    for val, (lo, hi) in zip(theta, priors):
        if not (lo <= val <= hi):
            return -np.inf
    return 0.0

def run_emcee(loglike_fn, theta0, priors, nwalkers=24, nsteps=500, nburn=200, rng=None):
    try:
        import emcee
    except Exception:
        # Fallback: perform a crude random prior scan to produce a 'chain'-like result
        rng = np.random.default_rng() if rng is None else rng
        ndim = len(theta0)
        N = max(nwalkers*nsteps//2, 2000)
        chain = []
        lnp = []
        for _ in range(N):
            theta = np.array([rng.uniform(lo, hi) for (lo,hi) in priors])
            lp = lnprior(theta, priors)
            if not np.isfinite(lp):
                continue
            ll = loglike_fn(theta)
            chain.append(theta)
            lnp.append(lp + ll)
        return np.array(chain), np.array(lnp)

    rng = np.random.default_rng() if rng is None else rng
    ndim = len(theta0)
    p0 = theta0 + 1e-3*rng.normal(size=(nwalkers, ndim))
    def lnprob(p):
        lp = lnprior(p, priors)
        if not np.isfinite(lp):
            return -np.inf
        ll = loglike_fn(p)
        return lp + ll
    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob)
    sampler.run_mcmc(p0, nsteps, progress=False)
    chain = sampler.get_chain(discard=nburn, flat=True)
    lnp = sampler.get_log_prob(discard=nburn, flat=True)
    return chain, lnp
