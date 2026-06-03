from quill.core.commands import Command
from quill.core.guides import (
    build_keyboard_reference,
    build_keyboard_shortcut_html,
    build_welcome_guide,
)


def test_build_welcome_guide_contains_core_sections() -> None:
    guide = build_welcome_guide()
    assert "# Welcome to Quill" in guide
    assert "## Quick start" in guide
    assert "Keyboard Reference" in guide


def test_build_keyboard_reference_groups_commands() -> None:
    commands = [
        Command("file.open", "Open File", "Ctrl+O", lambda: None, "core.file"),
        Command("edit.find", "Find", "Ctrl+F", lambda: None, "core.search"),
        Command("tools.word_count", "Word Count", None, lambda: None, "core.analysis"),
    ]
    reference = build_keyboard_reference(commands)
    assert "## Edit" in reference
    assert "## File" in reference
    assert "## Tools" in reference
    assert "`Ctrl+O`" in reference
    assert "`(unbound)`" in reference


def test_build_keyboard_shortcut_html_renders_accessible_table() -> None:
    commands = [
        Command("file.open", "Open File", "Ctrl+O", lambda: None, "core.file"),
        Command("edit.find", "Find", "Ctrl+F", lambda: None, "core.search"),
        Command("tools.word_count", "Word Count", None, lambda: None, "core.analysis"),
    ]
    html = build_keyboard_shortcut_html(commands)

    # Document scaffolding for a self-contained, accessible page.
    assert html.startswith("<!DOCTYPE html>")
    assert '<html lang="en">' in html
    assert "<title>QUILL Keyboard Shortcuts</title>" in html

    # Grouped per section with table captions and column headers.
    assert "<h2>Edit</h2>" in html
    assert "<h2>File</h2>" in html
    assert "<h2>Tools</h2>" in html
    assert "<caption>File commands</caption>" in html
    assert '<th scope="col">Keystroke</th>' in html
    assert '<th scope="col">Command</th>' in html
    assert '<th scope="col">Command ID</th>' in html

    # Bound and unbound commands are both represented.
    assert "<code>Ctrl+O</code>" in html
    assert "<em>Unassigned</em>" in html
    assert "<code>tools.word_count</code>" in html


def test_build_keyboard_shortcut_html_escapes_special_characters() -> None:
    commands = [
        Command("edit.tag", "Wrap <b> & </b>", "Ctrl+B", lambda: None, "core.edit"),
    ]
    html = build_keyboard_shortcut_html(commands)
    assert "Wrap &lt;b&gt; &amp; &lt;/b&gt;" in html
    assert "Wrap <b>" not in html
