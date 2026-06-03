from __future__ import annotations

from quill.core.sentence_split import SentenceSpan, sentence_spans


def test_splits_on_terminal_punctuation() -> None:
    spans = sentence_spans("One. Two! Three?")
    assert [(s.start, s.end) for s in spans] == [(0, 5), (5, 10), (10, 16)]


def test_splits_on_newlines() -> None:
    spans = sentence_spans("a\nb\n")
    assert all(isinstance(s, SentenceSpan) for s in spans)
    assert [s.start for s in spans] == [0, 2]


def test_blank_text_yields_no_spans() -> None:
    assert sentence_spans("   \n  ") == []


def test_unterminated_text_is_one_span() -> None:
    spans = sentence_spans("no terminator here")
    assert len(spans) == 1
    assert (spans[0].start, spans[0].end) == (0, 18)
