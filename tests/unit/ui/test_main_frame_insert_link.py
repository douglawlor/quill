from __future__ import annotations

from pathlib import Path

import quill.ui.web_form as web_form
from quill.core.document import Document
from quill.ui.main_frame import MainFrame


class _Editor:
    def __init__(self, selection: str = "") -> None:
        self._selection = selection

    def GetStringSelection(self) -> str:
        return self._selection


def _build_frame(*, path: Path | None, selection: str = "") -> MainFrame:
    frame = MainFrame.__new__(MainFrame)
    frame.document = Document(path=path, text="")
    frame.editor = _Editor(selection)
    frame._status_message = "Ready"
    frame._wx = object()
    frame.frame = object()
    frame._set_status = lambda message: setattr(frame, "_status_message", message)
    return frame


def test_insert_link_uses_web_form_and_inserts_markdown(monkeypatch) -> None:
    frame = _build_frame(path=Path("note.md"), selection="Quill")
    captured: dict[str, object] = {}

    def fake_show_web_form(parent, wx, **kwargs):  # noqa: ANN001, ANN003
        captured["kwargs"] = kwargs
        return {"display_text": "Quill", "url": "https://example.com"}

    monkeypatch.setattr(web_form, "show_web_form", fake_show_web_form)

    inserted: list[str] = []
    frame._apply_insertion_result = lambda result: inserted.append(result.inserted_text)

    frame.insert_link()

    assert inserted == ["[Quill](https://example.com)"]
    assert frame._status_message == "Inserted link (markdown)"
    fields = {field["name"] for field in captured["kwargs"]["fields"]}
    assert fields == {"display_text", "url"}
    assert captured["kwargs"]["save_label"] == "Insert"


def test_insert_link_cancel_returns_and_announces(monkeypatch) -> None:
    frame = _build_frame(path=Path("note.md"))

    monkeypatch.setattr(web_form, "show_web_form", lambda *a, **k: None)

    called: list[object] = []
    frame._apply_insertion_result = lambda result: called.append(result)

    frame.insert_link()

    assert called == []
    assert frame._status_message == "Insert link cancelled"


def test_insert_link_blank_url_is_cancelled(monkeypatch) -> None:
    frame = _build_frame(path=Path("note.md"), selection="text")

    monkeypatch.setattr(
        web_form,
        "show_web_form",
        lambda *a, **k: {"display_text": "text", "url": "   "},
    )

    called: list[object] = []
    frame._apply_insertion_result = lambda result: called.append(result)

    frame.insert_link()

    assert called == []
    assert frame._status_message == "Insert link cancelled"
