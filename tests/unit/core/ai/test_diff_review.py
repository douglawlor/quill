"""Line-by-line diff review model for AI edits (AI-7)."""

from __future__ import annotations

from quill.core.ai.diff_review import DiffHunk, build_diff_review


def test_no_changes_has_no_hunks() -> None:
    review = build_diff_review("alpha\nbeta", "alpha\nbeta")
    assert not review.has_changes
    assert review.hunks == []
    assert review.summary() == "No changes to review."
    # Applying nothing round-trips the original exactly.
    assert review.accept_all() == "alpha\nbeta"
    assert review.reject_all() == "alpha\nbeta"


def test_pure_addition_is_added_hunk() -> None:
    review = build_diff_review("line one", "line one\nline two")
    assert len(review.hunks) == 1
    hunk = review.hunks[0]
    assert hunk.kind == "added"
    assert hunk.new_lines == ("line two",)
    assert "Added 1 line" in hunk.describe()


def test_pure_deletion_is_removed_hunk() -> None:
    review = build_diff_review("keep\ndrop", "keep")
    assert len(review.hunks) == 1
    hunk = review.hunks[0]
    assert hunk.kind == "removed"
    assert hunk.old_lines == ("drop",)
    assert "Removed 1 line" in hunk.describe()


def test_replacement_is_changed_hunk() -> None:
    review = build_diff_review("before", "after")
    assert len(review.hunks) == 1
    hunk = review.hunks[0]
    assert hunk.kind == "changed"
    assert hunk.old_lines == ("before",)
    assert hunk.new_lines == ("after",)
    assert "Changed" in hunk.describe()


def test_accept_all_yields_revised() -> None:
    review = build_diff_review("a\nb\nc", "a\nB\nc\nd")
    assert review.accept_all() == "a\nB\nc\nd"


def test_reject_all_yields_original() -> None:
    review = build_diff_review("a\nb\nc", "a\nB\nc\nd")
    assert review.reject_all() == "a\nb\nc"


def test_partial_apply_accepts_only_selected_hunks() -> None:
    # Two independent hunks: change "b"->"B" and append "d".
    review = build_diff_review("a\nb\nc", "a\nB\nc\nd")
    assert len(review.hunks) == 2
    # Accept only the first hunk (the change), reject the addition.
    first_only = review.apply({review.hunks[0].index})
    assert first_only == "a\nB\nc"
    # Accept only the second hunk (the addition), reject the change.
    second_only = review.apply({review.hunks[1].index})
    assert second_only == "a\nb\nc\nd"


def test_trailing_newline_round_trips() -> None:
    original = "a\nb\n"
    revised = "a\nb\n"
    review = build_diff_review(original, revised)
    assert review.accept_all() == original
    # A change preserving the trailing newline does not gain or lose one.
    review2 = build_diff_review("a\nb\n", "a\nB\n")
    assert review2.accept_all() == "a\nB\n"
    assert review2.reject_all() == "a\nb\n"


def test_detail_lines_label_removed_and_added() -> None:
    review = build_diff_review("old text", "new text")
    detail = review.hunks[0].detail_lines()
    assert detail[0] == review.hunks[0].describe()
    assert any(line.startswith("- removed: old text") for line in detail)
    assert any(line.startswith("+ added: new text") for line in detail)


def test_detail_lines_mark_blank_lines() -> None:
    hunk = DiffHunk(index=0, kind="changed", old_lines=("",), new_lines=("x",), old_line_no=1)
    detail = hunk.detail_lines()
    assert "- removed: (blank line)" in detail
    assert "+ added: x" in detail


def test_summary_counts_each_kind() -> None:
    review = build_diff_review("a\nb\nc\nd", "a\nB\nc")
    summary = review.summary()
    assert "hunk" in summary
    # There is at least one change and one removal in this diff.
    assert review.has_changes


def test_old_line_no_is_one_based() -> None:
    review = build_diff_review("a\nb\nc", "a\nb\nC")
    assert review.hunks[0].old_line_no == 3
