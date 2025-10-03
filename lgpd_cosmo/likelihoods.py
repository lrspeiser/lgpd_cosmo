
import numpy as np

class Likelihoods:
    def __init__(self):
        self.parts = []

    def add_planck_simple(self, ells, Dl_data, sigma, ells_model, Dl_model):
        # Interpolate model
        model_interp = np.interp(ells, ells_model, Dl_model, left=np.nan, right=np.nan)
        mask = np.isfinite(model_interp) & (sigma > 0)
        resid = (Dl_data[mask] - model_interp[mask]) / sigma[mask]
        chi2 = np.sum(resid**2)
        self.parts.append(('PlanckSimple', chi2, mask.sum()))
        return chi2

    def add_bao(self, bao_data, DV_over_rd_model):
        # bao_data: columns z, DV/rd, sigma ; model must be interpolated or computed at those z
        z = bao_data[:,0]; obs = bao_data[:,1]; sig = bao_data[:,2]
        model = DV_over_rd_model(z)
        resid = (obs - model)/sig
        chi2 = float(np.sum(resid**2))
        self.parts.append(('BAO', chi2, len(z)))
        return chi2

    def add_sne(self, sne_data, mu_model):
        z = sne_data[:,0]; obs = sne_data[:,1]; sig = sne_data[:,2]
        model = mu_model(z)
        resid = (obs - model)/sig
        chi2 = float(np.sum(resid**2))
        self.parts.append(('SNe', chi2, len(z)))
        return chi2

    def add_growth(self, growth_data, fs8_model):
        z = growth_data[:,0]; obs = growth_data[:,1]; sig = growth_data[:,2]
        model = fs8_model(z)
        resid = (obs - model)/sig
        chi2 = float(np.sum(resid**2))
        self.parts.append(('Growth', chi2, len(z)))
        return chi2

    def summary(self):
        dof = sum(n for _,_,n in self.parts)
        total = sum(c for _,c,_ in self.parts)
        return total, dof, self.parts
