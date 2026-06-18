from fastapi import FastAPI
from pydantic import BaseModel

from ouroboros.config import settings
from ouroboros.gateway.service import OuroborosService
from ouroboros.guard.tool_guard import MCPToolGuard

app = FastAPI(title="Ouroboros API", version="0.1.0")
service = OuroborosService(settings=settings)
guard = MCPToolGuard(jwt_secret=settings.guard_jwt_secret, required_scope=settings.required_tool_scope)


class IngestRequest(BaseModel):
    source: str
    content: str


class AskRequest(BaseModel):
    query: str


class GuardRequest(BaseModel):
    token: str


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "project": settings.project_name,
        "domain": settings.domain,
    }


@app.post("/knowledge/ingest")
def ingest(req: IngestRequest) -> dict[str, object]:
    return service.ingest(source=req.source, content=req.content)


@app.post("/query")
def query(req: AskRequest) -> dict[str, object]:
    result = service.ask(query=req.query)
    return {
        "answer": result.answer,
        "retrieved": result.retrieved,
    }


@app.post("/eval/run")
def run_eval() -> dict[str, object]:
    return service.run_eval_round()


@app.post("/guard/validate")
def validate_guard(req: GuardRequest) -> dict[str, object]:
    decision = guard.validate(req.token)
    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
    }
