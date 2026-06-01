from __future__ import annotations

import pytest

from quill.core.announcements import format_announcement, format_progress, pluralize


@pytest.mark.parametrize(
    "count,unit,expected",
    [
        (1, "word", "1 word"),
        (0, "word", "0 words"),
        (42, "word", "42 words"),
        (1200, "word", "1,200 words"),
        (2, "match", "2 matches"),
        (3, "character", "3 characters"),
    ],
)
def test_pluralize(count: int, unit: str, expected: str) -> None:
    assert pluralize(count, unit) == expected


def test_outcome_with_object_and_count_matches_grammar() -> None:
    assert format_announcement("Rewrote", "paragraph", count=42) == "Rewrote paragraph, 42 words."


def test_outcome_with_thousands_separator() -> None:
    assert (
        format_announcement("Summarized", "document", count=1200)
        == "Summarized document, 1,200 words."
    )


def test_outcome_verb_and_object_only() -> None:
    assert format_announcement("Saved", "document") == "Saved document."


def test_outcome_verb_only_is_capitalized_and_terminated() -> None:
    assert format_announcement("copied") == "Copied."


def test_outcome_singular_unit() -> None:
    assert format_announcement("Replaced", "selection", count=1) == "Replaced selection, 1 word."


def test_outcome_with_detail_segment() -> None:
    assert (
        format_announcement("Rewrote", "paragraph", count=5, detail="grammar fixed")
        == "Rewrote paragraph, 5 words, grammar fixed."
    )


def test_existing_terminal_punctuation_is_preserved() -> None:
    assert format_announcement("Nothing to rewrite!") == "Nothing to rewrite!"


def test_progress_matches_announcement_grammar() -> None:
    assert format_progress("Rewriting", "paragraph", count=42) == "Rewriting paragraph, 42 words."
