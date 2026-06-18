.PHONY: sync clean-venv reset-venv install dev run test build check pip-install pip-dev

UV ?= uv
PYTHON ?= python3

sync:
	$(UV) sync --extra dev

clean-venv:
	rm -rf .venv

reset-venv: clean-venv sync

install: sync

dev: sync

pip-install:
	$(PYTHON) -m pip install -e .

pip-dev:
	$(PYTHON) -m pip install -e .[dev]

run:
	$(UV) run uvicorn ouroboros.main:app --host 0.0.0.0 --port 8000 --reload

test:
	$(UV) run pytest -q

build:
	$(UV) run python -m compileall -q ouroboros
	$(UV) build --wheel --out-dir dist

check: test build
