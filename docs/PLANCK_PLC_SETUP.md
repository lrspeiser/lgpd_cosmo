# Planck 2018 Official Likelihood (PLC/clik) Integration

This document explains how to install and link the official Planck 2018 likelihood (“PLC”, a.k.a. clik) so it can be used from this repository.

Why this matters
- Reviewers will expect results using the official Planck TT/TE/EE+lensing likelihoods with full nuisance parameter marginalization.
- We will keep the simplified binned path for quick tests, but the PLC path becomes the primary reference pipeline once installed.

What you will need
- macOS (tested), Linux also works.
- Xcode command line tools on macOS: xcode-select --install
- A working Python env (we use .venv in the repo)
- CMake, gsl, cfitsio (via Homebrew or MacPorts)

Install prerequisites (Homebrew)
- brew update
- brew install cmake gsl cfitsio

Obtain PLC (clik)
- You must accept the Planck Collaboration license and download the official likelihood packages.
- Go to: https://pla.esac.esa.int (Planck Legacy Archive) or the Planck 2018 likelihood page.
- Download the Planck 2018 likelihood (PLC 3.0 or latest) and unpack to a local directory, referred to below as <PLC_ROOT>.

Build clik
- cd <PLC_ROOT>
- mkdir build && cd build
- cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=<PLC_ROOT>/install
- make -j8
- make install

Environment variables (add to your shell rc or session)
- export CLIK_PATH=<PLC_ROOT>/install
- export DYLD_LIBRARY_PATH="$CLIK_PATH/lib:${DYLD_LIBRARY_PATH}"
- export LD_LIBRARY_PATH="$CLIK_PATH/lib:${LD_LIBRARY_PATH}"
- export PYTHONPATH="$CLIK_PATH/lib/python${PYTHONPATH:+:$PYTHONPATH}"

Python binding test
- "$REPO_ROOT"/.venv/bin/python -c "import clik; print('clik OK', clik.__file__)"

Wiring into this repository
- We provide an adapter at lgpd_cosmo/planck_plc.py that checks for clik and exposes a minimal interface to evaluate -2 ln L given Cls.
- The adapter does not ship Planck data; you must point it to the local likelihood paths.
- The adapter includes explicit checks and will raise informative errors if the environment is not configured correctly. This is intentional to avoid silent fallbacks.

Using PLC in analyses (once installed)
- See scripts/planck_plc_check.py for a sanity test that loads a likelihood and evaluates it at baseline Cls.
- Future: a scripts/run_planck_plc_fit.py will run an MCMC over our parameters plus nuisance parameters; we will integrate with an optimizer or sampler once clik is available.

Notes and caveats
- Our LGPD phenomenology currently modifies spectra after computation; a truly Boltzmann-consistent implementation requires integrating μ/Σ/LGPD into CLASS/CAMB. We will clearly label any PLC usage as “phenomenology-on-top”.
- Do not commit Planck likelihood files to the repo.
- If you switch Python versions, rebuild or re-point PYTHONPATH to clik for that version.

Troubleshooting
- ImportError: No module named clik -> Check PYTHONPATH and that <PLC_ROOT>/install/lib/python has clik.
- dyld: Library not loaded: libclik -> Check DYLD_LIBRARY_PATH or use install_name_tool on macOS.
- Version mismatches -> Clean build and reinstall.
