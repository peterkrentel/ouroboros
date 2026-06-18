# Ouroboros Architecture

## Purpose
Ouroboros is a domain self-improving LLM system with a hybrid inference strategy:
- Local model path (Qwen via Ollama) for development, privacy, and fallback.
- Hosted model path (Gemini Flash-Lite) for public web traffic and cost control.

This document defines the execution architecture in three stages.

## Stage 1: MVP Now (Current + Immediate Next)

### Components
- Web/API service: FastAPI app in this repository.
- Knowledge layer: local in-memory chunk store (replaceable).
- Inference providers:
  - Local: Ollama endpoint.
  - Hosted: Gemini API endpoint.
- Guard layer: JWT scope validation for external tool calls.

### Runtime Flow
1. Client calls API endpoint.
2. API retrieves relevant context from knowledge store.
3. API selects provider by environment setting.
4. API sends prompt to selected provider.
5. API returns normalized response payload.

### Provider Selection Policy
- Primary provider is environment-driven:
  - OUROBOROS_LLM_PROVIDER=ollama
  - OUROBOROS_LLM_PROVIDER=gemini
- Optional fallback behavior:
  - If primary fails and fallback is enabled, use secondary provider.

### MVP Constraints
- Single API instance is acceptable.
- No hard dependency on Kubernetes for MVP.
- No production-grade Raft rollout required yet.

## Stage 2: V1 Production

### Deployment Topology
- Frontend: Vercel.
- API service: container host (Cloud Run, Render, Fly, or GKE).
- Model serving:
  - Hosted default: Gemini Flash-Lite.
  - Local/Ollama retained for dev and emergency fallback.

### Data and State
- Replace in-memory knowledge store with persistent vector store.
- Persist node metadata and evaluation records in managed database.
- Store artifacts and adapters in object storage.

### Reliability and Security
- Secrets manager for API keys and JWT secret.
- Rate limiting and per-provider quotas.
- Structured logs with provider tag and latency fields.
- Health/readiness probes and alerting.

## Stage 3: Scale-Out System

### Cluster and Consensus
- Multi-node challenger and leader roles.
- Quorum-driven promotion policies.
- Separate eval workers from inference serving.

### Training and Promotion
- Event-driven fine-tuning triggers from knowledge growth.
- Reproducible eval runs and promotion gates.
- Versioned adapters and rollback-safe deployment.

### Eval Quality Design

The self-improving loop is only as good as its measurement. Three layers prevent the challenger from gaming its own evals.

#### Layer 1: Structural Question Validation (automated)
Every challenger-generated question must pass all of these gates before entering the eval pool:
- Has exactly one unambiguous correct answer.
- Answer is derivable from the new knowledge chunk, not from the base model's prior training.
- Cannot be answered yes/no — disqualified as too easy to game.
- Answer does not appear verbatim in the source — disqualifies pure retrieval, requires reasoning.

#### Layer 2: Adversarial Cross-Scoring (the key mechanism)
Before any question enters a promotion eval:
1. Leader node answers challenger's questions **without access to the new knowledge chunk**.
2. If the leader scores ≥70% on those questions, the batch is disqualified — the questions tested nothing new.
3. Only questions the leader **fails** are promoted to the eval pool.

This is self-contained and requires no human review. The leader's inability to answer is the proof that a question tests genuine knowledge acquisition.

#### Layer 3: Anchor Eval Set (ground truth brake)
- ~200 human-curated questions seeded before the system's first run.
- Every promotion cycle must maintain score on the anchor set — no regression allowed.
- A challenger that games its own evals will still fail on anchors it had no hand in writing.
- Anchors are versioned and append-only; never removed once added.

#### Promotion Gate
A challenger must satisfy all three conditions to trigger leader election:
1. Outscores the leader on the adversarially filtered question pool by a minimum delta (configurable, default 5%).
2. Does not regress on the anchor eval set.
3. Quorum of all non-candidate nodes confirms the score differential.

The minimum delta prevents thrashing — small noise in eval results does not trigger unnecessary promotions.

### Platform
- Move full orchestrated workloads to GKE when scale requires it.
- Dedicated GPU pool only for model-serving or training jobs.
- Keep web/API and model workloads isolated by node pool and policy.

## Environment Contract

Required baseline variables:
- OUROBOROS_DOMAIN
- OUROBOROS_LLM_PROVIDER
- OUROBOROS_LLM_MODEL
- OUROBOROS_OLLAMA_URL
- OUROBOROS_GUARD_JWT_SECRET
- OUROBOROS_REQUIRED_TOOL_SCOPE

Gemini-specific variables:
- OUROBOROS_GEMINI_API_KEY
- OUROBOROS_GEMINI_MODEL
- OUROBOROS_GEMINI_DAILY_LIMIT

Optional routing variables:
- OUROBOROS_LLM_FALLBACK_PROVIDER
- OUROBOROS_LLM_ENABLE_FALLBACK

## Immediate Build Order
1. Implement provider interface and factory.
2. Add Gemini provider client.
3. Add provider-normalized response schema.
4. Add quota guard for Gemini daily limits.
5. Add integration tests for ingest, query, eval with provider mocking.
