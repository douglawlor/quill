"""EdSharp command registration and Tools-menu wiring for :class:`MainFrame`.

Extracted from ``main_frame.py`` to keep the monolith under its GATE-11 budget.
The mixin owns the single source of truth for the EdSharp (EDS-1..21) command
table, registers those commands with the palette/Keymap Editor, and builds the
``Tools > EdSharp Tools`` submenu. Every handler lives on
:class:`~quill.ui.main_frame_edsharp.EdSharpActionsMixin`; this mixin only wires
them into the accessible surfaces, so both stay in lock-step.
"""

from __future__ import annotations

from collections.abc import Callable


class EdSharpMenuMixin:
    """Palette + menu wiring for the EdSharp parity commands."""

    def _edsharp_command_table(self) -> list[tuple[str, str, Callable[[], None]]]:
        """EdSharp parity commands (EDS-1..21) as ``(id, label, handler)`` rows.

        Shared by command registration (palette + Keymap Editor) and the EdSharp
        Tools menu so the two never drift. None carry a default keybinding;
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

    def _build_edsharp_menu(self) -> object:
        """Build the Tools > EdSharp Tools submenu and bind every item.

        Items reuse the handlers from ``_edsharp_command_table`` so the menu and
        the command palette stay in lock-step. Labels show any user-assigned
        keybinding via ``_menu_label``.
        """
        wx = self._wx
        handlers = {
            command_id: handler for command_id, _label, handler in self._edsharp_command_table()
        }

        def item(menu: object, command_id: str, label: str) -> None:
            item_id = wx.NewIdRef()
            menu.Append(item_id, self._menu_label(label, command_id))
            handler = handlers[command_id]
            self.frame.Bind(wx.EVT_MENU, lambda _e, run=handler: run(), id=item_id)

        insert_menu = wx.Menu()
        item(insert_menu, "eds.insert_special_character", "Insert &Special Character...")
        item(insert_menu, "eds.insert_date_time", "Insert &Date and Time")
        item(insert_menu, "eds.calculate_and_insert_date", "Insert &Calculated Date...")
        item(insert_menu, "eds.insert_file_content", "Insert &File Content...")

        lines_menu = wx.Menu()
        item(lines_menu, "eds.number_lines", "&Number Lines...")
        item(lines_menu, "eds.hard_wrap_lines", "&Hard-Wrap Lines...")
        lines_menu.AppendSeparator()
        item(lines_menu, "eds.delete_to_line_start", "Delete to Line &Start")
        item(lines_menu, "eds.delete_to_line_end", "Delete to Line &End")
        item(lines_menu, "eds.delete_to_document_start", "Delete to Document &Top")
        item(lines_menu, "eds.delete_to_document_end", "Delete to Document &Bottom")
        item(lines_menu, "eds.delete_paragraph", "Delete &Paragraph")

        compare_menu = wx.Menu()
        item(compare_menu, "eds.set_lines_first_not_second", "Lines in &First Block Only")
        item(compare_menu, "eds.set_lines_common", "Lines &Common to Both Blocks")

        regex_menu = wx.Menu()
        item(regex_menu, "eds.count_regex_matches", "&Count Matches...")
        item(regex_menu, "eds.extract_regex_matches", "&Extract Matches...")

        go_menu = wx.Menu()
        item(go_menu, "eds.go_to_percent", "Go to &Percent...")
        item(go_menu, "eds.move_to_first_non_blank", "&First Non-Blank")
        item(go_menu, "eds.move_to_last_non_blank", "&Last Non-Blank")

        speak_menu = wx.Menu()
        item(speak_menu, "eds.speak_cursor_address", "Cursor &Address")
        item(speak_menu, "eds.speak_document_status", "Document &Status")
        item(speak_menu, "eds.speak_selection_length", "Selection &Length")

        menu = wx.Menu()
        menu.AppendSubMenu(insert_menu, "&Insert")
        menu.AppendSubMenu(lines_menu, "&Lines")
        menu.AppendSubMenu(compare_menu, "Compare &Blocks")
        menu.AppendSubMenu(regex_menu, "Find with &Regex")
        menu.AppendSubMenu(go_menu, "&Go")
        menu.AppendSubMenu(speak_menu, "Spea&k")
        menu.AppendSeparator()
        item(menu, "eds.new_document_from_clipboard", "&New Document from Clipboard")
        item(menu, "eds.paste_html_as_markdown", "Paste &HTML as Markdown")
        menu.AppendSeparator()
        item(menu, "eds.toggle_read_only_guard", "Toggle &Read-Only Guard")
        item(menu, "eds.toggle_clipboard_collector", "Toggle Clipboard Co&llector")
        item(menu, "eds.collect_clipboard_now", "Collect Clipboard No&w")
        item(menu, "eds.toggle_key_describer", "Toggle &Key Describer")
        item(menu, "eds.toggle_indent_announce", "Toggle Indentation &Announcements")
        item(menu, "eds.infer_indent", "I&nfer Indentation...")
        menu.AppendSeparator()
        item(menu, "eds.run_current_file", "R&un Current File")
        item(menu, "eds.run_target_at_cursor", "&Open Target at Cursor")
        item(menu, "eds.rename_current_file", "Rename Current File...")
        item(menu, "eds.delete_current_file", "Delete Current File...")
        return menu
