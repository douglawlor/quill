"""Source-contract tests for EdSharp (EDS-1..21) UI wiring in main_frame.py.

These assert that every EdSharp command is registered (palette + Keymap Editor)
and surfaced in the Tools > EdSharp Tools menu, and that the read-only guard and
key/indent event hooks are wired. Live wx construction is impractical for the full
menu tree in CI, so we verify the wiring via the source text — the same strategy
used by the A11Y-4 dialog-contract guard and the menu-contract test.
"""

from __future__ import annotations

from pathlib import Path

import quill.ui.main_frame as main_frame_module
import quill.ui.main_frame_edsharp_menu as eds_menu_module
import quill.ui.main_frame_menu as main_frame_menu_module

_SOURCE = (
    Path(main_frame_module.__file__).read_text(encoding="utf-8")
    + "\n"
    + Path(main_frame_menu_module.__file__).read_text(encoding="utf-8")
)
_MENU_SOURCE = Path(eds_menu_module.__file__).read_text(encoding="utf-8")

# Every EdSharp command id that must be both registered and menu-wired.
_EDS_COMMAND_IDS = [
    "eds.insert_special_character",
    "eds.insert_date_time",
    "eds.calculate_and_insert_date",
    "eds.insert_file_content",
    "eds.new_document_from_clipboard",
    "eds.paste_html_as_markdown",
    "eds.number_lines",
    "eds.hard_wrap_lines",
    "eds.delete_to_line_start",
    "eds.delete_to_line_end",
    "eds.delete_to_document_start",
    "eds.delete_to_document_end",
    "eds.delete_paragraph",
    "eds.set_lines_first_not_second",
    "eds.set_lines_common",
    "eds.count_regex_matches",
    "eds.extract_regex_matches",
    "eds.speak_cursor_address",
    "eds.speak_document_status",
    "eds.speak_selection_length",
    "eds.go_to_percent",
    "eds.move_to_first_non_blank",
    "eds.move_to_last_non_blank",
    "eds.toggle_read_only_guard",
    "eds.toggle_clipboard_collector",
    "eds.collect_clipboard_now",
    "eds.toggle_key_describer",
    "eds.toggle_indent_announce",
    "eds.infer_indent",
    "eds.run_current_file",
    "eds.run_target_at_cursor",
    "eds.rename_current_file",
    "eds.delete_current_file",
]


def test_command_table_lists_every_eds_command() -> None:
    table_start = _MENU_SOURCE.index("def _edsharp_command_table")
    table_end = _MENU_SOURCE.index("def _register_edsharp_commands")
    table = _MENU_SOURCE[table_start:table_end]
    for command_id in _EDS_COMMAND_IDS:
        assert f'"{command_id}"' in table, f"{command_id} missing from command table"


def test_commands_are_registered_and_keymap_assignable() -> None:
    assert "self._register_edsharp_commands()" in _SOURCE
    assert "EdSharpMenuMixin" in _SOURCE.split("class MainFrame(")[1].split(")")[0]
    register = _MENU_SOURCE[_MENU_SOURCE.index("def _register_edsharp_commands") :][:400]
    # Registration goes through the standard command registry (palette + Keymap
    # Editor) and reads any user binding rather than shipping a default.
    assert "self.commands.register(" in register
    assert "self._binding_for(command_id)" in register


def test_every_command_is_menu_wired() -> None:
    # menus.md Phase 4: the EdSharp monolith is dissolved. Each command appears
    # in the command table AND in one of the recirculation helpers / the Power
    # Tools submenu, so it is both registered and menu-wired.
    for command_id in _EDS_COMMAND_IDS:
        assert _MENU_SOURCE.count(f'"{command_id}"') >= 2, (
            f"{command_id} not menu-wired (only present in the command table)"
        )
    # The cohesive remainder ships as Tools > Power Tools (the foreign "EdSharp"
    # brand name is gone); the recirculated groups are appended to conventional
    # menus from the menu build.
    assert 'AppendSubMenu(self._build_power_tools_menu(), "&Power Tools")' in _SOURCE
    for helper in (
        "_append_edsharp_insert_items",
        "_append_edsharp_edit_items",
        "_append_edsharp_file_create_items",
        "_append_edsharp_file_ops_items",
        "_append_edsharp_transform_line_items",
        "_append_edsharp_navigate_items",
        "_append_edsharp_search_items",
        "_append_edsharp_accessibility_items",
    ):
        assert f"self.{helper}(" in _SOURCE, f"{helper} is not called from the menu build"


def test_menu_items_are_bound() -> None:
    # The shared _eds_menu_item helper appends and binds every entry in one step.
    assert "self.frame.Bind(wx.EVT_MENU, lambda _e, run=handler: run(), id=item_id)" in _MENU_SOURCE


def test_read_only_guard_protects_edit_helpers() -> None:
    guard = (
        "if self._document_is_read_only():\n"
        '            self._set_status("Document is read-only")\n'
        "            return"
    )
    assert _SOURCE.count(guard) >= 3, "read-only guard missing from one of the _apply_* helpers"


def test_event_hooks_are_wired() -> None:
    char_hook = _SOURCE[_SOURCE.index("def _on_editor_char_hook") :][:200]
    assert "if self._maybe_describe_key(event):" in char_hook
    caret = _SOURCE[_SOURCE.index("def _on_editor_caret_activity") :][:200]
    assert "self._maybe_announce_indent()" in caret


def test_read_only_state_refreshes_on_tab_switch() -> None:
    activate = _SOURCE[_SOURCE.index("def _activate_tab") :][:1200]
    assert "self._refresh_read_only_state()" in activate


def test_read_only_state_refreshes_on_open() -> None:
    # Newly opened/selected tabs must re-apply a persisted read-only guard.
    create_tab = _SOURCE[_SOURCE.index("def _create_document_tab") :][:1400]
    assert "self._refresh_read_only_state()" in create_tab


def test_command_table_is_exactly_the_expected_ids_with_no_duplicates() -> None:
    import re

    table_start = _MENU_SOURCE.index("def _edsharp_command_table")
    table_end = _MENU_SOURCE.index("def _register_edsharp_commands")
    ids = re.findall(r'"(eds\.[a-z_]+)"', _MENU_SOURCE[table_start:table_end])
    assert len(ids) == len(_EDS_COMMAND_IDS)
    assert len(set(ids)) == len(ids), "duplicate command id in table"
    assert set(ids) == set(_EDS_COMMAND_IDS)


def test_every_table_handler_exists_on_the_actions_mixin() -> None:
    import re

    from quill.ui.main_frame_edsharp import EdSharpActionsMixin

    table_start = _MENU_SOURCE.index("def _edsharp_command_table")
    table_end = _MENU_SOURCE.index("def _register_edsharp_commands")
    handlers = re.findall(r"self\.([a-z_]+)[,)]", _MENU_SOURCE[table_start:table_end])
    assert handlers, "no handlers parsed from command table"
    for name in handlers:
        assert hasattr(EdSharpActionsMixin, name), f"missing handler {name} on EdSharpActionsMixin"
