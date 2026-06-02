"""AI availability messaging (AI-6)."""

from __future__ import annotations

from quill.core.ai.availability import (
    AI_DISABLED_MESSAGE,
    describe_ai_availability,
)


def test_disabled_returns_master_switch_message() -> None:
    status = describe_ai_availability(enabled=False, available=True)
    assert status.ok is False
    assert status.message == AI_DISABLED_MESSAGE
    assert status.needs_key is False
    assert status.blocks_editor is False


def test_available_is_ready() -> None:
    status = describe_ai_availability(enabled=True, available=True)
    assert status.ok is True
    assert status.message == "AI is ready."
    assert status.blocks_editor is False


def test_unavailable_uses_reason() -> None:
    status = describe_ai_availability(
        enabled=True, available=False, reason="The model is still warming up."
    )
    assert status.ok is False
    assert "warming up" in status.message
    assert status.needs_key is False


def test_unavailable_without_reason_has_default() -> None:
    status = describe_ai_availability(enabled=True, available=False)
    assert status.ok is False
    assert status.message.strip() != ""


def test_missing_key_sets_needs_key() -> None:
    status = describe_ai_availability(
        enabled=True, available=False, reason="No API key set; add one in AI settings."
    )
    assert status.ok is False
    assert status.needs_key is True


def test_feature_name_is_woven_into_message() -> None:
    status = describe_ai_availability(
        enabled=True,
        available=False,
        reason="The model is unavailable.",
        feature="Rewrite",
    )
    assert status.message.startswith("Rewrite is unavailable:")


def test_never_blocks_editor() -> None:
    for enabled in (True, False):
        for available in (True, False):
            status = describe_ai_availability(enabled=enabled, available=available)
            assert status.blocks_editor is False
