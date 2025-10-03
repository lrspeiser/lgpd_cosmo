PY?=python
PIP?=pip

setup:
	. ./.venv/bin/activate || true; $(PY) -m pip install -e .; $(PY) -m pip install emcee

demo:
	. ./.venv/bin/activate || true; $(PY) examples/run_demo.py

real-data:
	. ./.venv/bin/activate || true; test -f data/planck_baseline_cls.npz || (echo "Missing data/planck_baseline_cls.npz. See README/paper.md for instructions."; exit 1); $(PY) examples/fit_with_real_data.py

paper:
	cd paper && pdflatex -interaction=nonstopmode -halt-on-error lgpd_unraveling_cosmology.tex && \
	bibtex lgpd_unraveling_cosmology && \
	pdflatex -interaction=nonstopmode -halt-on-error lgpd_unraveling_cosmology.tex && \
	pdflatex -interaction=nonstopmode -halt-on-error lgpd_unraveling_cosmology.tex

clean:
	rm -rf __pycache__ */__pycache__ *.aux *.bbl *.blg *.log *.out build dist *.egg-info
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	find . -name "*.pyc" -type f -delete