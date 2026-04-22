PYTHON ?= python3

.PHONY: setup validate test preflight

setup:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"

validate:
	$(PYTHON) scripts/validate_strategy_matrix.py

test:
	$(PYTHON) -m pytest -q

preflight:
	$(PYTHON) scripts/preflight_check.py --root .

