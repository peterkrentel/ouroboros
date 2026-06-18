# Ouroboros Project Tracker

## North Star
Ship a hybrid LLM system that uses:
- Local Qwen (Ollama) for dev and fallback.
- Gemini Flash-Lite for hosted web traffic.

## Current Status
- [x] Python project scaffolded
- [x] FastAPI app running
- [x] uv workflow enabled
- [x] reset-venv target added
- [x] tests and build passing
- [x] architecture baseline documented

## Active Plan (Sprint A)

### Milestone A1: Provider Abstraction
- [x] Define provider interface
- [x] Implement Ollama provider via interface
- [x] Implement Gemini provider via interface
- [x] Add provider factory from environment

### Milestone A2: Runtime Policy
- [ ] Add provider fallback routing policy
- [ ] Add Gemini daily quota guard
- [ ] Add provider-specific timeout and retry policy

### Milestone A3: Quality
- [x] Add integration tests (ingest -> query -> eval)
- [ ] Add provider contract tests with mocks
- [ ] Add structured logs (provider, latency, token estimate)

## Deployment Path
- [ ] MVP host: web plus API shell on low-cost hosting
- [ ] Provider secret management configured
- [ ] Staging environment with hybrid routing verified

## Done Log
- 2026-06-17: Core modules, API, and tests created.
- 2026-06-17: uv-first local workflow verified.
- 2026-06-17: reset-venv and check flow validated.
- 2026-06-17: Runtime health endpoint validated.
- 2026-06-18: Milestone A1 provider abstraction completed (Ollama + Gemini + factory).
- 2026-06-18: API integration tests added for health, ingest/query, eval, and guard.

## Working Rules
- Update this file whenever task state changes.
- Prefer small, mergeable increments.
- Keep one in-progress milestone at a time.
