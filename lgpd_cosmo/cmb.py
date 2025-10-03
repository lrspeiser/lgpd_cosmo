
import numpy as np
import warnings
from .models import LGPDTransfer

def load_baseline_cls(npz_path):
    data = np.load(npz_path)
    ell = data['ell']
    cls = {
        'TT': data['cltt'],
        'TE': data['clte'],
        'EE': data['clee']
    }
    if 'clbb' in data:
        cls['BB'] = data['clbb']
    if 'clpp' in data:
        cls['PP'] = data['clpp']
    return ell, cls

def _ensure_Dl(ell, Cl):
    """Convert Cl to Dl = ell(ell+1)Cl/2π if needed. We assume Cl here and convert to Dl for modulation."""
    ell = np.asarray(ell)
    Cl = np.asarray(Cl)
    Dl = ell*(ell+1.0)*Cl/(2.0*np.pi)
    return Dl

def _back_to_Cl(ell, Dl):
    return (2.0*np.pi)*Dl/(ell*(ell+1.0) + 1e-12)

class CMBSpectra:
    def __init__(self, ell, cls):
        self.ell = np.asarray(ell)
        self.cls = cls  # dict with keys 'TT','TE','EE', optional 'BB','PP'

    @classmethod
    def from_npz(cls, path):
        ell, cls = load_baseline_cls(path)
        return cls(ell, cls)

def apply_modifications(ell, cls, transfer: LGPDTransfer):
    """Apply phenomenological LGPD + μ/Σ modifications to baseline Cls.

    - Decoherence damping: multiplies Dl envelopes by D(ell).
    - Lensing amplitude: scales high-ℓ power via an A_L-like factor on TT/EE (simplified).
    - μ: small-scale driving subtly boosts acoustic contrast (we implement a mild ℓ-dependent factor).

    This is intentionally simple and meant for model exploration, not precision.
    """
    ell = np.asarray(ell)
    out = {}
    D_env = transfer.Dl_mod_factor(ell)
    A_L = transfer.lensing_amp()
    mu_today = transfer.mu_today_large_scales()

    def mod_Dl(Dl, kind):
        # Basic rule: apply envelope; lensing amplification on TT/EE for ell > ~300; μ boosts mid-ℓ contrast
        Dl_mod = Dl * D_env
        mask = ell > 300
        if kind in ('TT','EE'):
            Dl_mod[mask] *= A_L
        # μ boosts contrast around peaks (ℓ~100-1500): apply a tanh-windowed factor
        window = 0.5*(1.0 + np.tanh((ell-80)/80)) * (1.0 - np.exp(- (ell/1200.0)**2))
        Dl_mod *= (1.0 + 0.2*mu_today*window)
        return Dl_mod

    for key in cls:
        Dl = _ensure_Dl(ell, cls[key])
        Dl_mod = mod_Dl(Dl, key)
        out[key] = _back_to_Cl(ell, Dl_mod)
    return out

# Optional CLASS hook (best-effort; no dependency here)
def get_baseline_cls_from_class(cosmoparams=None, lmax=2500):
    try:
        from classy import Class
    except Exception as e:
        warnings.warn("CLASS not available: {}".format(e))
        return None, None
    cosmo = Class()
    params = dict(
        output = 'tCl,lCl,pCl',
        l_max_scalars = lmax,
        A_s = 2.07e-9,
        n_s = 0.965,
        h = 0.677,
        omega_b = 0.0224,
        omega_cdm = 0.12,
        tau_reio = 0.054,
        Omega_k = 0.0,
    )
    if cosmoparams:
        params.update(cosmoparams)
    cosmo.set(params)
    cosmo.compute()
    ells = np.arange(2, lmax+1)
    cl = cosmo.lensed_cl(lmax)
    conv = 2.0*np.pi/(ells*(ells+1.0))
    cltt = cl['tt'][2:lmax+1] * conv
    clte = cl['te'][2:lmax+1] * conv
    clee = cl['ee'][2:lmax+1] * conv
    clbb = cl['bb'][2:lmax+1] * conv
    try:
        clpp = cosmo.raw_cl_ps(lmax)['pp'][2:lmax+1] * conv
    except Exception:
        clpp = None
    cosmo.struct_cleanup()
    cosmo.empty()
    data = {'ell': ells, 'cltt': cltt, 'clte': clte, 'clee': clee, 'clbb': clbb}
    if clpp is not None:
        data['clpp'] = clpp
    return ells, data
