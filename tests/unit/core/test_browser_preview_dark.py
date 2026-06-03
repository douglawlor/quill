from quill.core.browser_preview import render_preview_body


def test_render_preview_body_light_has_no_dark_style() -> None:
    body = render_preview_body("# Title\n\nHello", "markdown")
    assert "background:#1e1e1e" not in body
    assert "<h1" in body


def test_render_preview_body_dark_injects_dark_stylesheet() -> None:
    # Issue #83: in dark mode the preview WebView must render dark too, so the
    # split view is not half dark, half bright.
    body = render_preview_body("# Title\n\nHello", "markdown", dark=True)
    assert "background:#1e1e1e" in body
    assert "color:#e6e6e6" in body
    # The rendered content still follows the injected style.
    assert "<h1" in body


def test_render_preview_body_dark_applies_to_html_and_plain() -> None:
    html_body = render_preview_body("<h1>Hi</h1>", "html", dark=True)
    assert "background:#1e1e1e" in html_body
    plain_body = render_preview_body("just text", "plain", dark=True)
    assert "background:#1e1e1e" in plain_body
    assert "<pre>" in plain_body
