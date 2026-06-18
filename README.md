# Ouroboros

Raft-inspired domain self-improving LLM system with a runnable local API.

## What Is Included

- Python package scaffold matching the architecture layers:
	- `ouroboros/core`
	- `ouroboros/knowledge`
	- `ouroboros/eval`
	- `ouroboros/finetune`
	- `ouroboros/cluster`
	- `ouroboros/guard`
	- `ouroboros/gateway`
- FastAPI app with endpoints for ingest, query, eval, and guard validation.
- Build/test workflow via `Makefile` and `pyproject.toml`.

## Quick Start

```bash
make sync
make run
```

Open `http://localhost:8000/docs` for the interactive API.

The default workflow uses `uv` and creates a local `.venv` automatically.

To recreate the environment from scratch in one command:

```bash
make reset-venv
```

If you prefer pip, use:

```bash
make pip-dev
uvicorn ouroboros.main:app --host 0.0.0.0 --port 8000 --reload
```

## Build

```bash
make check
```

This runs tests and package build checks.

## Environment Variables

All environment variables use the `OUROBOROS_` prefix:

- `OUROBOROS_LLM_PROVIDER` (`ollama` or `gemini`)
- `OUROBOROS_DOMAIN`
- `OUROBOROS_LLM_MODEL`
- `OUROBOROS_OLLAMA_URL`
- `OUROBOROS_GEMINI_MODEL`
- `OUROBOROS_GEMINI_API_KEY`
- `OUROBOROS_GUARD_JWT_SECRET`
- `OUROBOROS_REQUIRED_TOOL_SCOPE`

Example provider selection:

```bash
export OUROBOROS_LLM_PROVIDER=gemini
export OUROBOROS_GEMINI_API_KEY=your-key
export OUROBOROS_GEMINI_MODEL=gemini-2.0-flash-lite
```

## Example API Calls

```bash
curl -s http://localhost:8000/health | jq

curl -s -X POST http://localhost:8000/knowledge/ingest \
	-H 'Content-Type: application/json' \
	-d '{"source":"k8s-docs","content":"Kubernetes deployments manage replicated pods and rollout strategy."}' | jq

curl -s -X POST http://localhost:8000/query \
	-H 'Content-Type: application/json' \
	-d '{"query":"How do deployments handle rollout?"}' | jq
```
