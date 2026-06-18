import jwt
import pytest
from fastapi.testclient import TestClient

import ouroboros.main as main_module
from ouroboros.config import Settings
from ouroboros.gateway.service import OuroborosService
from ouroboros.guard.tool_guard import MCPToolGuard

TEST_GUARD_SECRET = "integration-test-secret-at-least-32-bytes"


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    settings = Settings(
        llm_provider="ollama",
        llm_model="qwen3:8b",
        ollama_url="http://localhost:11434",
    )
    service = OuroborosService(settings=settings)

    # Keep integration tests deterministic and offline by stubbing model output.
    monkeypatch.setattr(service.llm, "generate", lambda prompt: f"mocked:{prompt[:64]}")
    monkeypatch.setattr(main_module, "service", service)
    monkeypatch.setattr(
        main_module,
        "guard",
        MCPToolGuard(jwt_secret=TEST_GUARD_SECRET, required_scope="tools:invoke"),
    )

    return TestClient(main_module.app)


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["project"] == "Ouroboros"


def test_ingest_then_query_flow(client: TestClient) -> None:
    ingest_response = client.post(
        "/knowledge/ingest",
        json={
            "source": "k8s-docs",
            "content": "Kubernetes deployments manage rollout strategy and replica updates.",
        },
    )
    assert ingest_response.status_code == 200
    ingest_body = ingest_response.json()
    assert ingest_body["chunks_added"] >= 1
    assert ingest_body["knowledge_size"] >= 1

    query_response = client.post("/query", json={"query": "How does rollout strategy work?"})
    assert query_response.status_code == 200
    query_body = query_response.json()
    assert query_body["answer"].startswith("mocked:")
    assert len(query_body["retrieved"]) >= 1


def test_eval_endpoint_runs(client: TestClient) -> None:
    client.post(
        "/knowledge/ingest",
        json={
            "source": "mlops-notes",
            "content": "Model evaluation requires reproducible harnesses and promotion gates.",
        },
    )

    response = client.post("/eval/run")
    assert response.status_code == 200

    body = response.json()
    assert "avg_leader_score" in body
    assert "avg_challenger_score" in body
    assert "results" in body


def test_guard_validation_endpoint(client: TestClient) -> None:
    token = jwt.encode({"scope": "tools:invoke"}, TEST_GUARD_SECRET, algorithm="HS256")

    response = client.post("/guard/validate", json={"token": token})

    assert response.status_code == 200
    body = response.json()
    assert body["allowed"] is True
    assert body["reason"] == "ok"
