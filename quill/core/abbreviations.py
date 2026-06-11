"""Abbreviation expansion library — bare-word TextExpander-style shortcuts.

Abbreviations differ from snippets: no trigger prefix is required. The user
types "btw " and the editor silently replaces "btw" with "by the way". A
sound can be played on expansion if configured.
"""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass
from pathlib import Path

_TRIGGER_CHARS: frozenset[str] = frozenset({
    " ",
    "\n",
    "\t",
    ".",
    ",",
    ";",
    ":",
    "!",
    "?",
    ")",
    "]",
    "}",
    '"',
    "'",
})

_ABBREVIATIONS_FILE = "abbreviations.json"


@dataclass(slots=True)
class Abbreviation:
    id: str
    abbreviation: str
    expansion: str
    case_sensitive: bool = False
    enabled: bool = True
    description: str = ""


@dataclass(slots=True)
class AbbreviationLibrary:
    version: int
    abbreviations: list[Abbreviation]


@dataclass(slots=True)
class AbbreviationMatch:
    token_start: int
    token_end: int
    resolved_text: str
    cursor_offset: int
    has_cursor: bool


_BUILTINS: list[tuple[str, str, str]] = [
    ("btw", "by the way", "Common shorthand"),
    ("imo", "in my opinion", ""),
    ("afaik", "as far as I know", ""),
    ("asap", "as soon as possible", ""),
    ("fwiw", "for what it's worth", ""),
    ("tbd", "to be determined", ""),
    ("wrt", "with respect to", ""),
    ("aka", "also known as", ""),
    ("eg", "for example", ""),
    ("ie", "that is", ""),
    ("atm", "at the moment", ""),
    ("iirc", "if I recall correctly", ""),
    ("imho", "in my humble opinion", ""),
    ("tbh", "to be honest", ""),
    ("ngl", "not going to lie", ""),
]


def _make_default_library() -> AbbreviationLibrary:
    return AbbreviationLibrary(
        version=1,
        abbreviations=[
            Abbreviation(
                id=str(uuid.uuid4()),
                abbreviation=abbr,
                expansion=exp,
                description=desc,
            )
            for abbr, exp, desc in _BUILTINS
        ],
    )


def resolve_expansion(expansion: str, clipboard_text: str = "") -> tuple[str, int, bool]:
    """Resolve variables in an abbreviation expansion body.

    Returns (resolved_text, cursor_offset, has_cursor_marker).
    cursor_offset is relative to the start of resolved_text.
    """
    text = expansion
    if clipboard_text:
        text = text.replace("${clipboard}", clipboard_text)
    text = text.replace("${date}", datetime.date.today().strftime("%B %d, %Y"))
    text = text.replace("${time}", datetime.datetime.now().strftime("%I:%M %p"))
    has_cursor = "${cursor}" in text
    cursor_offset = len(text)
    if has_cursor:
        cursor_offset = text.index("${cursor}")
        text = text.replace("${cursor}", "")
    return text, cursor_offset, has_cursor


def try_expand(
    text: str,
    caret: int,
    library: AbbreviationLibrary,
    clipboard_text: str = "",
) -> AbbreviationMatch | None:
    """Check for an abbreviation ending just before the character at caret-1.

    caret-1 must be a trigger character (space, punctuation, etc.).
    Returns an AbbreviationMatch or None.
    """
    if caret < 2 or caret > len(text):
        return None
    trigger_char = text[caret - 1]
    if trigger_char not in _TRIGGER_CHARS:
        return None
    token_end = caret - 1
    token_start = token_end
    while token_start > 0 and not text[token_start - 1].isspace():
        token_start -= 1
    if token_start >= token_end:
        return None
    token = text[token_start:token_end]
    candidates = sorted(
        (a for a in library.abbreviations if a.enabled),
        key=lambda a: len(a.abbreviation),
        reverse=True,
    )
    for abbr in candidates:
        if abbr.case_sensitive:
            match = token == abbr.abbreviation
        else:
            match = token.lower() == abbr.abbreviation.lower()
        if match:
            resolved, cursor_offset, has_cursor = resolve_expansion(abbr.expansion, clipboard_text)
            return AbbreviationMatch(
                token_start=token_start,
                token_end=token_end,
                resolved_text=resolved,
                cursor_offset=cursor_offset,
                has_cursor=has_cursor,
            )
    return None


def load_abbreviation_library(data_dir: Path | None = None) -> AbbreviationLibrary:
    from quill.core import paths
    from quill.core.storage import read_json

    base = data_dir if data_dir is not None else paths.app_data_dir()
    path = base / _ABBREVIATIONS_FILE
    if not path.exists():
        return _make_default_library()
    try:
        data = read_json(path, default={})
    except Exception:  # noqa: BLE001
        return _make_default_library()
    if not isinstance(data, dict):
        return _make_default_library()
    abbreviations: list[Abbreviation] = []
    for raw in data.get("abbreviations", []):
        if not isinstance(raw, dict):
            continue
        try:
            abbreviations.append(
                Abbreviation(
                    id=str(raw.get("id", uuid.uuid4())),
                    abbreviation=str(raw.get("abbreviation", "")),
                    expansion=str(raw.get("expansion", "")),
                    case_sensitive=bool(raw.get("case_sensitive", False)),
                    enabled=bool(raw.get("enabled", True)),
                    description=str(raw.get("description", "")),
                )
            )
        except Exception:  # noqa: BLE001
            continue
    return AbbreviationLibrary(
        version=int(data.get("version", 1)),
        abbreviations=abbreviations,
    )


def save_abbreviation_library(library: AbbreviationLibrary, data_dir: Path | None = None) -> None:
    from quill.core import paths
    from quill.core.storage import write_json_atomic

    base = data_dir if data_dir is not None else paths.app_data_dir()
    path = base / _ABBREVIATIONS_FILE
    write_json_atomic(
        path,
        {
            "version": library.version,
            "abbreviations": [
                {
                    "id": a.id,
                    "abbreviation": a.abbreviation,
                    "expansion": a.expansion,
                    "case_sensitive": a.case_sensitive,
                    "enabled": a.enabled,
                    "description": a.description,
                }
                for a in library.abbreviations
            ],
        },
    )
