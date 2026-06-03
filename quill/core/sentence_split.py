"""Sentence segmentation for Read Aloud.

Read Aloud speaks one sentence at a time so it can report progress, pause
between sentences, and stop responsively. The span model and the splitter live
here, separate from the engine plumbing in :mod:`quill.core.read_aloud`, so the
pure text logic can be unit-tested without any audio backend.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_SENTENCE_PATTERN = re.compile(r".+?(?:[.!?]+(?:\s+|$)|\n+|$)", re.DOTALL)


@dataclass(frozen=True, slots=True)
class SentenceSpan:
    start: int
    end: int


def sentence_spans(text: str) -> list[SentenceSpan]:
    spans: list[SentenceSpan] = []
    for match in _SENTENCE_PATTERN.finditer(text):
        start, end = match.span()
        if text[start:end].strip():
            spans.append(SentenceSpan(start=start, end=end))
    if not spans and text.strip():
        spans.append(SentenceSpan(0, len(text)))
    return spans
