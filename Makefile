SHELL := /bin/bash

.PHONY: help setup api ui dev

help:
	@echo "Available commands:"
	@echo "  make setup  - create venv (Python 3.10-3.13) and install dependencies"
	@echo "  make api    - run FastAPI backend"
	@echo "  make ui     - run Gradio frontend"
	@echo "  make dev    - run backend + frontend together"
	@echo "  make setup PYTHON=python3.11  - force a specific Python binary"

setup:
	@PY_BIN="$${PYTHON:-}"; \
	if [ -z "$$PY_BIN" ]; then \
	  for bin in python3.13 python3.12 python3.11 python3.10; do \
	    if command -v $$bin >/dev/null 2>&1; then PY_BIN="$$bin"; break; fi; \
	  done; \
	fi; \
	if [ -z "$$PY_BIN" ]; then \
	  echo "No compatible Python (3.10-3.13) found."; \
	  echo "Install one (example on macOS: brew install python@3.12), then run:"; \
	  echo "make setup PYTHON=python3.12"; \
	  exit 1; \
	fi; \
	echo "Using $$PY_BIN"; \
	"$$PY_BIN" -m venv --clear .venv; \
	source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

api:
	./scripts/start_api.sh

ui:
	./scripts/start_ui.sh

dev:
	./scripts/start_all.sh
