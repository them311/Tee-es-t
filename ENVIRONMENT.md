# SNB — Development Environment

Complete, modular, production-safe foundation for SNB Consulting automations
(agents, scrapers, integrations, pipelines) living alongside LFDS, StudentFlow
and the commercial-agent skill.

## What's in the box

```
snb/                       ← canonical Python package
├── agents/                autonomous units (base, registry, scheduler)
├── config/                typed settings + structured logging
├── core/                  base classes (HTTP client, retries, exceptions)
├── integrations/          Gmail, Airtable, HubSpot, Shopify, Notion
├── pipelines/             async pipeline primitives
├── scrapers/              resilient extraction base
├── services/              business-facing orchestration
├── utils/                 shared helpers
└── cli/                   typer CLI exposed as `snb`

tests/                     pytest suite (asyncio mode)
.github/workflows/         python-ci: ruff + mypy + pytest
.devcontainer/             reproducible VS Code / web dev container
docker-compose.dev.yml     postgres + redis + snb dev container
Dockerfile.dev             dev image with all extras
Makefile                   single entrypoint for all dev tasks
pyproject.toml             package, deps, tool configs (ruff/mypy/pytest)
.pre-commit-config.yaml    git hooks (ruff, mypy, secrets, EOL)
.env.example               every env var documented in one place
```

## Quick start

```bash
# 1. create a venv and install everything
make install-all

# 2. copy and edit env
cp .env.example .env

# 3. verify the CLI is wired
make cli ARGS="info"

# 4. run lint + typecheck + tests
make check

# 5. optional: install git hooks
make hooks
```

## Docker dev stack

```bash
# postgres + redis + snb container
docker compose -f docker-compose.dev.yml up --build

# one-shot CLI against the stack
docker compose -f docker-compose.dev.yml run --rm snb snb info
```

## Common commands

| Command              | Purpose                                          |
|----------------------|--------------------------------------------------|
| `make install`       | venv + package + dev extras                      |
| `make install-all`   | + api, db, queue, scrape, llm extras             |
| `make format`        | ruff fix + format                                |
| `make lint`          | ruff check                                       |
| `make typecheck`     | mypy                                             |
| `make test`          | pytest                                           |
| `make test-cov`      | pytest + coverage html                           |
| `make check`         | lint + typecheck + test                          |
| `make cli ARGS=...`  | run the `snb` CLI                                |
| `make scheduler`     | run all scheduled agents                         |
| `make up` / `down`   | docker dev stack                                 |
| `make hooks`         | install pre-commit                               |
| `make precommit`     | run hooks on all files                           |
| `make clean`         | nuke venv + caches                               |

## Optional extras

The base install is intentionally minimal. Pull only what you need:

```bash
pip install -e ".[api]"      # FastAPI + uvicorn
pip install -e ".[db]"       # SQLAlchemy async + asyncpg + alembic
pip install -e ".[queue]"    # redis + arq worker
pip install -e ".[scrape]"   # selectolax + bs4 + lxml + playwright
pip install -e ".[llm]"      # anthropic + openai SDKs
pip install -e ".[dev]"      # ruff, mypy, pytest, respx, pre-commit
```

Or everything at once:
```bash
pip install -e ".[dev,api,db,queue,scrape,llm]"
```

## Architecture principles

1. **Business value first** — every module maps to a real operational need
   (lead gen, CRM enrichment, outreach, scraping).
2. **Modular, replaceable** — integrations are thin wrappers; business logic
   lives in `services/` so connectors can be swapped without rewrites.
3. **Explicit over magic** — typed settings (`pydantic-settings`), typed HTTP
   errors, typed CLI (`typer`). No globals outside `get_settings()` and the
   agent registry.
4. **Async throughout** — `httpx.AsyncClient` + `asyncio` primitives. One
   execution model, no mixed sync/async surprises.
5. **Testable** — `respx` for HTTP mocking, `pytest-asyncio` for agents/
   pipelines. Base classes designed for easy fakes.

## CLI surface

```bash
snb info                           # env + version
snb agents list                    # registered agents
snb agents run <name> -p k=v       # one-shot run
snb scheduler                      # loop all scheduled agents
snb integration ping <name>        # sanity check an integration
```

## What exists alongside this (untouched)

| Dir / file             | Project                                       |
|------------------------|-----------------------------------------------|
| `src/`, `server/`      | LFDS quiz (React + Vite + Express)            |
| `studentflow/`         | Python FastAPI backend                        |
| `studentflow-web/`     | StudentFlow React frontend                    |
| `commercial-agent/`    | commercial-agent Claude skill                 |
| `docker-compose.yml`   | existing StudentFlow + LFDS dev stack         |
| `netlify/`, `fly.toml` | existing deployment configs                   |

This `snb/` package is the new **shared foundation** — sub-projects can depend
on it (`pip install -e ..` from inside `studentflow/` for example) without any
of them being forced to migrate today.

## Built-in agents

Registered automatically by `snb/bootstrap.py`; visible via `snb agents list`.
Every run is persisted to `data/job_log.jsonl` for the digest to consume.

| Agent              | Interval | Purpose                                             |
|--------------------|----------|-----------------------------------------------------|
| `shopify_sync`     | 1h       | pull Shopify customers → upsert HubSpot contacts    |
| `lead_enrichment`  | 15min    | new Airtable leads → HubSpot upsert + flag synced   |
| `outreach`         | 30min    | Airtable outreach queue → Claude draft → Gmail send |
| `daily_digest`     | 24h      | 24h ops summary → Claude rewrite → email to sender  |

Trigger manually:
```bash
snb agents run shopify_sync
snb agents run outreach -p batch_size=10
snb scheduler              # run them all on their intervals
```

## API surface (FastAPI)

Install the extra once (`pip install -e '.[api]'`), then:

```bash
make api                     # dev, hot-reload on :8080
```

| Route                       | Method | Purpose                                  |
|-----------------------------|--------|------------------------------------------|
| `/health`                   | GET    | liveness + version + registered agents   |
| `/webhook/lead`             | POST   | ingest JSON lead (Airtable + HubSpot)    |
| `/webhook/shopify`          | POST   | upsert Shopify order customer to HubSpot |
| `/agents/{name}/run`        | POST   | trigger any agent out-of-band (API key)  |

Secure the `/agents/*` endpoint with `SNB_API_KEY=<random>` in `.env`.

## Deploy

Two-process Fly.io app: one HTTP machine (API) + one worker (scheduler).
Shared volume `snb_data` persists the job log.

```bash
make deploy-init              # first time only
make deploy-secrets           # push .env -> Fly secrets
make deploy                   # build + roll out
make deploy-status            # app + machines
make deploy-logs              # stream logs
```

GitHub Actions: `.github/workflows/deploy-snb.yml` offers a manual trigger
(type "deploy" to confirm). Requires `FLY_API_TOKEN` repo secret.

## Next high-impact modules

- `snb/db/` — async SQLAlchemy session, Alembic migrations
- `snb/queue/` — arq worker (replace in-process scheduler for scale)
- `snb/integrations/google_sheets.py` — service account flow
- `snb/scrapers/playwright.py` — headless-browser base for JS-heavy sites
- `snb/services/outreach.py` — multi-step cadences (LinkedIn + email)
