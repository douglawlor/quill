from __future__ import annotations

import pytest

from quill.core.ai.assistant import _split_into_chunks


def test_short_text_is_one_chunk() -> None:
    assert _split_into_chunks("hello", 100) == ["hello"]


def test_chunks_respect_max_chars() -> None:
    text = "\n\n".join("word " * 200 for _ in range(10))  # large, multi-paragraph
    chunks = _split_into_chunks(text, 1000)
    assert len(chunks) > 1
    assert all(len(c) <= 1000 for c in chunks)


def test_oversized_single_paragraph_is_hard_split() -> None:
    chunks = _split_into_chunks("x" * 2500, 1000)
    assert all(len(c) <= 1000 for c in chunks)
    assert "".join(chunks) == "x" * 2500


@pytest.mark.parametrize("bad_max", [0, -1, -1000])
def test_non_positive_max_chars_raises(bad_max: int) -> None:
    # Regression for BUG-7: max_chars <= 0 must not loop forever or silently
    # drop content via range(step<=0); it raises a clear ValueError instead.
    with pytest.raises(ValueError, match="positive"):
        _split_into_chunks("x" * 50, bad_max)
