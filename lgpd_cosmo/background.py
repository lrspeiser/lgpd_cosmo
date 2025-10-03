
import numpy as np
from scipy.integrate import quad

class LCDM:
    def __init__(self, H0=67.74, Omega_m=0.315, Omega_b=0.049, Omega_k=0.0, Tcmb=2.7255):
        self.H0 = H0
        self.h = H0/100.0
        self.Om = Omega_m
        self.Ob = Omega_b
        self.Ok = Omega_k
        self.Ode = 1.0 - Omega_m - Omega_k
        self.Tcmb = Tcmb

    def E(self, z, w=-1.0):
        return np.sqrt(self.Om*(1+z)**3 + self.Ok*(1+z)**2 + self.Ode*(1+z)**(3*(1+w)))

    def H(self, z, w=-1.0):
        return self.H0 * self.E(z, w=w)

    def comoving_distance(self, z, w=-1.0):
        c = 299792.458
        integrand = lambda zp: 1.0/self.E(zp, w=w)
        chi = quad(integrand, 0.0, z, limit=200)[0] * c / self.H0
        if self.Ok == 0.0:
            return chi
        sqrtOk = np.sqrt(np.abs(self.Ok))
        if self.Ok > 0:
            return np.sinh(sqrtOk*chi) / sqrtOk
        else:
            return np.sin(sqrtOk*chi) / sqrtOk

    def angular_diameter_distance(self, z, w=-1.0):
        return self.comoving_distance(z, w=w)/(1+z)

    def luminosity_distance(self, z, w=-1.0):
        return (1+z)*self.comoving_distance(z, w=w)

def w_eff(a, w0=-1.0, wa=0.0):
    """CPL parameterization: w(a) = w0 + wa(1-a)."""
    return w0 + wa*(1.0 - a)
