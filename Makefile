## SNB — developer makefile
## Single-entrypoint commands for install, lint, test, run, docker.
## Everything here is opt-in: the existing node / studentflow targets are untouched.

SHELL := /bin/bash
PY ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
PIP := $(BIN)/pip

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help
	@awk 'BEGIN{FS":.*##";printf "\nUsage: make \033[36m<target>\033[0m\n\n"} /^[a-zA-Z_0-9-]+:.*##/ {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ---------------- Environment ----------------
$(VENV)/bin/activate:
	$(PY) -m venv $(VENV)
	$(PIP) install --upgrade pip wheel

.PHONY: install
install: $(VENV)/bin/activate ## Install package + dev extras in .venv
	$(PIP) install -e ".[dev]"

.PHONY: install-all
install-all: $(VENV)/bin/activate ## Install package + every optional extra
	$(PIP) install -e ".[dev,api,db,queue,scrape,llm]"

.PHONY: clean
clean: ## Remove build artefacts and venv
	rm -rf $(VENV) build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage

# ---------------- Quality gates ----------------
.PHONY: lint
lint: ## ruff check
	$(BIN)/ruff check snb tests

.PHONY: format
format: ## ruff format + import sort
	$(BIN)/ruff check --fix snb tests
	$(BIN)/ruff format snb tests

.PHONY: typecheck
typecheck: ## mypy on snb/
	$(BIN)/mypy snb

.PHONY: test
test: ## pytest
	$(BIN)/pytest

.PHONY: test-cov
test-cov: ## pytest with coverage
	$(BIN)/pytest --cov --cov-report=term --cov-report=html

.PHONY: check
check: lint typecheck test ## lint + typecheck + test

# ---------------- Runtime ----------------
.PHONY: cli
cli: ## Run the snb CLI (pass ARGS="...")
	$(BIN)/snb $(ARGS)

.PHONY: scheduler
scheduler: ## Run all scheduled agents
	$(BIN)/snb scheduler

.PHONY: shell
shell: ## Drop into a python REPL with snb preloaded
	$(BIN)/python -c "import snb; import IPython; IPython.embed()" || $(BIN)/python

# ---------------- Runtime: API ----------------
.PHONY: api
api: ## run the FastAPI server with hot-reload
	$(BIN)/uvicorn snb.api.app:app --reload --host 0.0.0.0 --port 8080

.PHONY: api-prod
api-prod: ## run the FastAPI server in production mode
	$(BIN)/uvicorn snb.api.app:app --host 0.0.0.0 --port $${PORT:-8080} --workers 2

# ---------------- Docker ----------------
.PHONY: up
up: ## docker compose dev stack (postgres + redis + app)
	docker compose -f docker-compose.dev.yml up --build

.PHONY: down
down: ## stop dev stack
	docker compose -f docker-compose.dev.yml down

.PHONY: logs
logs: ## tail dev stack logs
	docker compose -f docker-compose.dev.yml logs -f

.PHONY: build-prod
build-prod: ## build the production image locally
	docker build -f Dockerfile.prod -t snb-api:local .

.PHONY: run-prod
run-prod: ## run the production image locally
	docker run --rm -p 8080:8080 --env-file .env snb-api:local

# ---------------- Deploy ----------------
.PHONY: deploy-init
deploy-init: ## one-time Fly setup for the snb API
	./scripts/deploy-snb.sh init

.PHONY: deploy-secrets
deploy-secrets: ## push .env values as Fly secrets
	./scripts/deploy-snb.sh secrets

.PHONY: deploy
deploy: ## deploy to Fly.io
	./scripts/deploy-snb.sh deploy

.PHONY: deploy-status
deploy-status: ## show Fly app status
	./scripts/deploy-snb.sh status

.PHONY: deploy-logs
deploy-logs: ## stream Fly logs
	./scripts/deploy-snb.sh logs

# ---------------- Hooks ----------------
.PHONY: hooks
hooks: ## install pre-commit hooks
	$(BIN)/pre-commit install

.PHONY: precommit
precommit: ## run pre-commit on all files
	$(BIN)/pre-commit run --all-files
