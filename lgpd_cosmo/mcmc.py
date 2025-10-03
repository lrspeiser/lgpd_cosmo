
import numpy as np
import warnings

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
    return chain, lnp, sampler


def compute_autocorr_time(sampler):
    """Compute integrated autocorrelation time for each parameter.
    Returns array of tau values, or None if estimation fails.
    """
    try:
        tau = sampler.get_autocorr_time(quiet=True)
        return tau
    except Exception as e:
        warnings.warn(f"Could not compute autocorrelation time: {e}")
        return None


def compute_gelman_rubin(chains_list):
    """Compute Gelman-Rubin R-hat for multiple chains.
    chains_list: list of arrays, each (N_samples, N_params)
    Returns: array of R-hat values (one per parameter)
    """
    if len(chains_list) < 2:
        warnings.warn("R-hat requires at least 2 chains; returning None")
        return None
    M = len(chains_list)
    N = min(c.shape[0] for c in chains_list)
    ndim = chains_list[0].shape[1]
    
    # Trim all chains to same length
    chains = np.array([c[:N, :] for c in chains_list])  # (M, N, ndim)
    
    # Within-chain variance
    W = np.mean(np.var(chains, axis=1, ddof=1), axis=0)
    
    # Between-chain variance
    chain_means = np.mean(chains, axis=1)  # (M, ndim)
    grand_mean = np.mean(chain_means, axis=0)  # (ndim,)
    B = N * np.var(chain_means, axis=0, ddof=1)
    
    # Pooled variance estimate
    var_plus = ((N - 1) * W + B) / N
    
    # R-hat
    Rhat = np.sqrt(var_plus / (W + 1e-12))
    return Rhat


def effective_sample_size(chain, tau=None):
    """Estimate ESS given chain and optional autocorrelation time.
    chain: (N, ndim)
    tau: array of length ndim (optional)
    Returns: array of ESS per parameter
    """
    N = chain.shape[0]
    ndim = chain.shape[1]
    if tau is None:
        # Rough estimate: assume tau ~ 10–50 for MCMC
        tau = np.full(ndim, 20.0)
    ess = N / (2.0 * tau)
    return ess
