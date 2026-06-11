"""Abbreviation Manager dialog — create, edit, and organise abbreviations.

Hardened dialog (A11Y-4): exposes show() and close() so callers never call
ShowModal or Destroy directly on the inner wx.Dialog.
"""

from __future__ import annotations

import wx

from quill.core.abbreviations import (
    Abbreviation,
    AbbreviationLibrary,
    save_abbreviation_library,
)


class _AbbreviationEditDialog:
    """Inner dialog for creating or editing a single abbreviation."""

    def __init__(
        self,
        parent: object,
        abbreviation: Abbreviation | None = None,
    ) -> None:
        title = "Edit Abbreviation" if abbreviation else "New Abbreviation"
        self.dialog = wx.Dialog(
            parent,
            title=title,
            style=wx.DEFAULT_DIALOG_STYLE,
        )
        self.dialog.SetMinSize(wx.Size(420, 280))

        root = wx.BoxSizer(wx.VERTICAL)
        grid = wx.FlexGridSizer(cols=2, hgap=8, vgap=6)
        grid.AddGrowableCol(1)

        grid.Add(wx.StaticText(self.dialog, label="&Abbreviation:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._abbr_ctrl = wx.TextCtrl(self.dialog)
        self._abbr_ctrl.SetName("Abbreviation trigger word")
        grid.Add(self._abbr_ctrl, 1, wx.EXPAND)

        grid.Add(wx.StaticText(self.dialog, label="&Expansion:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._exp_ctrl = wx.TextCtrl(
            self.dialog, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER, size=(-1, 70)
        )
        self._exp_ctrl.SetName("Expansion text — use ${cursor}, ${date}, ${time}, ${clipboard}")
        grid.Add(self._exp_ctrl, 1, wx.EXPAND)

        grid.Add(wx.StaticText(self.dialog, label="&Description:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self._desc_ctrl = wx.TextCtrl(self.dialog)
        self._desc_ctrl.SetName("Optional description")
        grid.Add(self._desc_ctrl, 1, wx.EXPAND)

        root.Add(grid, 0, wx.EXPAND | wx.ALL, 10)

        self._case_ctrl = wx.CheckBox(self.dialog, label="&Case sensitive")
        self._enabled_ctrl = wx.CheckBox(self.dialog, label="E&nabled")
        self._enabled_ctrl.SetValue(True)
        root.Add(self._case_ctrl, 0, wx.LEFT | wx.BOTTOM, 10)
        root.Add(self._enabled_ctrl, 0, wx.LEFT | wx.BOTTOM, 10)

        buttons = self.dialog.CreateButtonSizer(wx.OK | wx.CANCEL)
        if buttons is not None:
            ok_btn = self.dialog.FindWindowById(wx.ID_OK)
            if ok_btn is not None:
                ok_btn.SetDefault()
            root.Add(buttons, 0, wx.EXPAND | wx.ALL, 8)

        self.dialog.SetSizer(root)
        self.dialog.Layout()

        from quill.ui.dialog_contract import apply_modal_ids

        apply_modal_ids(self.dialog, affirmative_id=wx.ID_OK, cancel_id=wx.ID_CANCEL)

        if abbreviation is not None:
            self._abbr_ctrl.SetValue(abbreviation.abbreviation)
            self._exp_ctrl.SetValue(abbreviation.expansion)
            self._desc_ctrl.SetValue(abbreviation.description)
            self._case_ctrl.SetValue(abbreviation.case_sensitive)
            self._enabled_ctrl.SetValue(abbreviation.enabled)

        self._abbr_ctrl.SetFocus()

    def show(self) -> int:
        return self.dialog.ShowModal()

    def close(self) -> None:
        self.dialog.Destroy()

    def get_values(self) -> tuple[str, str, str, bool, bool]:
        return (
            self._abbr_ctrl.GetValue().strip(),
            self._exp_ctrl.GetValue(),
            self._desc_ctrl.GetValue().strip(),
            self._case_ctrl.GetValue(),
            self._enabled_ctrl.GetValue(),
        )


class AbbreviationManagerDialog:
    """Browse, create, edit, and delete abbreviations."""

    def __init__(self, parent: object, library: AbbreviationLibrary) -> None:
        self._library = library
        self.dialog = wx.Dialog(
            parent,
            title="Manage Abbreviations",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetMinSize(wx.Size(600, 400))

        root = wx.BoxSizer(wx.VERTICAL)

        self._list = wx.ListCtrl(
            self.dialog,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN,
        )
        self._list.SetName("Abbreviations list")
        self._list.InsertColumn(0, "Abbreviation", width=120)
        self._list.InsertColumn(1, "Expansion", width=320)
        self._list.InsertColumn(2, "On", width=40)
        root.Add(self._list, 1, wx.EXPAND | wx.ALL, 8)

        btn_row = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_new = wx.Button(self.dialog, label="&New")
        self._btn_edit = wx.Button(self.dialog, label="&Edit")
        self._btn_delete = wx.Button(self.dialog, label="&Delete")
        self._btn_toggle = wx.Button(self.dialog, label="Enable/Disa&ble")
        btn_close = wx.Button(self.dialog, wx.ID_CANCEL, label="C&lose")
        for btn in (self._btn_new, self._btn_edit, self._btn_delete, self._btn_toggle):
            btn_row.Add(btn, 0, wx.RIGHT, 4)
        btn_row.AddStretchSpacer(1)
        btn_row.Add(btn_close, 0)
        root.Add(btn_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.dialog.SetSizer(root)
        self.dialog.Layout()

        from quill.ui.dialog_contract import apply_modal_ids

        apply_modal_ids(self.dialog, cancel_id=wx.ID_CANCEL, cancel_label="Close")

        self._btn_new.Bind(wx.EVT_BUTTON, self._on_new)
        self._btn_edit.Bind(wx.EVT_BUTTON, self._on_edit)
        self._btn_delete.Bind(wx.EVT_BUTTON, self._on_delete)
        self._btn_toggle.Bind(wx.EVT_BUTTON, self._on_toggle)
        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_edit)

        self._rebuild_list()
        self._list.SetFocus()

    def show(self) -> int:
        return self.dialog.ShowModal()

    def close(self) -> None:
        self.dialog.Destroy()

    # -- list helpers --

    def _rebuild_list(self) -> None:
        sel = self._list.GetFirstSelected()
        self._list.DeleteAllItems()
        for i, abbr in enumerate(self._library.abbreviations):
            self._list.InsertItem(i, abbr.abbreviation)
            preview = abbr.expansion.replace("\n", " ")[:60]
            self._list.SetItem(i, 1, preview)
            self._list.SetItem(i, 2, "Y" if abbr.enabled else "N")
        if 0 <= sel < self._list.GetItemCount():
            self._list.Select(sel)
            self._list.EnsureVisible(sel)
        elif self._list.GetItemCount() > 0:
            self._list.Select(0)

    def _selected_index(self) -> int:
        return self._list.GetFirstSelected()

    # -- event handlers --

    def _on_new(self, _event: object) -> None:
        import uuid

        edit_dlg = _AbbreviationEditDialog(self.dialog)
        result = edit_dlg.show()
        if result == wx.ID_OK:
            abbr_text, exp_text, desc_text, case_s, enabled = edit_dlg.get_values()
            if abbr_text and exp_text:
                new_abbr = Abbreviation(
                    id=str(uuid.uuid4()),
                    abbreviation=abbr_text,
                    expansion=exp_text,
                    description=desc_text,
                    case_sensitive=case_s,
                    enabled=enabled,
                )
                self._library.abbreviations.append(new_abbr)
                self._library.abbreviations.sort(key=lambda a: a.abbreviation.lower())
                save_abbreviation_library(self._library)
                self._rebuild_list()
        edit_dlg.close()

    def _on_edit(self, _event: object) -> None:
        idx = self._selected_index()
        if idx < 0:
            return
        abbr = self._library.abbreviations[idx]
        edit_dlg = _AbbreviationEditDialog(self.dialog, abbr)
        result = edit_dlg.show()
        if result == wx.ID_OK:
            abbr_text, exp_text, desc_text, case_s, enabled = edit_dlg.get_values()
            if abbr_text and exp_text:
                abbr.abbreviation = abbr_text
                abbr.expansion = exp_text
                abbr.description = desc_text
                abbr.case_sensitive = case_s
                abbr.enabled = enabled
                save_abbreviation_library(self._library)
                self._rebuild_list()
        edit_dlg.close()

    def _on_delete(self, _event: object) -> None:
        idx = self._selected_index()
        if idx < 0:
            return
        abbr = self._library.abbreviations[idx]
        confirm = wx.MessageDialog(
            self.dialog,
            f"Delete abbreviation '{abbr.abbreviation}'?",
            "Delete Abbreviation",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )
        result = confirm.ShowModal()
        confirm.Destroy()
        if result == wx.ID_YES:
            del self._library.abbreviations[idx]
            save_abbreviation_library(self._library)
            self._rebuild_list()

    def _on_toggle(self, _event: object) -> None:
        idx = self._selected_index()
        if idx < 0:
            return
        abbr = self._library.abbreviations[idx]
        abbr.enabled = not abbr.enabled
        save_abbreviation_library(self._library)
        self._rebuild_list()
