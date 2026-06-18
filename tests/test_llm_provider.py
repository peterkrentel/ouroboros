from types import SimpleNamespace

import pytest

from ouroboros.core.llm import GeminiClient, OllamaClient, create_llm_client


def test_factory_builds_ollama_client() -> None:
    settings = SimpleNamespace(
        llm_provider="ollama",
        llm_model="qwen3:8b",
        ollama_url="http://localhost:11434",
        llm_timeout_seconds=12.0,
    )

    client = create_llm_client(settings)

    assert isinstance(client, OllamaClient)
    assert client.model == "qwen3:8b"
    assert client.timeout_seconds == 12.0


def test_factory_builds_gemini_client() -> None:
    settings = SimpleNamespace(
        llm_provider="gemini",
        gemini_model="gemini-2.0-flash-lite",
        gemini_api_key="test-key",
        llm_timeout_seconds=9.5,
    )

    client = create_llm_client(settings)

    assert isinstance(client, GeminiClient)
    assert client.model == "gemini-2.0-flash-lite"
    assert client.timeout_seconds == 9.5


def test_factory_rejects_gemini_without_key() -> None:
    settings = SimpleNamespace(
        llm_provider="gemini",
        gemini_model="gemini-2.0-flash-lite",
        gemini_api_key="",
        llm_timeout_seconds=20.0,
    )

    with pytest.raises(ValueError):
        create_llm_client(settings)
