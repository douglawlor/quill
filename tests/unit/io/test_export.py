from __future__ import annotations

from pathlib import Path

import pytest

from quill.core.document import Document
from quill.io.export import (
    format_label_for_path,
    markdown_to_html,
    markdown_to_plain_text,
    write_document_as,
    write_html_document,
    write_plain_text_document,
)


# --------------------------------------------------------------------------- #
# markdown_to_plain_text
# --------------------------------------------------------------------------- #
def test_plain_strips_heading_and_emphasis() -> None:
    md = "# Title\n\nThis is **bold** and *italic* and `code`."
    assert markdown_to_plain_text(md) == "Title\n\nThis is bold and italic and code."


def test_plain_strips_links_keeping_text() -> None:
    assert markdown_to_plain_text("See [the site](https://example.com).") == "See the site."


def test_plain_unwraps_images_before_links() -> None:
    assert markdown_to_plain_text("![a cat](cat.png)") == "a cat"


def test_plain_preserves_inline_code_contents() -> None:
    # Markup inside a code span must survive untouched.
    assert markdown_to_plain_text("Use `**not bold**` here.") == "Use **not bold** here."


def test_plain_leaves_snake_case_untouched() -> None:
    assert markdown_to_plain_text("call foo_bar_baz and snake_case now") == (
        "call foo_bar_baz and snake_case now"
    )


def test_plain_strips_underscore_emphasis() -> None:
    assert markdown_to_plain_text("_italic_ and __bold__ words") == "italic and bold words"


def test_plain_normalizes_bullets_and_keeps_numbers() -> None:
    md = "* one\n+ two\n- three\n\n1. first\n2. second"
    assert markdown_to_plain_text(md) == "- one\n- two\n- three\n\n1. first\n2. second"


def test_plain_drops_blockquote_marker() -> None:
    assert markdown_to_plain_text("> quoted line") == "quoted line"


def test_plain_horizontal_rule_becomes_blank() -> None:
    assert markdown_to_plain_text("a\n\n---\n\nb") == "a\n\nb"


def test_plain_fenced_code_is_verbatim() -> None:
    md = "```\n# not a heading\n**kept**\n```"
    assert markdown_to_plain_text(md) == "# not a heading\n**kept**"


def test_plain_collapses_excess_blank_lines() -> None:
    assert markdown_to_plain_text("a\n\n\n\nb") == "a\n\nb"


# --------------------------------------------------------------------------- #
# markdown_to_html
# --------------------------------------------------------------------------- #
def test_html_is_standalone_without_refresh_meta() -> None:
    out = markdown_to_html("# Hi\n\nText", "My Doc")
    assert out.startswith("<!doctype html>")
    assert "<title>My Doc</title>" in out
    assert 'charset="utf-8"' in out
    assert "http-equiv" not in out  # no live-preview auto refresh in a saved file
    assert "<h1" in out and "Hi" in out


def test_html_escapes_title() -> None:
    assert "<title>A &amp; B</title>" in markdown_to_html("x", "A & B")


# --------------------------------------------------------------------------- #
# writers + dispatcher
# --------------------------------------------------------------------------- #
def _doc(text: str) -> Document:
    return Document(text=text, path=None, modified=True, encoding="utf-8", line_ending="\n")


def test_write_plain_text_strips_and_marks_saved(tmp_path: Path) -> None:
    doc = _doc("# H\n\n**b**")
    target = tmp_path / "out.txt"
    result = write_plain_text_document(doc, target)
    assert result == target
    assert target.read_text(encoding="utf-8") == "H\n\nb"
    assert doc.path == target and doc.modified is False


def test_write_html_document_writes_html(tmp_path: Path) -> None:
    doc = _doc("# H")
    target = tmp_path / "out.html"
    write_html_document(doc, target)
    body = target.read_text(encoding="utf-8")
    assert body.startswith("<!doctype html>")
    assert doc.modified is False


@pytest.mark.parametrize(
    "name,expected_marker",
    [
        ("a.rtf", "{\\rtf"),
        ("a.html", "<!doctype html>"),
        ("a.htm", "<!doctype html>"),
        ("a.xhtml", "<!doctype html>"),
        ("a.txt", "Bold"),
        ("a.text", "Bold"),
        ("a.md", "**Bold**"),
        ("a.markdown", "**Bold**"),
        ("a.weird", "**Bold**"),
    ],
)
def test_dispatch_by_extension(tmp_path: Path, name: str, expected_marker: str) -> None:
    doc = _doc("**Bold**")
    target = tmp_path / name
    write_document_as(doc, target)
    assert expected_marker in target.read_text(encoding="utf-8", errors="replace")


def test_dispatch_txt_strips_markup(tmp_path: Path) -> None:
    doc = _doc("**Bold**")
    target = tmp_path / "a.txt"
    write_document_as(doc, target)
    assert target.read_text(encoding="utf-8") == "Bold"


def test_dispatch_md_is_verbatim(tmp_path: Path) -> None:
    doc = _doc("# Title\n\n**Bold**")
    target = tmp_path / "a.md"
    write_document_as(doc, target)
    assert target.read_text(encoding="utf-8") == "# Title\n\n**Bold**"


def test_line_ending_preserved_on_export(tmp_path: Path) -> None:
    doc = Document(text="a\n\nb", path=None, modified=True, encoding="utf-8", line_ending="\r\n")
    target = tmp_path / "a.txt"
    write_plain_text_document(doc, target)
    assert target.read_bytes() == b"a\r\n\r\nb"


def test_write_requires_path() -> None:
    with pytest.raises(ValueError):
        write_document_as(_doc("x"), None)


def test_format_label_for_path() -> None:
    assert format_label_for_path(Path("a.rtf")) == "rich text"
    assert format_label_for_path(Path("a.html")) == "HTML"
    assert format_label_for_path(Path("a.txt")) == "plain text"
    assert format_label_for_path(Path("a.md")) == "Markdown"
    assert format_label_for_path(Path("a.unknown")) == "Markdown"


def test_export_module_is_wx_free() -> None:
    import quill.io.export as export_module

    source = Path(export_module.__file__).read_text(encoding="utf-8")
    assert "import wx" not in source
