from __future__ import annotations

from pathlib import Path

from quill.ui.main_frame import MainFrame


def _frame() -> MainFrame:
    return MainFrame.__new__(MainFrame)


def test_typed_extension_is_honored_over_filter() -> None:
    frame = _frame()
    # User typed .txt but the HTML filter (index 2) was highlighted: keep .txt.
    assert frame._resolve_save_target(Path("notes.txt"), 2) == Path("notes.txt")


def test_missing_extension_uses_text_filter() -> None:
    frame = _frame()
    assert frame._resolve_save_target(Path("notes"), 0) == Path("notes.txt")


def test_missing_extension_uses_markdown_filter() -> None:
    frame = _frame()
    assert frame._resolve_save_target(Path("notes"), 1) == Path("notes.md")


def test_missing_extension_uses_html_filter() -> None:
    frame = _frame()
    assert frame._resolve_save_target(Path("notes"), 2) == Path("notes.html")


def test_missing_extension_uses_rtf_filter() -> None:
    frame = _frame()
    assert frame._resolve_save_target(Path("notes"), 3) == Path("notes.rtf")


def test_all_files_filter_defaults_to_markdown() -> None:
    frame = _frame()
    assert frame._resolve_save_target(Path("notes"), 4) == Path("notes.md")
    assert frame._resolve_save_target(Path("notes"), -1) == Path("notes.md")


def test_no_double_extension_created() -> None:
    frame = _frame()
    result = frame._resolve_save_target(Path("report.txt"), 2)
    assert result.suffix == ".txt"
    assert str(result).count(".") == 1
