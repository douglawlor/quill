"""Machine guard for a recurring dialog bug class (#84 / #119 / status bar).

When a dialog parents its content controls to an inner ``wx.Panel(dialog)`` but
then adds ``dialog.CreateButtonSizer(...)``'s OK/Cancel buttons (which are
children of the *dialog*, not the panel) into that panel's sizer, the buttons
are mislaid: they stay unrealized, so clicks and ``SetEscapeId`` dismissal both
fail and the dialog traps the user.

This test scans every dialog-building function across ``quill/ui`` and fails if
that exact parent/sizer mismatch reappears. Correct dialogs either parent all
controls directly to the dialog, or keep the inner panel but add the button
sizer to the dialog-owned outer sizer.
"""

from __future__ import annotations

import ast
from pathlib import Path

UI_DIR = Path(__file__).resolve().parents[3] / "quill" / "ui"
_DIALOG_NAMES = {"dialog", "self.dialog", "dlg", "self.dlg"}


def _panel_vars_parented_to_dialog(fn: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign):
            continue
        val = node.value
        if (
            isinstance(val, ast.Call)
            and isinstance(val.func, ast.Attribute)
            and val.func.attr == "Panel"
            and val.args
            and ast.unparse(val.args[0]) in _DIALOG_NAMES
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _button_sizer_vars(fn: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Assign):
            continue
        val = node.value
        if (
            isinstance(val, ast.Call)
            and isinstance(val.func, ast.Attribute)
            and val.func.attr == "CreateButtonSizer"
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _find_mismatched_dialogs() -> list[str]:
    flagged: list[str] = []
    for path in sorted(UI_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            panels = _panel_vars_parented_to_dialog(fn)
            buttons = _button_sizer_vars(fn)
            if not panels or not buttons:
                continue
            # Which sizer variables received the button sizer via .Add(buttons)?
            sizers_with_buttons: set[str] = set()
            for node in ast.walk(fn):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "Add"
                    and node.args
                    and isinstance(node.func.value, ast.Name)
                    and ast.unparse(node.args[0]) in buttons
                ):
                    sizers_with_buttons.add(node.func.value.id)
            # Is any such sizer then assigned to a panel via SetSizer*?
            for node in ast.walk(fn):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in {"SetSizer", "SetSizerAndFit"}
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id in panels
                    and node.args
                    and ast.unparse(node.args[0]) in sizers_with_buttons
                ):
                    flagged.append(f"{path.name}::{fn.name} (line {fn.lineno})")
    return flagged


def test_no_dialog_buttons_in_inner_panel_sizer() -> None:
    flagged = _find_mismatched_dialogs()
    assert not flagged, (
        "CreateButtonSizer buttons (dialog children) placed in an inner "
        "wx.Panel(dialog) sizer — they will not realize and the dialog cannot "
        "be dismissed. Add the button sizer to the dialog's own outer sizer "
        "instead. Offending dialogs:\n  " + "\n  ".join(flagged)
    )
