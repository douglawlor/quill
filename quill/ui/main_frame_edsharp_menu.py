"""EdSharp command registration and menu wiring for :class:`MainFrame`.

Extracted from ``main_frame.py`` to keep the monolith under its GATE-11 budget.
The mixin owns the single source of truth for the EdSharp (EDS-1..21) command
table, registers those commands with the palette/Keymap Editor, and recirculates
them into their conventional menus (menus.md Phase 4): the former
``Tools > EdSharp Tools`` monolith is dissolved so its commands live where users
expect them (Insert, Edit, File, Format, Navigate, Search, Tools > Accessibility)
and the cohesive remainder ships as ``Tools > Power Tools``. Every handler lives
on :class:`~quill.ui.main_frame_edsharp.EdSharpActionsMixin`; this mixin only
wires them into the accessible surfaces, so both stay in lock-step.
"""

from __future__ import annotations

from collections.abc import Callable


class EdSharpMenuMixin:
    """Palette + menu wiring for the EdSharp parity commands."""

    def _edsharp_command_table(self) -> list[tuple[str, str, Callable[[], None]]]:
        """EdSharp parity commands (EDS-1..21) as ``(id, label, handler)`` rows.

        Shared by command registration (palette + Keymap Editor) and the menu
        recirculation so the two never drift. None carry a default keybinding;
        EdSharp's own shortcuts collide with QUILL's curated keymap, so users bind
        them from the Keymap Editor instead.
        """
        return [
            (
                "eds.insert_special_character",
                "EdSharp: Insert Special Character",
                self.insert_special_character,
            ),
            ("eds.insert_date_time", "EdSharp: Insert Date and Time", self.insert_date_time),
            (
                "eds.calculate_and_insert_date",
                "EdSharp: Insert Calculated Date",
                self.calculate_and_insert_date,
            ),
            ("eds.insert_file_content", "EdSharp: Insert File Content", self.insert_file_content),
            (
                "eds.new_document_from_clipboard",
                "EdSharp: New Document from Clipboard",
                self.new_document_from_clipboard,
            ),
            (
                "eds.paste_html_as_markdown",
                "EdSharp: Paste HTML as Markdown",
                self.paste_html_as_markdown,
            ),
            ("eds.number_lines", "EdSharp: Number Lines", self.number_lines),
            ("eds.hard_wrap_lines", "EdSharp: Hard-Wrap Lines", self.hard_wrap_lines),
            (
                "eds.delete_to_line_start",
                "EdSharp: Delete to Line Start",
                self.delete_to_line_start,
            ),
            ("eds.delete_to_line_end", "EdSharp: Delete to Line End", self.delete_to_line_end),
            (
                "eds.delete_to_document_start",
                "EdSharp: Delete to Document Start",
                self.delete_to_document_start,
            ),
            (
                "eds.delete_to_document_end",
                "EdSharp: Delete to Document End",
                self.delete_to_document_end,
            ),
            ("eds.delete_paragraph", "EdSharp: Delete Paragraph", self.delete_paragraph),
            (
                "eds.set_lines_first_not_second",
                "EdSharp: Lines in First Block Only",
                self.set_lines_first_not_second,
            ),
            ("eds.set_lines_common", "EdSharp: Lines Common to Both Blocks", self.set_lines_common),
            ("eds.count_regex_matches", "EdSharp: Count Regex Matches", self.count_regex_matches),
            (
                "eds.extract_regex_matches",
                "EdSharp: Extract Regex Matches",
                self.extract_regex_matches,
            ),
            (
                "eds.speak_cursor_address",
                "EdSharp: Speak Cursor Address",
                self.speak_cursor_address,
            ),
            (
                "eds.speak_document_status",
                "EdSharp: Speak Document Status",
                self.speak_document_status,
            ),
            (
                "eds.speak_selection_length",
                "EdSharp: Speak Selection Length",
                self.speak_selection_length,
            ),
            ("eds.go_to_percent", "EdSharp: Go to Percent", self.go_to_percent),
            (
                "eds.move_to_first_non_blank",
                "EdSharp: Move to First Non-Blank",
                self.move_to_first_non_blank,
            ),
            (
                "eds.move_to_last_non_blank",
                "EdSharp: Move to Last Non-Blank",
                self.move_to_last_non_blank,
            ),
            (
                "eds.toggle_read_only_guard",
                "EdSharp: Toggle Read-Only Guard",
                self.toggle_read_only_guard,
            ),
            (
                "eds.toggle_clipboard_collector",
                "EdSharp: Toggle Clipboard Collector",
                self.toggle_clipboard_collector,
            ),
            (
                "eds.collect_clipboard_now",
                "EdSharp: Collect Clipboard Now",
                self.collect_clipboard_now,
            ),
            (
                "eds.toggle_key_describer",
                "EdSharp: Toggle Key Describer",
                self.toggle_key_describer,
            ),
            (
                "eds.toggle_indent_announce",
                "EdSharp: Toggle Indentation Announcements",
                self.toggle_indent_announce,
            ),
            ("eds.infer_indent", "EdSharp: Infer Indentation", self.infer_indent),
            ("eds.run_current_file", "EdSharp: Run Current File", self.run_current_file),
            (
                "eds.run_target_at_cursor",
                "EdSharp: Open Target at Cursor",
                self.run_target_at_cursor,
            ),
            ("eds.rename_current_file", "EdSharp: Rename Current File", self.rename_current_file),
            ("eds.delete_current_file", "EdSharp: Delete Current File", self.delete_current_file),
        ]

    def _register_edsharp_commands(self) -> None:
        for command_id, label, handler in self._edsharp_command_table():
            self.commands.register(command_id, label, handler, self._binding_for(command_id))

    def _edsharp_handlers(self) -> dict[str, Callable[[], None]]:
        return {
            command_id: handler for command_id, _label, handler in self._edsharp_command_table()
        }

    def _eds_menu_item(self, menu: object, command_id: str, label: str) -> None:
        """Append one EdSharp command to ``menu`` and bind its handler.

        Shared by every recirculation helper and the Power Tools submenu so the
        menu surface and the command palette stay in lock-step. The label shows
        any user-assigned keybinding via ``_menu_label``.
        """
        wx = self._wx
        item_id = wx.NewIdRef()
        menu.Append(item_id, self._menu_label(label, command_id))
        handler = self._edsharp_handlers()[command_id]
        self.frame.Bind(wx.EVT_MENU, lambda _e, run=handler: run(), id=item_id)

    # --- Recirculation helpers (menus.md Phase 4) --------------------------
    # Each appends a separator-led EdSharp group to a conventional menu.

    def _append_edsharp_insert_items(self, insert_menu: object) -> None:
        insert_menu.AppendSeparator()
        self._eds_menu_item(insert_menu, "eds.insert_special_character", "Special &Character...")
        self._eds_menu_item(insert_menu, "eds.insert_date_time", "Date and &Time")
        self._eds_menu_item(insert_menu, "eds.calculate_and_insert_date", "C&alculated Date...")
        self._eds_menu_item(insert_menu, "eds.insert_file_content", "File &Content...")

    def _append_edsharp_edit_items(self, edit_menu: object) -> None:
        edit_menu.AppendSeparator()
        self._eds_menu_item(edit_menu, "eds.paste_html_as_markdown", "Paste &HTML as Markdown")
        edit_menu.AppendSeparator()
        self._eds_menu_item(edit_menu, "eds.delete_to_line_start", "Delete to Line &Start")
        self._eds_menu_item(edit_menu, "eds.delete_to_line_end", "Delete to Line E&nd")
        self._eds_menu_item(edit_menu, "eds.delete_to_document_start", "Delete to Document &Top")
        self._eds_menu_item(edit_menu, "eds.delete_to_document_end", "Delete to Document Botto&m")
        self._eds_menu_item(edit_menu, "eds.delete_paragraph", "Delete Paragrap&h")

    def _append_edsharp_file_create_items(self, file_menu: object) -> None:
        self._eds_menu_item(file_menu, "eds.new_document_from_clipboard", "New from Cli&pboard")

    def _append_edsharp_file_ops_items(self, file_menu: object) -> None:
        self._eds_menu_item(file_menu, "eds.run_current_file", "R&un Current File")
        self._eds_menu_item(file_menu, "eds.run_target_at_cursor", "Open &Target at Cursor")
        self._eds_menu_item(file_menu, "eds.rename_current_file", "Re&name Current File...")
        self._eds_menu_item(file_menu, "eds.delete_current_file", "Dele&te Current File...")

    def _append_edsharp_transform_line_items(self, transform_menu: object) -> None:
        self._eds_menu_item(transform_menu, "eds.number_lines", "&Number Lines...")
        self._eds_menu_item(transform_menu, "eds.hard_wrap_lines", "&Hard-Wrap Lines...")

    def _append_edsharp_navigate_items(self, navigate_menu: object) -> None:
        navigate_menu.AppendSeparator()
        self._eds_menu_item(navigate_menu, "eds.go_to_percent", "Go to &Percent...")
        self._eds_menu_item(navigate_menu, "eds.move_to_first_non_blank", "First &Non-Blank")
        self._eds_menu_item(navigate_menu, "eds.move_to_last_non_blank", "&Last Non-Blank")

    def _append_edsharp_search_items(self, search_menu: object) -> None:
        search_menu.AppendSeparator()
        self._eds_menu_item(search_menu, "eds.count_regex_matches", "&Count Regex Matches...")
        self._eds_menu_item(search_menu, "eds.extract_regex_matches", "E&xtract Regex Matches...")
        search_menu.AppendSeparator()
        self._eds_menu_item(
            search_menu, "eds.set_lines_first_not_second", "Lines in First &Block Only"
        )
        self._eds_menu_item(search_menu, "eds.set_lines_common", "Lines Co&mmon to Both Blocks")

    def _append_edsharp_accessibility_items(self, accessibility_menu: object) -> None:
        accessibility_menu.AppendSeparator()
        self._eds_menu_item(accessibility_menu, "eds.speak_cursor_address", "Speak Cursor &Address")
        self._eds_menu_item(
            accessibility_menu, "eds.speak_document_status", "Speak Document Stat&us"
        )
        self._eds_menu_item(
            accessibility_menu, "eds.speak_selection_length", "Speak Selection &Length"
        )

    def _build_power_tools_menu(self) -> object:
        """Build the Tools > Power Tools submenu (the cohesive EdSharp remainder).

        These commands have no conventional menu home — they are editor-power
        utilities (read-only guard, clipboard collector, key describer, indent
        helpers) that belong together rather than scattered. The foreign
        "EdSharp" brand name is dropped (menus.md Phase 4 / §3.7).
        """
        wx = self._wx
        menu = wx.Menu()
        self._eds_menu_item(menu, "eds.toggle_read_only_guard", "Toggle &Read-Only Guard")
        self._eds_menu_item(menu, "eds.toggle_clipboard_collector", "Toggle Clipboard Co&llector")
        self._eds_menu_item(menu, "eds.collect_clipboard_now", "Collect Clipboard No&w")
        self._eds_menu_item(menu, "eds.toggle_key_describer", "Toggle &Key Describer")
        self._eds_menu_item(menu, "eds.toggle_indent_announce", "Toggle Indentation &Announcements")
        self._eds_menu_item(menu, "eds.infer_indent", "I&nfer Indentation...")
        return menu
