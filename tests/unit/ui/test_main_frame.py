"""Tests for MainFrame dialog contract helpers (M-28: crash recovery focus)."""

from __future__ import annotations

import re
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[3] / "quill" / "ui" / "main_frame.py").read_text(
    encoding="utf-8"
)


def test_show_modal_dialog_has_restore_editor_focus_param() -> None:
    # M-28: _show_modal_dialog must accept restore_editor_focus to prevent
    # focus-racing in loops that re-show the same dialog.
    assert "restore_editor_focus: bool = True" in SOURCE


def test_crash_recovery_loop_does_not_steal_focus() -> None:
    # M-28: The crash-recovery re-show loop must pass restore_editor_focus=False
    # so editor.SetFocus is not called between loop iterations, which would race
    # with the dialog's own focus management.
    assert "restore_editor_focus=False" in SOURCE
    # The _show_modal_dialog call for Crash Recovery must carry the flag.
    crash_call = (
        "_show_modal_dialog(\n"
        '                    dialog, "Crash Recovery", restore_editor_focus=False\n'
        "                )"
    )
    assert crash_call in SOURCE


def test_document_tab_declares_language_profile_slots() -> None:
    # #263: _DocumentTab is @dataclass(slots=True) — every attribute assigned
    # elsewhere must be declared as a slot, or the assignment raises
    # AttributeError. _on_notebook_page_changed and the language picker
    # both write _language_profile and _language_profile_pinned; the slots
    # are what keeps those writes from crashing.
    tab_block_match = re.search(
        r"^class _DocumentTab:.*?(?=^class |\Z)", SOURCE, re.MULTILINE | re.DOTALL
    )
    assert tab_block_match is not None, "_DocumentTab block not found"
    block = tab_block_match.group(0)
    assert "_language_profile: object = None" in block
    assert "_language_profile_pinned: bool = False" in block


def test_open_startup_logs_handler_is_defined() -> None:
    # #263: Help > View Startup Logs... handler. Uses _reveal_in_explorer so
    # the OS opens the file in the default app.
    assert "def open_startup_logs(self) -> None" in SOURCE
    assert "startup-errors.log" in SOURCE


def test_help_view_startup_logs_menu_id_is_defined() -> None:
    # The Help > View Startup Logs... wiring requires the new id to appear in
    # both the menu build and the EVT_MENU binding.
    menu_src = (
        Path(__file__).resolve().parents[3] / "quill" / "ui" / "main_frame_menu.py"
    ).read_text(encoding="utf-8")
    assert "_id_view_startup_logs" in menu_src
    assert "help.view_startup_logs" in menu_src


def test_startup_speech_gate_uses_quiet_status() -> None:
    # #263: The "Ready. Tip..." and "Theme applied..." announcements must
    # keep showing in the status bar but stay silent on the screen reader
    # when announcement_startup_tips_enabled is off.
    assert "announcement_startup_tips_enabled" in SOURCE
    assert "_set_status_quiet" in SOURCE
