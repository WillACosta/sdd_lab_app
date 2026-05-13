.DEFAULT_GOAL := help

VENV      := .venv
PIP       := $(VENV)/bin/pip
UVICORN   := $(VENV)/bin/uvicorn
STREAMLIT := $(VENV)/bin/streamlit
PYTEST    := $(VENV)/bin/pytest

BACKEND_PORT  ?= 8000
FRONTEND_PORT ?= 8501
BACKEND_URL   ?= http://localhost:$(BACKEND_PORT)

.PHONY: help install run backend frontend test clean reset

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

install: $(VENV)/bin/activate ## Create venv and install dependencies

run: install ## Run backend and frontend together (Ctrl-C stops both)
	@trap 'kill 0' INT TERM EXIT; \
	$(UVICORN) backend.main:app --reload --port $(BACKEND_PORT) & \
	BACKEND_URL=$(BACKEND_URL) $(STREAMLIT) run frontend/app.py --server.port $(FRONTEND_PORT) & \
	wait

backend: install ## Run only the FastAPI backend
	$(UVICORN) backend.main:app --reload --port $(BACKEND_PORT)

frontend: install ## Run only the Streamlit frontend
	BACKEND_URL=$(BACKEND_URL) $(STREAMLIT) run frontend/app.py --server.port $(FRONTEND_PORT)

test: install ## Run the test suite
	$(PYTEST)

clean: ## Remove caches and build artifacts
	rm -rf .pytest_cache *.egg-info
	find . -type d -name __pycache__ -not -path "./$(VENV)/*" -exec rm -rf {} +

reset: clean ## Remove venv AND saved data (destructive)
	rm -rf $(VENV) backend/data
