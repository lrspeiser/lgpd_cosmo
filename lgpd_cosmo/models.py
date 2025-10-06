
import numpy as np

class LGPDParams:
    """Low-Gravity Photonic Decoherence parameters.

    Parameters
    ----------
    log10_Gamma0 : float
        Normalization (s^-1) of decoherence rate.
    a_star : float
        Critical scale factor-like parameter controlling low-gravity onset (proxy for cH^-1 scale).
    p : float
        Steepness of the low-gravity transition.
    T_lgpd : float
        Fixed-point blackbody temperature (Kelvin), ~2.725.
    xi_damp : float
        Multiplicative factor controlling anisotropy damping from decoherence (dimensionless).
    """
    def __init__(self, log10_Gamma0=-18.0, a_star=1.0, p=2.0, T_lgpd=2.725, xi_damp=0.0):
        self.log10_Gamma0 = log10_Gamma0
        self.a_star = a_star
        self.p = p
        self.T_lgpd = T_lgpd
        self.xi_damp = xi_damp

class CondensateParams:
    """Parameters for μ(k,z) (modified Newtonian potential)."""
    def __init__(self, mu0=0.0, k0=0.05, m=2.0, zt=1.0, n=2.0):
        self.mu0 = mu0  # amplitude today
        self.k0 = k0    # [h/Mpc]
        self.m = m      # scale slope
        self.zt = zt    # transition redshift
        self.n = n      # z steepness

class CondensateParamsBinned:
    """Two-bin redshift parameterization for μ(k,z):

    μ(k,z) = μ_low  for z <= z_split
           = μ_high for z >  z_split

    with optional k-dependence through the same scale factor as CondensateParams.
    """
    def __init__(self, mu_low=0.0, mu_high=0.0, z_split=0.5, k0=0.05, m=2.0):
        self.mu_low = mu_low
        self.mu_high = mu_high
        self.z_split = z_split
        self.k0 = k0
        self.m = m

class ElasticityParams:
    """Parameters for Σ(k,z) (lensing modification / anisotropic stress)."""
    def __init__(self, sigma0=0.0, k0=0.05, m=2.0, zt=1.0, n=2.0):
        self.sigma0 = sigma0
        self.k0 = k0
        self.m = m
        self.zt = zt
        self.n = n

class ThreadbareParams:
    """Finite coherence length ℓ_c controlling large-scale response."""
    def __init__(self, lc0=300.0, nu=1.0, zt=1.0, n=2.0):
        self.lc0 = lc0  # Mpc/h
        self.nu = nu
        self.zt = zt
        self.n = n

def S_of_z(z, zt, n):
    return 1.0 / (1.0 + ((1.0 + z)/(1.0 + zt))**n)

def mu_kz(k, z, pars: CondensateParams):
    """Scale- and redshift-dependent modification to Newtonian potential Φ → (1+μ)Φ."""
    scale = 1.0 / (1.0 + (k/pars.k0)**(-pars.m))
    return pars.mu0 * scale * S_of_z(z, pars.zt, pars.n)

def mu_kz_binned(k, z, pars: 'CondensateParamsBinned'):
    """Two-bin μ(k,z) using piecewise-constant amplitude in redshift, with k scaling.

    Notes:
    - Vectorized over z; k may be scalar or array broadcastable with z.
    - This is a phenomenological parameterization intended for trend testing.
    """
    z = np.asarray(z)
    scale = 1.0 / (1.0 + (np.asarray(k)/pars.k0)**(-pars.m))
    amp = np.where(z <= pars.z_split, pars.mu_low, pars.mu_high)
    return amp * scale

# Helper for growth-only usage (μ(a) without k)
# This maps a -> μ(a) corresponding to the binned redshift model
# a = 1/(1+z)

def mu_of_a_binned(a, pars: 'CondensateParamsBinned'):
    a = np.asarray(a)
    z = 1.0/np.maximum(a, 1e-8) - 1.0
    return np.where(z <= pars.z_split, pars.mu_low, pars.mu_high)

def sigma_kz(k, z, pars: ElasticityParams):
    scale = 1.0 / (1.0 + (k/pars.k0)**(-pars.m))
    return pars.sigma0 * scale * S_of_z(z, pars.zt, pars.n)

def coherence_length(z, pars: ThreadbareParams):
    return pars.lc0 * (1.0 + z)**(-pars.nu) * S_of_z(z, pars.zt, pars.n)

def gamma_of_a(a, pars: LGPDParams):
    """Decoherence rate Γ(a) with a low-gravity trigger around a_star.
    a ~ 1/(1+z). """
    Gamma0 = 10.0**pars.log10_Gamma0
    return Gamma0 * ( (pars.a_star**2) / (a*a + pars.a_star**2) )**pars.p

class LGPDTransfer:
    """A simple wrapper collecting the different effects that feed into observables.
    It provides multiplicative modulations for C_ell and simple damping from decoherence.
    """
    def __init__(self, lgpd: LGPDParams, cond: CondensateParams, elas: ElasticityParams, thread: ThreadbareParams=None):
        self.lgpd = lgpd
        self.cond = cond
        self.elas = elas
        self.thread = thread

    def Dl_mod_factor(self, ell):
        """Phenomenological anisotropy damping envelope from decoherence.
        We model it as exp[- xi_damp * ell(ell+1)/ell_d^2 ], with ell_d ~ 1500 by default.
        """
        ell = np.asarray(ell)
        ell_d = 1500.0
        return np.exp(- self.lgpd.xi_damp * ell*(ell+1.0) / (ell_d**2))

    def lensing_amp(self):
        """Return an effective lensing amplitude A_L ~ 1 + Σ at k~0.1 h/Mpc, z~2."""
        k = 0.1
        z = 2.0
        return 1.0 + sigma_kz(k, z, self.elas)

    def mu_today_large_scales(self):
        # Evaluate μ on large scales (k~0.01 h/Mpc) at z=0 for a rough amplitude proxy.
        if isinstance(self.cond, CondensateParams):
            return mu_kz(0.01, 0.0, self.cond)
        try:
            # Support two-bin model
            if isinstance(self.cond, CondensateParamsBinned):
                return mu_kz_binned(0.01, 0.0, self.cond)
        except NameError:
            # CondensateParamsBinned may not be defined if not imported; default to 0.
            pass
        return 0.0

