"""Streaming backends and assistant streaming (AI-1, AI-14)."""

from __future__ import annotations

from collections.abc import Callable

import pytest

import quill.core.ai.provider_backend as provider_backend
from quill.core.ai.backend import AIBackend
from quill.core.ai.provider_backend import ProviderChatBackend
from quill.core.assistant_ai import AssistantConnectionSettings


class _BlockingOnlyBackend(AIBackend):
    name = "blocking"

    def is_available(self) -> tuple[bool, str | None]:
        return True, None

    def respond(self, prompt: str) -> str:
        return "whole answer"


def test_base_backend_streams_once_as_fallback() -> None:
    backend = _BlockingOnlyBackend()
    received: list[str] = []
    text = backend.respond_stream("hi", received.append)
    assert text == "whole answer"
    assert received == ["whole answer"]


def _settings(provider: str = "openai") -> AssistantConnectionSettings:
    return AssistantConnectionSettings(provider=provider, host="https://api.openai.com", model="m")


def test_provider_backend_streams_deltas(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_stream(
        settings: object, api_key: str, prompt: str, on_delta: Callable[[str], None]
    ) -> tuple[str | None, str | None]:
        on_delta("Hel")
        on_delta("lo")
        return "Hello", None

    monkeypatch.setattr(provider_backend, "generate_assistant_response_stream", fake_stream)
    backend = ProviderChatBackend(_settings(), api_key="key")
    received: list[str] = []
    text = backend.respond_stream("hi", received.append)
    assert text == "Hello"
    assert received == ["Hel", "lo"]


def test_provider_backend_pre_stream_error_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    def failing_stream(
        settings: object, api_key: str, prompt: str, on_delta: Callable[[str], None]
    ) -> tuple[str | None, str | None]:
        return None, "network blip"

    def fake_blocking(settings: object, api_key: str, prompt: str) -> tuple[str | None, str | None]:
        return "fallback answer", None

    monkeypatch.setattr(provider_backend, "generate_assistant_response_stream", failing_stream)
    monkeypatch.setattr(provider_backend, "generate_assistant_response", fake_blocking)
    backend = ProviderChatBackend(_settings(), api_key="key")
    received: list[str] = []
    text = backend.respond_stream("hi", received.append)
    assert text == "fallback answer"
    assert received == ["fallback answer"]


def test_provider_backend_mid_stream_error_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def failing_after_emit(
        settings: object, api_key: str, prompt: str, on_delta: Callable[[str], None]
    ) -> tuple[str | None, str | None]:
        on_delta("partial")
        return None, "connection dropped"

    monkeypatch.setattr(provider_backend, "generate_assistant_response_stream", failing_after_emit)
    backend = ProviderChatBackend(_settings(), api_key="key")
    received: list[str] = []
    with pytest.raises(RuntimeError):
        backend.respond_stream("hi", received.append)
    # The partial fragment was still delivered; no duplicate retry.
    assert received == ["partial"]


def test_provider_backend_unavailable_raises() -> None:
    backend = ProviderChatBackend(_settings("off"), api_key="")
    with pytest.raises(RuntimeError):
        backend.respond_stream("hi", lambda _f: None)
