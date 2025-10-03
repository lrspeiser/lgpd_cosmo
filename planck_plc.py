
"""
Planck PLC (clik) adapter.

Usage:
    from lgpd_cosmo.planck_plc import PlanckPLC

    plc = PlanckPLC({
        "highl_TTTEEE": "/path/to/hi_l/plik/plik_dx11dr2_HM_v18_TTTEEE.clik",
        "lowl_TT": "/path/to/low_l/commander/commander_dx11d_..._TT.clik",
        "lowl_EE": "/path/to/low_l/lollipop/lollipop_dx11_..._EE.clik",
        "lensing": "/path/to/lensing/plik_lensing.clik_lensing"
    })

    # cl_dict expects *lensed* C_ell in K^2 unless units="muK"
    ell = np.arange(0, 4001)
    cl_dict = {"ell": ell, "TT": cltt, "EE": clee, "TE": clte, "BB": clbb, "PP": clpp}
    nll = plc.nll(cl_dict, units="K", nuis=None)
"""
import os
import numpy as np

class PlanckPLC:
    def __init__(self, like_paths: dict, verbose=True):
        try:
            import clik  # noqa: F401
        except Exception as e:
            raise ImportError("Could not import clik. Check your PLC install and PYTHONPATH.") from e

        self.clik = __import__("clik")
        self.likes = {}
        self.verbose = verbose

        for key, path in like_paths.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"Likelihood path not found for '{key}': {path}")
            try:
                if key == "lensing":
                    self.likes[key] = self.clik.clik_lensing(path)
                else:
                    self.likes[key] = self.clik.clik(path)
                if self.verbose:
                    print(f"[plc] loaded {key}: {path}")
            except Exception as e:
                raise RuntimeError(f"Failed to load clik likelihood '{key}' at {path}") from e

    @staticmethod
    def _ensure_muK2(arr, units="K"):
        arr = np.asarray(arr, dtype=float)
        if units == "K":
            return arr * 1.0e12
        elif units == "muK":
            return arr
        else:
            raise ValueError("units must be 'K' or 'muK'.")

    @staticmethod
    def _build_clik_vec(ell, cl_dict, lkl):
        has_cl = lkl.get_has_cl()  # {'tt':bool,'ee':bool,'bb':bool,'te':bool,...}
        order = []
        if has_cl.get('tt', False): order.append('TT')
        if has_cl.get('ee', False): order.append('EE')
        if has_cl.get('bb', False): order.append('BB')
        if has_cl.get('te', False): order.append('TE')

        lmin = lkl.get_lmin()
        lmax = lkl.get_lmax()

        vec = []
        for L in range(lmin, lmax+1):
            for spec in order:
                if spec in cl_dict and L < len(cl_dict[spec]):
                    vec.append(cl_dict[spec][L])
                else:
                    vec.append(0.0)
        return np.array(vec, dtype=float)

    @staticmethod
    def _build_lensing_vec(ell, clpp, lkl_len):
        v = np.asarray(clpp, dtype=float)
        if len(v) < lkl_len:
            pad = np.zeros(lkl_len - len(v))
            v = np.concatenate([v, pad])
        return v[:lkl_len]

    def nll(self, input_cls: dict, units="K", nuis: dict|None=None):
        ell = np.asarray(input_cls.get("ell"))
        if ell is None:
            raise ValueError("input_cls must contain 'ell' array.")
        cl_local = {}
        for k in ("TT","EE","BB","TE"):
            if k in input_cls:
                cl_local[k] = self._ensure_muK2(input_cls[k], units=units)

        # Lensing phi-phi: dimensionless, do NOT scale like temperature spectra
        clpp_local = None
        if "PP" in input_cls:
            clpp_local = np.asarray(input_cls["PP"], dtype=float)
        
        total = 0.0
        for key, lkl in self.likes.items():
            if key == "lensing":
                if clpp_local is None:
                    raise ValueError("Lensing likelihood loaded but 'PP' (phi-phi) not provided.")
                vec_len = lkl.get_lmax() + 1
                v = self._build_lensing_vec(ell, clpp_local, vec_len)
            else:
                v = self._build_clik_vec(ell, cl_local, lkl)

            pars = lkl.get_extra_parameter_names()
            if nuis is None:
                x = {name: lkl.get_extra_parameter_default(name) for name in pars}
                x_vec = np.array([x[name] for name in pars], dtype=float) if len(pars)>0 else np.empty(0)
            else:
                x_vec = np.array([nuis.get(name, lkl.get_extra_parameter_default(name)) for name in pars], dtype=float) if len(pars)>0 else np.empty(0)

            try:
                nll = lkl(v, x_vec)
            except Exception as e:
                raise RuntimeError(f"clik evaluation failed for '{key}': {e}")
            if self.verbose:
                print(f"[plc] {key}: -2lnL = {nll:.3f}")
            total += float(nll)
        return total
