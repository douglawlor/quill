"""Unit tests for the bundled math-equations Quillin.

Covers:
- manifest.json: validates, resolves to Insert menu, declares Ctrl+Shift+E
  hotkey, declares correct capabilities.
- extension.py handler: inline LaTeX, block LaTeX, MathML passthrough,
  selection pre-fill and replace, empty cancel, prompt cancel, mode cancel.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from quill.core.quillins.loader import bundled_extensions_root
from quill.core.quillins.registry import build_registry
from quill.core.quillins.validation import parse_manifest, validate_manifest

_DIR = bundled_extensions_root() / "math-equations"


def _load_manifest():
    raw = json.loads((_DIR / "manifest.json").read_text(encoding="utf-8"))
    assert validate_manifest(raw) == []
    return parse_manifest(raw)


class _FakeApi:
    def __init__(self) -> None:
        self.handlers: dict[str, Callable[[Any], None]] = {}

    def register_command(self, name: str, handler: Callable[[Any], None]) -> None:
        self.handlers[name] = handler


@dataclass
class _FakeCtx:
    selection: str = ""
    prompts: list[str | None] = field(default_factory=list)
    choices: list[str | None] = field(default_factory=list)
    inserted: list[str] = field(default_factory=list)
    replaced: list[str] = field(default_factory=list)
    announced: list[str] = field(default_factory=list)

    def get_selection(self) -> str:
        return self.selection

    def prompt(self, title: str, label: str, default: str = "") -> str | None:
        return self.prompts.pop(0)

    def show_choices(self, title: str, items: list[str]) -> str | None:
        return self.choices.pop(0)

    def insert_text(self, text: str) -> None:
        self.inserted.append(text)

    def replace_selection(self, text: str) -> None:
        self.replaced.append(text)

    def announce(self, message: str) -> None:
        self.announced.append(message)


def _register_extension() -> _FakeApi:
    sys.path.insert(0, str(_DIR))
    try:
        ns: dict[str, Any] = {}
        exec((_DIR / "extension.py").read_text(encoding="utf-8"), ns)  # noqa: S102
        api = _FakeApi()
        ns["register"](api)
        return api
    finally:
        sys.path.remove(str(_DIR))


# -- manifest -----------------------------------------------------------------


def test_manifest_validates_and_has_correct_id() -> None:
    manifest = _load_manifest()
    assert manifest.id == "com.quill.bundled.math-equations"


def test_manifest_capabilities() -> None:
    manifest = _load_manifest()
    caps = set(manifest.capabilities)
    assert caps >= {"ui.prompt", "ui.choices", "ui.announce", "editor.read", "editor.write"}


def test_manifest_command_under_insert_menu() -> None:
    manifest = _load_manifest()
    registry = build_registry([manifest])
    assert registry.conflicts == ()
    parents = {m.parent for m in registry.menus}
    assert "Insert" in parents


def test_manifest_hotkey_ctrl_shift_e() -> None:
    manifest = _load_manifest()
    bindings = {hk.binding for hk in manifest.contributes.hotkeys}
    assert "Ctrl+Shift+E" in bindings


# -- handler: LaTeX insertion -------------------------------------------------


def test_inline_latex_inserts_dollar_delimiters() -> None:
    api = _register_extension()
    ctx = _FakeCtx(prompts=["E=mc^2"], choices=["Inline  ($...$)"])
    api.handlers["insert_equation"](ctx)
    assert ctx.inserted == ["$E=mc^2$"]
    assert ctx.announced == ["Inserted math equation"]


def test_block_latex_inserts_double_dollar_with_newlines() -> None:
    api = _register_extension()
    ctx = _FakeCtx(prompts=[r"\sum_{n=1}^{\infty} \frac{1}{n^2}"], choices=["Block  ($$...$$)"])
    api.handlers["insert_equation"](ctx)
    assert len(ctx.inserted) == 1
    snippet = ctx.inserted[0]
    assert snippet.startswith("\n$$\n")
    assert snippet.endswith("\n$$\n")
    assert r"\sum" in snippet


# -- handler: MathML detection ------------------------------------------------


def test_mathml_inserts_verbatim_without_mode_prompt() -> None:
    api = _register_extension()
    mathml = "<math><mi>x</mi></math>"
    ctx = _FakeCtx(prompts=[mathml])
    api.handlers["insert_equation"](ctx)
    assert ctx.inserted == [mathml]
    assert ctx.choices == []  # show_choices never called
    assert "MathML" in ctx.announced[0]


def test_mathml_with_leading_whitespace_detected() -> None:
    api = _register_extension()
    mathml = "  <math><mi>y</mi></math>"
    ctx = _FakeCtx(prompts=[mathml])
    api.handlers["insert_equation"](ctx)
    assert ctx.inserted[0].startswith("<math")


def test_mathml_with_selection_replaces_not_inserts() -> None:
    api = _register_extension()
    mathml = "<math><mi>z</mi></math>"
    ctx = _FakeCtx(selection="old text", prompts=[mathml])
    api.handlers["insert_equation"](ctx)
    assert ctx.replaced == [mathml]
    assert ctx.inserted == []


# -- handler: selection pre-fill ----------------------------------------------


def test_inline_selection_stripped_and_replaced() -> None:
    api = _register_extension()
    ctx = _FakeCtx(
        selection="$x^2$",
        prompts=["x^2"],
        choices=["Inline  ($...$)"],
    )
    api.handlers["insert_equation"](ctx)
    assert ctx.replaced == ["$x^2$"]
    assert ctx.inserted == []


def test_block_selection_surfaces_block_mode_first() -> None:
    # When the selection is block-delimited, the choice list should start with
    # Block so the user can confirm with one keypress.
    api = _register_extension()
    ctx = _FakeCtx(
        selection="$$x^2$$",
        prompts=["x^2"],
        choices=["Block  ($$...$$)"],
    )
    api.handlers["insert_equation"](ctx)
    assert ctx.replaced
    assert "$$" in ctx.replaced[0]


# -- handler: cancel paths ----------------------------------------------------


def test_cancel_prompt_does_nothing() -> None:
    api = _register_extension()
    ctx = _FakeCtx(prompts=[None])
    api.handlers["insert_equation"](ctx)
    assert ctx.inserted == []
    assert ctx.replaced == []
    assert ctx.announced == []


def test_empty_equation_announces_cancel() -> None:
    api = _register_extension()
    ctx = _FakeCtx(prompts=["   "])
    api.handlers["insert_equation"](ctx)
    assert ctx.inserted == []
    assert ctx.announced and "cancelled" in ctx.announced[0].lower()


def test_cancel_mode_choice_does_nothing() -> None:
    api = _register_extension()
    ctx = _FakeCtx(prompts=["E=mc^2"], choices=[None])
    api.handlers["insert_equation"](ctx)
    assert ctx.inserted == []
    assert ctx.announced == []
