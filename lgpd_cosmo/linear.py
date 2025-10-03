
import numpy as np
from scipy.integrate import odeint

class GrowthModel:
    """Solve linear growth D(a) with optional μ(a) modification to effective G.

    We integrate: D'' + [ (3/a) + (H'/H) ] D' - 1.5 Ω_m(a) [1+μ(a)] D / a^2 = 0

    Using a log-derivative change is more stable, but we keep it simple for clarity.
    """
    def __init__(self, lcdm, mu_of_a_fn=None):
        self.cosmo = lcdm
        self.mu_of_a_fn = mu_of_a_fn if mu_of_a_fn is not None else (lambda a: 0.0)

    def E(self, a, w=-1.0):
        z = 1.0/a - 1.0
        return self.cosmo.E(z, w=w)

    def Om_a(self, a):
        z = 1.0/a - 1.0
        Ez2 = self.cosmo.E(z)**2
        return self.cosmo.Om * a**(-3) / Ez2

    def dlnH_dlna(self, a, w=-1.0):
        z = 1.0/a - 1.0
        Om = self.cosmo.Om * a**(-3) / self.cosmo.E(z, w=w)**2
        Ode = self.cosmo.Ode / self.cosmo.E(z, w=w)**2
        return -0.5*(1+3*w*Ode)

    def solve(self, a_array, w=-1.0):
        a_array = np.asarray(a_array)
        a_array = np.sort(a_array)
        # State vector y = [D, D']
        def deriv(y, a):
            D, Dp = y
            mu = self.mu_of_a_fn(a)
            E = self.E(a, w=w)
            dlnH = self.dlnH_dlna(a, w=w)
            Om = self.Om_a(a)
            Dpp = - ( (3.0/a) + dlnH ) * Dp + 1.5 * Om * (1+mu) * D / (a*a)
            return [Dp, Dpp]

        # initial conditions deep in matter era
        a_init = a_array[0] if a_array[0] > 1e-4 else 1e-4
        y0 = [a_init, 1.0]  # growing mode ~ a
        sol = [y0]
        a_vals = [a_init]
        for ai in a_array[1:]:
            # integrate with simple Euler or small steps ODE - to avoid ODEINT complexities in notebook environment
            a_prev = a_vals[-1]
            y_prev = sol[-1]
            steps = max(5, int( (ai - a_prev)/1e-3 ))
            da = (ai - a_prev)/steps
            y = y_prev[:]
            a = a_prev
            for _ in range(steps):
                k1 = deriv(y, a)
                y_mid = [y[0]+0.5*da*k1[0], y[1]+0.5*da*k1[1]]
                k2 = deriv(y_mid, a+0.5*da)
                y = [y[0] + da*k2[0], y[1] + da*k2[1]]
                a += da
            sol.append(y)
            a_vals.append(ai)
        D = np.array([s[0] for s in sol])
        # Normalize D(a=1)=1
        D /= D[-1]
        return a_vals, D

    def fsigma8(self, z_array, sigma8_0=0.8):
        """Compute fσ8(z) given a present-day normalization σ8_0.

        Notes:
        - This is a phenomenological calculation using the current GrowthModel.
        - For full consistency, σ8_0 should be derived from a Boltzmann pipeline.
        """
        z = np.asarray(z_array)
        a = 1.0/(1.0+z)
        a_sorted = np.linspace(a.min()*0.99, 1.0, 800)
        a_vals, D = self.solve(a_sorted)
        a_vals = np.asarray(a_vals)
        # f = d ln D / d ln a
        lnD = np.log(np.maximum(D, 1e-12))
        lna = np.log(np.maximum(a_vals, 1e-8))
        dlnD_dlna = np.gradient(lnD, lna)
        f_interp = np.interp(a, a_vals, dlnD_dlna)
        D_interp = np.interp(a, a_vals, D)
        return f_interp * sigma8_0 * D_interp

    def E_G(self, z_array, Sigma_eff=0.0):
        """Crude E_G(z) estimator: E_G ≈ Ω_m(a) (1+Σ_eff) / f(z).

        This is a diagnostic, not a precision prediction without a full
        Boltzmann implementation. Σ_eff is an effective lensing modifier
        evaluated at scales relevant to galaxy-galaxy lensing.
        """
        z = np.asarray(z_array)
        a = 1.0/(1.0+z)
        # reuse f from fsigma8 with σ8_0 normalized out
        a_sorted = np.linspace(a.min()*0.99, 1.0, 800)
        a_vals, D = self.solve(a_sorted)
        lnD = np.log(np.maximum(D, 1e-12))
        lna = np.log(np.maximum(a_vals, 1e-8))
        f = np.interp(a, a_vals, np.gradient(lnD, lna))
        Om_a = np.array([self.Om_a(ai) for ai in a])
        return Om_a * (1.0 + Sigma_eff) / np.maximum(f, 1e-6)
