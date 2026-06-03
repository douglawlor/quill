from __future__ import annotations

from quill.core.punctuation_speech import (
    DEFAULT_PUNCTUATION_LEVEL,
    PUNCTUATION_LEVELS,
    normalize_punctuation_level,
    verbalize_punctuation,
)


def test_none_level_leaves_text_unchanged() -> None:
    text = "Cost: $5 (cheap) -- really?"
    assert verbalize_punctuation(text, "none") == text


def test_some_level_speaks_technical_symbols_only() -> None:
    result = verbalize_punctuation("Email me @ home & wait.", "some")
    assert "at" in result.split()
    assert "and" in result.split()
    # Sentence punctuation is untouched at "some".
    assert result.endswith("wait.")


def test_some_level_does_not_speak_sentence_punctuation() -> None:
    assert verbalize_punctuation("Hello, world.", "some") == "Hello, world."


def test_most_level_speaks_brackets_and_dashes() -> None:
    result = verbalize_punctuation("a (b) - c", "most")
    words = result.split()
    assert "left" in words and "paren" in words
    assert "right" in words
    assert "dash" in words


def test_most_level_leaves_sentence_punctuation_alone() -> None:
    assert verbalize_punctuation("Done.", "most") == "Done."


def test_all_level_speaks_sentence_punctuation() -> None:
    result = verbalize_punctuation("Hello, world.", "all")
    words = result.split()
    assert "comma" in words
    assert "dot" in words


def test_apostrophe_never_split() -> None:
    for level in PUNCTUATION_LEVELS:
        assert "don't" in verbalize_punctuation("don't stop", level)


def test_em_and_en_dash_named() -> None:
    assert "em dash" in verbalize_punctuation("a\u2014b", "most")
    assert "en dash" in verbalize_punctuation("a\u2013b", "most")


def test_normalize_unknown_defaults_to_some() -> None:
    assert normalize_punctuation_level("bogus") == DEFAULT_PUNCTUATION_LEVEL
    assert normalize_punctuation_level("  ALL ") == "all"


def test_levels_are_cumulative() -> None:
    sample = "@ ( ."
    some = verbalize_punctuation(sample, "some")
    most = verbalize_punctuation(sample, "most")
    full = verbalize_punctuation(sample, "all")
    # "@" is spoken at every active level.
    assert "at" in some.split()
    assert "at" in most.split()
    assert "at" in full.split()
    # "(" only from "most" upward.
    assert "paren" not in some
    assert "paren" in most
    # "." only at "all".
    assert "dot" not in most.split()
    assert "dot" in full.split()
