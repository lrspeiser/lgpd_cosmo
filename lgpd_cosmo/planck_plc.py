import os
import logging

try:
    import clik  # Planck likelihood library
    _HAS_CLIK = True
except Exception:
    _HAS_CLIK = False

class PlanckPLCLike:
    """
    Thin adapter around the official Planck 'clik' likelihood.

    Important:
    - This adapter does NOT bundle Planck data. You must install PLC and
      set environment variables as described in docs/PLANCK_PLC_SETUP.md.
    - The LGPD spectra used here are phenomenologically modified; this is
      NOT yet a Boltzmann-consistent implementation. We will clearly log
      that status to avoid any silent misinterpretation.
    - We intentionally fail fast if 'clik' is unavailable or misconfigured.

    Usage outline (once PLC installed):
        like = PlanckPLCLike(plc_root=os.environ['CLIK_PATH'], which=['TT','TE','EE','lensing'])
        # Prepare a dict of Cl arrays (C_ell in microK^2) with keys 'TT','TE','EE' (and optionally 'PP' for lensing)
        lnL = like.loglike(ell, cls)

    References:
      - docs/PLANCK_PLC_SETUP.md
    """
    def __init__(self, plc_root: str, which=('TT','TE','EE','lensing')):
        if not _HAS_CLIK:
            raise ImportError("clik not found. See docs/PLANCK_PLC_SETUP.md for installation instructions.")
        if not plc_root or not os.path.isdir(plc_root):
            raise ValueError("Invalid plc_root. Set CLIK_PATH or pass a valid installation path.")
        self.plc_root = plc_root
        self.which = tuple(which)
        logging.getLogger(__name__).warning(
            "Using Planck PLC with phenomenological LGPD spectra (not Boltzmann-consistent)."
        )
        # TODO: open specific likelihood components (high-l TTTEEE, low-l TT, low-l EE, lensing) via clik.clik
        # This requires local file paths inside plc_root; we do not hardcode them here.
        self._handles = {}
        for comp in self.which:
            # Placeholder structure; users must provide exact paths in a future step.
            self._handles[comp] = None

    def loglike(self, ell, cls_dict):
        """
        Evaluate log-likelihood given ell and Cl dict.

        Parameters:
        - ell: array-like multipoles (must cover required ell range for the selected likelihood components).
        - cls_dict: {'TT': C_ell_TT, 'TE': C_ell_TE, 'EE': C_ell_EE, optional 'PP': C_ell_phiPhi}

        Returns:
        - lnL: float, the total log-likelihood.

        Note:
        - This method is a scaffold. It validates inputs and raises NotImplementedError until
          component likelihoods are opened and data are mapped into the clik expected format.
        """
        required = {'TT','TE','EE'} if any(c in ('TT','TE','EE') for c in self.which) else set()
        if any(k not in cls_dict for k in required):
            missing = [k for k in required if k not in cls_dict]
            raise ValueError(f"Missing Cl components: {missing}")
        if 'lensing' in self.which and 'PP' not in cls_dict:
            raise ValueError("Lensing requested but 'PP' (phi-phi) spectrum not provided.")
        # Validate types and shapes
        # Mapping into clik format is not implemented yet to avoid silent misuse.
        raise NotImplementedError(
            "Planck PLC evaluation not yet wired. Provide likelihood file paths and mapping to clik inputs."
        )
