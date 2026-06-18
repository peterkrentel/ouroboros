from __future__ import annotations

from dataclasses import dataclass

import jwt


@dataclass
class ToolAccessDecision:
    allowed: bool
    reason: str


class MCPToolGuard:
    """Validates JWT scope claims for tool invocation requests."""

    def __init__(self, jwt_secret: str, required_scope: str) -> None:
        self.jwt_secret = jwt_secret
        self.required_scope = required_scope

    def validate(self, token: str) -> ToolAccessDecision:
        try:
            claims = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
        except Exception as exc:
            return ToolAccessDecision(allowed=False, reason=f"invalid_token:{exc}")

        scope = str(claims.get("scope", ""))
        scopes = scope.split()
        if self.required_scope not in scopes:
            return ToolAccessDecision(allowed=False, reason="missing_scope")

        return ToolAccessDecision(allowed=True, reason="ok")
