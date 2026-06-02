"""Streaming chat parsing and generation (AI-1, AI-14)."""

from __future__ import annotations

import json

import pytest

import quill.core.assistant_ai as assistant_ai
from quill.core.assistant_ai import (
    AssistantConnectionSettings,
    generate_assistant_response_stream,
    iter_stream_text,
    parse_stream_event,
    stream_chat_endpoint,
)

# --- pure parsing contract --------------------------------------------------


def test_parse_stream_event_openai_delta() -> None:
    data = json.dumps({"choices": [{"delta": {"content": "Hel"}}]})
    assert parse_stream_event("openai", data) == "Hel"


def test_parse_stream_event_claude_content_block() -> None:
    data = json.dumps({"type": "content_block_delta", "delta": {"text": "lo"}})
    assert parse_stream_event("claude", data) == "lo"


def test_parse_stream_event_claude_ignores_other_types() -> None:
    data = json.dumps({"type": "message_start", "message": {}})
    assert parse_stream_event("claude", data) is None


def test_parse_stream_event_gemini_parts() -> None:
    data = json.dumps({"candidates": [{"content": {"parts": [{"text": "hi"}]}}]})
    assert parse_stream_event("gemini", data) == "hi"


def test_parse_stream_event_ollama_message() -> None:
    data = json.dumps({"message": {"content": "tok"}})
    assert parse_stream_event("ollama", data) == "tok"


def test_parse_stream_event_done_and_blank_are_none() -> None:
    assert parse_stream_event("openai", "[DONE]") is None
    assert parse_stream_event("openai", "") is None
    assert parse_stream_event("openai", "not json") is None


def test_iter_stream_text_sse_openai() -> None:
    lines = [
        b": keep-alive",
        b'data: {"choices": [{"delta": {"content": "Hel"}}]}',
        b'data: {"choices": [{"delta": {"content": "lo"}}]}',
        b"data: [DONE]",
        b'data: {"choices": [{"delta": {"content": "ignored"}}]}',
    ]
    assert list(iter_stream_text("openai", lines)) == ["Hel", "lo"]


def test_iter_stream_text_ndjson_ollama() -> None:
    lines = [
        json.dumps({"message": {"content": "a"}}),
        json.dumps({"message": {"content": "b"}}),
        json.dumps({"done": True, "message": {"content": ""}}),
    ]
    assert list(iter_stream_text("ollama", lines)) == ["a", "b"]


def test_stream_chat_endpoint_gemini_uses_sse() -> None:
    url = stream_chat_endpoint("gemini", "https://g.example", "gemini-2.0-flash")
    assert ":streamGenerateContent" in url
    assert "alt=sse" in url


# --- generation with a mocked transport -------------------------------------


class _FakeStreamResponse:
    def __init__(self, lines: list[bytes]) -> None:
        self._lines = lines

    def __enter__(self) -> _FakeStreamResponse:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    def __iter__(self):
        return iter(self._lines)


def _settings(provider: str = "openai") -> AssistantConnectionSettings:
    return AssistantConnectionSettings(provider=provider, host="https://api.openai.com", model="m")


def test_generate_stream_emits_deltas_and_returns_full_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lines = [
        b'data: {"choices": [{"delta": {"content": "Hel"}}]}',
        b'data: {"choices": [{"delta": {"content": "lo"}}]}',
        b"data: [DONE]",
    ]

    def fake_urlopen(request: object, timeout: float | None = None, context: object = None):
        return _FakeStreamResponse(lines)

    monkeypatch.setattr(assistant_ai, "urlopen", fake_urlopen)

    received: list[str] = []
    text, error = generate_assistant_response_stream(_settings(), "key", "hi", received.append)
    assert error is None
    assert text == "Hello"
    assert received == ["Hel", "lo"]


def test_generate_stream_off_provider_returns_error() -> None:
    received: list[str] = []
    text, error = generate_assistant_response_stream(_settings("off"), "key", "hi", received.append)
    assert text is None
    assert error is not None
    assert received == []


def test_generate_stream_empty_response_is_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: object, timeout: float | None = None, context: object = None):
        return _FakeStreamResponse([b"data: [DONE]"])

    monkeypatch.setattr(assistant_ai, "urlopen", fake_urlopen)
    received: list[str] = []
    text, error = generate_assistant_response_stream(_settings(), "key", "hi", received.append)
    assert text is None
    assert error is not None
    assert received == []
