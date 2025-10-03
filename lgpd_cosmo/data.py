
import numpy as np
import os

class DataRepository:
    def __init__(self, root='data'):
        self.root = root

    def path(self, name):
        return os.path.join(self.root, name)

    def load_planck_baseline(self, name='planck_baseline_cls.npz'):
        p = self.path(name)
        if not os.path.exists(p):
            raise FileNotFoundError(f"Missing {p}. See README for expected format.")
        data = np.load(p)
        return data['ell'], {
            'TT': data['cltt'],
            'TE': data['clte'],
            'EE': data['clee']
        }

    def load_simple_binned(self, filename):
        p = self.path(filename)
        arr = np.loadtxt(p, delimiter=',', skiprows=1)
        # Expect columns [ell, Dl, sigma]
        return arr[:,0], arr[:,1], arr[:,2]

    def load_bao(self, filename):
        # Expect columns [z, DV_over_rd, sigma]
        arr = np.loadtxt(self.path(filename), delimiter=',', skiprows=1)
        return arr

    def load_sne(self, filename):
        # Expect columns [z, mu, sigma]
        arr = np.loadtxt(self.path(filename), delimiter=',', skiprows=1)
        return arr

    def load_growth(self, filename):
        # Expect columns [z, fsigma8, sigma]
        arr = np.loadtxt(self.path(filename), delimiter=',', skiprows=1)
        return arr
