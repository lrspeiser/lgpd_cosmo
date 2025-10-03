
from setuptools import setup, find_packages

setup(
    name="lgpd_cosmo",
    version="0.1.0",
    description="Phenomenology sandbox for low-gravity decoherence and modified-gravity cosmology",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "emcee"
    ],
)
