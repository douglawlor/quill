"""Unit tests for quill.core.abbreviations."""

from __future__ import annotations

from quill.core.abbreviations import (
    _TRIGGER_CHARS,
    Abbreviation,
    AbbreviationLibrary,
    AbbreviationMatch,
    load_abbreviation_library,
    resolve_expansion,
    save_abbreviation_library,
    try_expand,
)


def _lib(*pairs: tuple[str, str]) -> AbbreviationLibrary:
    return AbbreviationLibrary(
        version=1,
        abbreviations=[
            Abbreviation(id=str(i), abbreviation=a, expansion=e) for i, (a, e) in enumerate(pairs)
        ],
    )


class TestResolveExpansion:
    def test_plain_text(self) -> None:
        text, offset, has_cursor = resolve_expansion("by the way")
        assert text == "by the way"
        assert offset == len("by the way")
        assert has_cursor is False

    def test_cursor_marker(self) -> None:
        text, offset, has_cursor = resolve_expansion("Hello ${cursor} world")
        assert text == "Hello  world"
        assert offset == 6
        assert has_cursor is True

    def test_cursor_at_start(self) -> None:
        text, offset, has_cursor = resolve_expansion("${cursor}end")
        assert text == "end"
        assert offset == 0
        assert has_cursor is True

    def test_date_substituted(self) -> None:
        import datetime

        text, _, _ = resolve_expansion("Today is ${date}.")
        assert datetime.date.today().strftime("%Y") in text

    def test_time_substituted(self) -> None:
        text, _, _ = resolve_expansion("Time: ${time}")
        assert ":" in text

    def test_clipboard_substituted(self) -> None:
        text, _, _ = resolve_expansion("See: ${clipboard}", clipboard_text="ref123")
        assert text == "See: ref123"

    def test_clipboard_empty_leaves_placeholder(self) -> None:
        text, _, _ = resolve_expansion("See: ${clipboard}")
        assert "${clipboard}" in text


class TestTryExpand:
    def test_no_match_returns_none(self) -> None:
        lib = _lib(("btw", "by the way"))
        assert try_expand("hello world ", 12, lib) is None

    def test_simple_match_on_space(self) -> None:
        lib = _lib(("btw", "by the way"))
        text = "Type btw "
        result = try_expand(text, len(text), lib)
        assert result is not None
        assert isinstance(result, AbbreviationMatch)
        assert result.resolved_text == "by the way"
        assert result.token_start == 5

    def test_trigger_char_in_result(self) -> None:
        lib = _lib(("eg", "for example"))
        text = "eg."
        result = try_expand(text, 3, lib)
        assert result is not None
        assert result.token_end == 2  # position of "."

    def test_case_insensitive_by_default(self) -> None:
        lib = _lib(("btw", "by the way"))
        text = "BTW "
        result = try_expand(text, 4, lib)
        assert result is not None

    def test_case_sensitive_no_match_on_different_case(self) -> None:
        lib = AbbreviationLibrary(
            version=1,
            abbreviations=[
                Abbreviation(
                    id="1", abbreviation="btw", expansion="by the way", case_sensitive=True
                )
            ],
        )
        text = "BTW "
        result = try_expand(text, 4, lib)
        assert result is None

    def test_case_sensitive_matches_exact_case(self) -> None:
        lib = AbbreviationLibrary(
            version=1,
            abbreviations=[
                Abbreviation(
                    id="1", abbreviation="btw", expansion="by the way", case_sensitive=True
                )
            ],
        )
        text = "btw "
        result = try_expand(text, 4, lib)
        assert result is not None

    def test_disabled_abbreviation_not_matched(self) -> None:
        lib = AbbreviationLibrary(
            version=1,
            abbreviations=[
                Abbreviation(id="1", abbreviation="btw", expansion="by the way", enabled=False)
            ],
        )
        text = "btw "
        result = try_expand(text, 4, lib)
        assert result is None

    def test_caret_too_small_returns_none(self) -> None:
        lib = _lib(("btw", "by the way"))
        assert try_expand("btw ", 1, lib) is None

    def test_non_trigger_char_returns_none(self) -> None:
        lib = _lib(("btw", "by the way"))
        text = "btwX"
        assert try_expand(text, 4, lib) is None

    def test_empty_token_returns_none(self) -> None:
        lib = _lib(("btw", "by the way"))
        assert try_expand("  ", 2, lib) is None

    def test_longest_match_first(self) -> None:
        lib = AbbreviationLibrary(
            version=1,
            abbreviations=[
                Abbreviation(id="1", abbreviation="imo", expansion="in my opinion"),
                Abbreviation(id="2", abbreviation="imho", expansion="in my humble opinion"),
            ],
        )
        text = "imho "
        result = try_expand(text, 5, lib)
        assert result is not None
        assert result.resolved_text == "in my humble opinion"

    def test_all_trigger_chars_fire(self) -> None:
        lib = _lib(("a", "alpha"))
        for ch in _TRIGGER_CHARS:
            text = f"a{ch}"
            result = try_expand(text, 2, lib)
            assert result is not None, f"trigger char {ch!r} did not fire"


class TestPersistence:
    def test_roundtrip(self, tmp_path: object) -> None:
        lib = _lib(("btw", "by the way"), ("imo", "in my opinion"))
        save_abbreviation_library(lib, tmp_path)
        loaded = load_abbreviation_library(tmp_path)
        assert len(loaded.abbreviations) == 2
        assert loaded.abbreviations[0].abbreviation == "btw"

    def test_load_missing_file_returns_defaults(self, tmp_path: object) -> None:
        loaded = load_abbreviation_library(tmp_path)
        assert len(loaded.abbreviations) > 0

    def test_load_corrupt_file_returns_defaults(self, tmp_path: object) -> None:
        (tmp_path / "abbreviations.json").write_text("not json{{{")
        loaded = load_abbreviation_library(tmp_path)
        assert len(loaded.abbreviations) > 0
