"""Source-contract test for the AI model panel Fast/Strong tier picker (AI-22).

The live ``wx.Dialog`` is not runtime-instantiated in tests; the repo validates
dialog wiring through source contracts. This asserts that the AI model panel
surfaces the tier picker, switches tiers with a spoken announcement, and lets a
person assign a model to each tier.
"""

from __future__ import annotations

from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[3] / "quill" / "ui" / "ai_model_panel.py").read_text(
    encoding="utf-8"
)


def test_imports_tier_engine() -> None:
    assert "from quill.core.ai.model_tiers import" in SOURCE
    for name in ("switch_active_tier", "assign_model_to_tier", "active_tier_id", "load_tiers"):
        assert name in SOURCE


def test_builds_tier_section() -> None:
    assert "_build_tier_section" in SOURCE
    assert 'SetName("Active speed tier")' in SOURCE
    assert "Speed tier" in SOURCE


def test_tier_change_is_announced() -> None:
    # The active-tier change goes through the engine helper and is spoken.
    assert "switch_active_tier(self._tier_order[self.tier_choice.GetSelection()])" in SOURCE
    assert "self._announce(message)" in SOURCE


def test_per_tier_model_assignment() -> None:
    assert "_on_tier_model_change" in SOURCE
    assert "assign_model_to_tier(tier_id, model_id)" in SOURCE
