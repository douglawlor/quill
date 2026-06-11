"""Copy Tray commands for MainFrame — 12-slot persistent clipboard.

Extracted into a mixin to keep ``main_frame.py`` within the GATE-11 size budget
(CQ-1). ``CopyTrayMixin`` is mixed into ``MainFrame`` and every method resolves
identically through the MRO; the ``self.editor``, ``self.frame``,
``self._announce``, ``self._set_status``, and ``self._show_modal_dialog`` helpers
it relies on stay on ``MainFrame``.

Multi-press behaviour (Phase 2):
  Single press  — paste immediately.
  Double press  — peek: announce slot content without pasting.
  Triple press  — open the Copy Tray dialog.
"""

from __future__ import annotations

import wx

from quill.core.copy_tray import CopyTray
from quill.core.multi_press import MultiPressDispatcher


class CopyTrayMixin:
    """Twelve-slot clipboard accessible by number key or dialog."""

    # -- lazy accessors --

    def _tray(self) -> CopyTray:
        if not hasattr(self, "_copy_tray_instance"):
            from quill.core import paths

            self._copy_tray_instance = CopyTray(paths.app_data_dir())
        return self._copy_tray_instance

    def _tray_dispatcher(self) -> MultiPressDispatcher:
        if not hasattr(self, "_copy_tray_dispatcher"):
            self._copy_tray_dispatcher = MultiPressDispatcher(window_ms=400)
            self._copy_tray_timers: dict[int, object] = {}
        return self._copy_tray_dispatcher

    # -- slot operations --

    def copy_to_tray_slot(self, n: int) -> None:
        start, end = self.editor.GetSelection()
        if start == end:
            self._announce(f"Select text first to copy to slot {n}")
            return
        text = self.editor.GetValue()[start:end]
        self._tray().copy_to(n, text)
        slot = self._tray().slot(n)
        label = f" ({slot.label})" if slot.label else ""
        self._set_status(f"Copied to slot {n}{label}: {slot.preview(50)}")
        self._announce(f"Copied to slot {n}{label}")

    def paste_from_tray_slot(self, n: int) -> None:
        """Route through MultiPressDispatcher: 1=paste, 2=peek, 3=dialog."""
        dispatcher = self._tray_dispatcher()
        count, needs_timer = dispatcher.press(f"tray_{n}")
        existing = self._copy_tray_timers.get(n)
        if existing is not None:
            stop = getattr(existing, "Stop", None)
            if callable(stop):
                stop()
        if needs_timer:
            timer = wx.CallLater(
                dispatcher.window_ms,
                self._fire_tray_action,
                n,
            )
            self._copy_tray_timers[n] = timer
        else:
            self._copy_tray_timers.pop(n, None)
            self._fire_tray_action_with_count(n, count)

    def _fire_tray_action(self, n: int) -> None:
        count = self._tray_dispatcher().timeout(f"tray_{n}")
        self._copy_tray_timers.pop(n, None)
        self._fire_tray_action_with_count(n, count)

    def _fire_tray_action_with_count(self, n: int, count: int) -> None:
        if count == 2:
            self._peek_tray_slot(n)
        elif count >= 3:
            self.open_copy_tray()
        else:
            self._do_paste_from_tray_slot(n)

    def _do_paste_from_tray_slot(self, n: int) -> None:
        text = self._tray().paste_from(n)
        if not text:
            self._announce(f"Slot {n} is empty")
            return
        start, end = self.editor.GetSelection()
        current = self.editor.GetValue()
        if start != end:
            updated = current[:start] + text + current[end:]
            new_pos = start + len(text)
        else:
            pos = self.editor.GetInsertionPoint()
            updated = current[:pos] + text + current[pos:]
            new_pos = pos + len(text)
        self._replace_document_text(updated)
        self.document.set_text(updated)
        self.editor.SetInsertionPoint(new_pos)
        self.editor.SetSelection(new_pos, new_pos)
        slot = self._tray().slot(n)
        label = f" ({slot.label})" if slot.label else ""
        self._set_status(f"Pasted from slot {n}{label}")
        self._announce(f"Pasted from slot {n}{label}")

    def _peek_tray_slot(self, n: int) -> None:
        slot = self._tray().slot(n)
        if slot.is_empty():
            self._announce(f"Slot {n} is empty")
            return
        label_part = f" ({slot.label})" if slot.label else ""
        preview = slot.preview(80)
        self._announce(f"Slot {n}{label_part}: {preview}")
        self._set_status(f"Slot {n}{label_part}: {preview}")

    # -- management commands --

    def open_copy_tray(self) -> None:
        from quill.ui.copy_tray_dialog import CopyTrayDialog

        tray = self._tray()
        dlg = CopyTrayDialog(self.frame, tray, self._get_editor_selection())
        result = self._show_modal_dialog(dlg.dialog, "Copy Tray")
        if result == wx.ID_OK and (text := dlg.selected_text_to_paste()):
            n = dlg.selected_slot()
            # Insert directly — the tray data is already up to date
            start, end = self.editor.GetSelection()
            current = self.editor.GetValue()
            if start != end:
                updated = current[:start] + text + current[end:]
                new_pos = start + len(text)
            else:
                pos = self.editor.GetInsertionPoint()
                updated = current[:pos] + text + current[pos:]
                new_pos = pos + len(text)
            self._replace_document_text(updated)
            self.document.set_text(updated)
            self.editor.SetInsertionPoint(new_pos)
            self.editor.SetSelection(new_pos, new_pos)
            slot = tray.slot(n)
            label = f" ({slot.label})" if slot.label else ""
            self._set_status(f"Pasted from slot {n}{label}")
            self._announce(f"Pasted from slot {n}{label}")
        dlg.close()

    def _get_editor_selection(self) -> str:
        start, end = self.editor.GetSelection()
        if start == end:
            return ""
        return self.editor.GetValue()[start:end]

    def clear_all_tray_slots(self) -> None:
        dlg = wx.MessageDialog(
            self.frame,
            "Clear all 9 copy tray slots? This cannot be undone.",
            "Clear Copy Tray",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
        )
        result = self._show_modal_dialog(dlg, "Clear Copy Tray")
        dlg.Destroy()
        if result == wx.ID_YES:
            self._tray().clear_all()
            self._announce("All copy tray slots cleared")
            self._set_status("Copy tray cleared")
