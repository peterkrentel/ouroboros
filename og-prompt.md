# OUROBOROS — Self-Improving Domain Intelligence System

## Project Vision
OUROBOROS is a domain-agnostic, self-improving AI expert system built on a Raft-inspired 
evolutionary cluster architecture. A small base LLM (Qwen3:8b) is the reasoning core. 
The system acquires knowledge autonomously, generates its own evaluation questions, 
fine-tunes challenger nodes, and promotes winners to leader via consensus — creating 
a compounding improvement loop with a built-in safety brake.

## Architecture Layers (bottom to top)
1. **Base model** — Qwen3:8b (Ollama), open weights, runs local or remote
2. **Knowledge layer** — domain-focused crawler + chunker → ChromaDB vector store
3. **RAG layer** — dynamic context injection at inference time
4. **Heuristic/prompt layer** — behavioral constraints, reasoning patterns, domain rules
5. **Fine-tuning pipeline** — Unsloth LoRA on challenger nodes when knowledge threshold hit
6. **Eval harness** — challenger generates questions from new knowledge, scores both nodes
7. **Raft promotion engine** — quorum-based leader election when challenger wins evals
8. **MCPToolGuard** — JWT-scoped tool access security layer (already built, integrate here)

## Cluster Topology
- 2 stable leader nodes (production inference)
- 2 challenger nodes (active learning/fine-tuning)
- Shared ChromaDB knowledge store
- GitHub Actions for orchestration
- k3s + Traefik for container runtime
- Vercel or Render for API gateway / UI

## Infrastructure Constraints
- Free tier first: Vercel (frontend/API), Render (backend services), GitHub Actions (CI/CD)
- Local: k3s cluster, Ollama, ChromaDB
- No paid GPU required for inference — M2 Pro compatible
- Fine-tuning: use Unsloth with LoRA (4-bit quantization), CPU-feasible for small LoRA adapters

## Domain Configuration
Domain is injected via config — the system is domain-agnostic.
Default domain for development: platform engineering / DevOps / MLOps
Knowledge sources: Kubernetes docs, CVEs, Terraform registry, GitHub, arXiv MLOps papers

## Key Design Decisions
- Challenger nodes cannot become leaders without winning eval quorum (safety brake)
- Eval questions are generated FROM new knowledge — tests genuine acquisition not memorization
- Eval quality itself is a metric — recursive improvement of measurement
- MCPToolGuard enforces JWT scope validation on all external tool calls
- All weight updates via LoRA adapters — base model never mutated, adapters are versioned

## Code Standards
- Python for ML pipeline (FastAPI, Unsloth, ChromaDB, LangChain/LlamaIndex)
- TypeScript for gateway and UI
- Docker + k3s for all services
- GitHub Actions for eval runs, fine-tuning triggers, and promotion workflows
- Everything infrastructure-as-code (Terraform or k3s manifests)

## File Structure
ouroboros/
├── core/           # base model interface, Ollama client
├── knowledge/      # crawler, chunker, ChromaDB ingestion
├── eval/           # question generation, scoring, promotion logic
├── finetune/       # Unsloth LoRA training pipeline
├── cluster/        # Raft-inspired node state machine
├── gateway/        # TypeScript API gateway
├── guard/          # MCPToolGuard integration
├── ui/             # Vercel-deployed frontend
├── infra/          # k3s manifests, Terraform
└── .github/        # Actions workflows

## When Writing Code
- Always consider which layer a component belongs to
- Eval harness must be stateless and reproducible
- Fine-tuning triggers are event-driven, not time-based
- Node state (leader/challenger/candidate) lives in etcd or a simple KV
- Never hardcode domain — always read from config