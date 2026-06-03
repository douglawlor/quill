"""DLG-3 Phase 4 guard: web-surface governance for rich-render dialogs.

This is the machine-enforced anti-regression control for Phase 4 of the dialog
estate governance plan (PRD section 9.13). It locks in the two Phase 4
acceptance claims so they cannot silently regress:

1. **Rich-render / chat / dynamic-form dialogs route only through sanctioned
   web surfaces with native-fallback parity.** Raw HTML rendering primitives
   (``wx.html.HtmlWindow`` and its ``.SetPage(...)``) may appear *only* inside
   the sanctioned ``preview_dialog.py`` ImportError fallback. Every other rich
   surface goes through the ``wx_accessible_webview`` library adapters
   (``preview_dialog.py``, ``accessible_webview.py``) or the
   ``assistant_panel.py`` chat dialog, each of which carries a native fallback.

2. **No raw HTML is dumped into document tabs in onboarding / welcome paths.**
   The welcome guide content opened into an editor tab is Markdown, never an
   HTML document.

Catching a stray ``HtmlWindow`` or an HTML welcome-guide dump here keeps the
NVDA/JAWS/Narrator parity of the web estate intact long before a manual pass.
"""

from __future__ import annotations

from pathlib import Path

from quill.core.guides import build_welcome_guide

REPO_ROOT = Path(__file__).resolve().parents[3]
UI_DIR = REPO_ROOT / "quill" / "ui"

# The single module allowed to construct a raw wx.html.HtmlWindow: it is the
# accessible-WebView library's native fallback (used only when the
# wx_accessible_webview package is unavailable).
_SANCTIONED_RAW_HTML_MODULE = "preview_dialog.py"

# Tokens that indicate raw, non-library HTML rendering.
_RAW_HTML_TOKENS = (".SetPage(", "HtmlWindow(")


def _ui_modules() -> list[Path]:
    return sorted(UI_DIR.glob("*.py"))


def test_raw_html_rendering_is_confined_to_the_sanctioned_fallback() -> None:
    offenders: list[str] = []
    for path in _ui_modules():
        if path.name == _SANCTIONED_RAW_HTML_MODULE:
            continue
        source = path.read_text(encoding="utf-8")
        for token in _RAW_HTML_TOKENS:
            if token in source:
                offenders.append(f"{path.name}: uses raw HTML primitive {token!r}")

    assert not offenders, (
        "Raw HTML rendering escaped the sanctioned preview_dialog fallback. "
        "Route rich content through the accessible WebView adapters instead:\n"
        + "\n".join(offenders)
    )


def test_preview_dialog_carries_a_native_webview_fallback() -> None:
    source = (UI_DIR / "preview_dialog.py").read_text(encoding="utf-8")
    assert "_HAS_WEBVIEW_LIB" in source
    assert "except ImportError" in source
    # The fallback renders through wx.html (always present), not the library.
    assert "import wx.html" in source


def test_assistant_chat_dialog_carries_a_native_listbox_fallback() -> None:
    source = (UI_DIR / "assistant_panel.py").read_text(encoding="utf-8")
    # The chat surface prefers the accessible WebView, but degrades to a stock
    # list box + text field when no WebView backend is available.
    assert "_build_fallback_input" in source
    assert "wx.ListBox(" in source
    assert "self._webview = None" in source


def test_welcome_guide_opened_into_a_tab_is_markdown_not_html() -> None:
    guide = build_welcome_guide()
    stripped = guide.lstrip()
    assert not stripped.startswith("<"), "welcome guide tab content must not be HTML"
    lowered = guide.lower()
    for html_marker in ("<!doctype", "<html", "<body", "<div", "</p>"):
        assert html_marker not in lowered, (
            f"welcome guide tab content contains HTML marker {html_marker!r}; "
            "onboarding/welcome tabs must carry Markdown only"
        )
    # Positive signal that it really is Markdown.
    assert guide.startswith("# "), "welcome guide should be a Markdown document"
