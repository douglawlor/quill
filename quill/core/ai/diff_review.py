"""Line-by-line diff review model for AI edits (AI-7).

This is the wx-free core behind the accessible "Review AI Changes" dialog. It
turns an original text and a proposed revision into an ordered list of
segments. Each changed segment becomes a *hunk* the user can accept or reject
independently, so a person can apply all, some, or none of an AI edit and read
every change line by line before anything touches the document.

The model is deliberately simple and deterministic (built on
:class:`difflib.SequenceMatcher` over lines) so the same review can be described
to a screen reader, navigated by hunk, and re-applied as a single text
replacement (one undo step in the editor).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher

__all__ = [
    "DiffHunk",
    "DiffReview",
    "build_diff_review",
]


def _split_lines(text: str) -> list[str]:
    """Split into lines without losing the final-newline distinction.

    ``"a\\nb".split("\\n") == ["a", "b"]`` and ``"a\\nb\\n".split("\\n")``
    ``== ["a", "b", ""]``; joining back with ``"\\n"`` round-trips exactly, so
    accepting or rejecting hunks never silently adds or drops a trailing
    newline.
    """
    return text.split("\n")


@dataclass(frozen=True, slots=True)
class DiffHunk:
    """A single accept/reject unit of change.

    ``kind`` is one of ``"added"``, ``"removed"``, or ``"changed"``.
    ``old_lines`` are the original lines (empty for a pure addition) and
    ``new_lines`` are the proposed lines (empty for a pure deletion).
    ``old_line_no`` is the 1-based line number in the original where the change
    begins, for human-readable announcements.
    """

    index: int
    kind: str
    old_lines: tuple[str, ...]
    new_lines: tuple[str, ...]
    old_line_no: int

    def describe(self) -> str:
        """A one-line, screen-reader-friendly summary of this hunk."""
        position = f"at line {self.old_line_no}"
        if self.kind == "added":
            count = len(self.new_lines)
            return f"Added {count} line{'s' if count != 1 else ''} {position}."
        if self.kind == "removed":
            count = len(self.old_lines)
            return f"Removed {count} line{'s' if count != 1 else ''} {position}."
        return (
            f"Changed {len(self.old_lines)} line"
            f"{'s' if len(self.old_lines) != 1 else ''} to "
            f"{len(self.new_lines)} line"
            f"{'s' if len(self.new_lines) != 1 else ''} {position}."
        )

    def detail_lines(self) -> list[str]:
        """Readable old/new content, line by line, for the detail pane."""
        lines: list[str] = [self.describe()]
        for old in self.old_lines:
            lines.append(f"- removed: {old}" if old else "- removed: (blank line)")
        for new in self.new_lines:
            lines.append(f"+ added: {new}" if new else "+ added: (blank line)")
        return lines


@dataclass(frozen=True, slots=True)
class _Segment:
    """An ordered piece of the diff. ``hunk_index`` is -1 for unchanged text."""

    old_lines: tuple[str, ...]
    new_lines: tuple[str, ...]
    hunk_index: int


@dataclass(slots=True)
class DiffReview:
    """The full reviewable diff between two texts."""

    original: str
    revised: str
    hunks: list[DiffHunk] = field(default_factory=list)
    _segments: list[_Segment] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.hunks)

    def apply(self, accepted: set[int]) -> str:
        """Rebuild the text accepting only the hunks whose index is in *accepted*.

        Unchanged segments are kept verbatim. A rejected hunk keeps its original
        lines; an accepted hunk uses the proposed lines. The result is a single
        string ready to drop into the editor in one replacement (one undo).
        """
        out: list[str] = []
        for segment in self._segments:
            if segment.hunk_index < 0:
                out.extend(segment.old_lines)
            elif segment.hunk_index in accepted:
                out.extend(segment.new_lines)
            else:
                out.extend(segment.old_lines)
        return "\n".join(out)

    def accept_all(self) -> str:
        return self.apply({hunk.index for hunk in self.hunks})

    def reject_all(self) -> str:
        return self.apply(set())

    def summary(self) -> str:
        """A short overall summary for an opening announcement."""
        if not self.hunks:
            return "No changes to review."
        added = sum(1 for h in self.hunks if h.kind == "added")
        removed = sum(1 for h in self.hunks if h.kind == "removed")
        changed = sum(1 for h in self.hunks if h.kind == "changed")
        parts: list[str] = []
        if added:
            parts.append(f"{added} addition{'s' if added != 1 else ''}")
        if removed:
            parts.append(f"{removed} removal{'s' if removed != 1 else ''}")
        if changed:
            parts.append(f"{changed} change{'s' if changed != 1 else ''}")
        total = len(self.hunks)
        return f"{total} hunk{'s' if total != 1 else ''} to review: " + ", ".join(parts) + "."


def build_diff_review(original: str, revised: str) -> DiffReview:
    """Build a :class:`DiffReview` from *original* to *revised* text."""
    old_lines = _split_lines(original)
    new_lines = _split_lines(revised)
    matcher = SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    segments: list[_Segment] = []
    hunks: list[DiffHunk] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        old_block = tuple(old_lines[i1:i2])
        new_block = tuple(new_lines[j1:j2])
        if tag == "equal":
            segments.append(_Segment(old_block, new_block, -1))
            continue
        if tag == "insert":
            kind = "added"
        elif tag == "delete":
            kind = "removed"
        else:  # "replace"
            kind = "changed"
        index = len(hunks)
        hunks.append(
            DiffHunk(
                index=index,
                kind=kind,
                old_lines=old_block,
                new_lines=new_block,
                old_line_no=i1 + 1,
            )
        )
        segments.append(_Segment(old_block, new_block, index))
    return DiffReview(original=original, revised=revised, hunks=hunks, _segments=segments)
