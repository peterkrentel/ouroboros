from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx


class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        """Generate a response for a prompt."""


@dataclass
class OllamaClient:
    base_url: str
    model: str
    timeout_seconds: float = 20.0

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        try:
            response = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout_seconds)
            response.raise_for_status()
            body = response.json()
            return str(body.get("response", "")).strip()
        except Exception:
            # Deterministic fallback keeps development flow working without local Ollama.
            return f"[fallback:{self.model}] {prompt[:300]}"


@dataclass
class GeminiClient:
    api_key: str
    model: str
    timeout_seconds: float = 20.0
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"

    def generate(self, prompt: str) -> str:
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt,
                        }
                    ]
                }
            ]
        }
        try:
            response = httpx.post(
                f"{self.base_url}/models/{self.model}:generateContent",
                params={"key": self.api_key},
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()

            candidates = body.get("candidates", [])
            if not candidates:
                return ""

            first = candidates[0]
            content = first.get("content", {})
            parts = content.get("parts", [])
            text_parts = [str(part.get("text", "")) for part in parts if isinstance(part, dict)]
            return "\n".join([part for part in text_parts if part]).strip()
        except Exception:
            return f"[fallback:{self.model}] {prompt[:300]}"


def create_llm_client(settings: object) -> LLMClient:
    provider = str(getattr(settings, "llm_provider", "ollama")).strip().lower()
    timeout_seconds = float(getattr(settings, "llm_timeout_seconds", 20.0))

    if provider == "ollama":
        return OllamaClient(
            base_url=str(getattr(settings, "ollama_url")),
            model=str(getattr(settings, "llm_model")),
            timeout_seconds=timeout_seconds,
        )

    if provider == "gemini":
        api_key = str(getattr(settings, "gemini_api_key", "")).strip()
        if not api_key:
            raise ValueError("OUROBOROS_GEMINI_API_KEY must be set when OUROBOROS_LLM_PROVIDER=gemini")

        return GeminiClient(
            api_key=api_key,
            model=str(getattr(settings, "gemini_model", "gemini-2.0-flash-lite")),
            timeout_seconds=timeout_seconds,
        )

    raise ValueError(f"Unsupported llm provider: {provider}")
