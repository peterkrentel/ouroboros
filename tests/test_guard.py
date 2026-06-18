import jwt

from ouroboros.guard.tool_guard import MCPToolGuard

JWT_SECRET = "test-secret-at-least-32-bytes-long"


def test_guard_allows_required_scope() -> None:
    token = jwt.encode({"scope": "tools:invoke other:scope"}, JWT_SECRET, algorithm="HS256")
    guard = MCPToolGuard(jwt_secret=JWT_SECRET, required_scope="tools:invoke")

    decision = guard.validate(token)

    assert decision.allowed is True
    assert decision.reason == "ok"


def test_guard_rejects_missing_scope() -> None:
    token = jwt.encode({"scope": "other:scope"}, JWT_SECRET, algorithm="HS256")
    guard = MCPToolGuard(jwt_secret=JWT_SECRET, required_scope="tools:invoke")

    decision = guard.validate(token)

    assert decision.allowed is False
    assert decision.reason == "missing_scope"
