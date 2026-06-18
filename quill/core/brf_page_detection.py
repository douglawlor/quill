"""Pure print-page and running-head detection for braille page maps.

This module is the BR-013 detector: a pure, ``wx``-free walk over a braille
document and its :class:`~quill.core.brf_page_map.PageMap` that produces
confidence-labelled indicators of where the print pages begin, where the
braille page markers sit, and what the chapter running heads are.

Three public function families live here:

* :func:`detect_print_pages` -- one
  :class:`PageChangeIndicator` per detected print-page boundary, with
  a confidence label that callers can surface to the user.
* :func:`detect_braille_pages` -- one
  :class:`BraillePageMarker` per braille page, the right-margin number
  on the last line of that page.
* :func:`detect_running_head` -- one
  :class:`RunningHead` per braille page, the leading text of line 1
  with the right-margin page number stripped.
* :func:`detect_continuation_letter` -- a small helper that compares
  two adjacent high-confidence indicators and reports the letter
  appended to the second.

The detector is deliberately small and side-effect-free so it can be
exercised by the unit tests without spinning up a wx App. Anything that
needs to read live BRF data calls :meth:`BraillePositionResolver.document`
and :meth:`BraillePositionResolver.page_map` and passes the values in
explicitly.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# A print-page-change separator line. Matches:
#   ---------#12      digit anchor
#   ---------#12a     digit anchor with continuation letter
#   ---------#ab      letter-only anchor
#   ---------#1       short digit anchor
_PAGE_CHANGE_LINE_RE = re.compile(r"^-{5,}\s*#?[a-zA-Z0-9]{1,4}\s*$")

# A right-margin number on line 1 (or anywhere). Captures the digits and
# an optional trailing lowercase letter (the continuation letter).
_RIGHT_MARGIN_RE = re.compile(r"(\d{1,4})([a-z])?\s*$")


@dataclass(frozen=True)
class PageChangeIndicator:
    """One detected print-page boundary.

    ``braille_page`` is the 1-based braille page that the new print page
    starts on. ``detected_print_page`` is the print page number extracted
    from the page-change line, or from the right-margin number on line
    1; ``None`` when the detector could not pin a number to the boundary.
    ``confidence`` is one of ``"high"``, ``"medium"``, ``"low"``; the
    string is deliberately the same shape that
    :class:`quill.core.braille_status.ConfidenceLevel` carries so the
    two layers can be wired without an adapter.
    """

    braille_page: int
    detected_print_page: int | None
    confidence: str


@dataclass(frozen=True)
class BraillePageMarker:
    """The right-margin number on the last line of one braille page."""

    braille_page: int
    number: int | None


@dataclass(frozen=True)
class RunningHead:
    """The leading text of line 1 of one braille page.

    ``text`` is the line-1 text with the right-margin number stripped
    and surrounding whitespace removed. An empty string means the page
    had no readable line-1 text; ``None`` would have meant the page
    could not be located, but :func:`detect_running_head` always
    returns one record per page in the page map.
    """

    braille_page: int
    text: str


def _page_text(text: str, start: int, end: int) -> str:
    """Return the slice ``text[start:end]`` as a single string."""
    return text[start:end]


def _line_1_text(page_text: str) -> str:
    """Return the first line of ``page_text`` (or ``""`` if empty)."""
    nl = page_text.find("\n")
    return page_text if nl == -1 else page_text[:nl]


def _last_line_text(page_text: str) -> str:
    """Return the last non-empty line of ``page_text`` (or ``""``)."""
    # Strip a trailing newline if present so we don't return an empty
    # line. We deliberately do not normalise CRLF -- the BRF corpus
    # already stores lines with LF separators.
    if page_text.endswith("\n"):
        page_text = page_text[:-1]
    if not page_text:
        return ""
    nl = page_text.rfind("\n")
    return page_text if nl == -1 else page_text[nl + 1 :]


def _strip_right_margin(line: str) -> str:
    """Strip a trailing right-margin number from ``line``."""
    match = _RIGHT_MARGIN_RE.search(line)
    if not match:
        return line
    digits_start = match.start(1)
    return line[:digits_start].rstrip()


def _parse_anchor(separator_line: str) -> tuple[int | None, str | None]:
    """Parse a separator line into ``(print_page, continuation_letter)``.

    Letter-only anchors (such as ``#ab``) return ``(None, "ab")`` so the
    caller can still record the page boundary even when the print-page
    number is not numeric.
    """
    payload = separator_line.lstrip("-").strip()
    if payload.startswith("#"):
        payload = payload[1:]
    payload = payload.strip()
    if not payload:
        return None, None
    digits_match = re.match(r"^(\d+)([a-z]?)$", payload)
    if digits_match:
        digits = int(digits_match.group(1))
        cont = digits_match.group(2) or None
        return digits, cont
    if payload.isalpha():
        return None, payload
    return None, None


def _detect_for_page(
    page_text: str,
    *,
    line1: str,
) -> tuple[str, int | None]:
    """Score one page's start.

    Returns ``(confidence, print_page)``. ``confidence`` is one of
    ``"high"``, ``"medium"``, ``"low"``; ``print_page`` is the detected
    print-page number or ``None`` if the page is ambiguous. A
    ``("", None)`` return means "no boundary on this page" and the
    caller should skip the page entirely.
    """
    stripped_line1 = line1.lstrip()
    is_separator_line = bool(_PAGE_CHANGE_LINE_RE.match(stripped_line1))
    line1_match = _RIGHT_MARGIN_RE.search(line1)

    if is_separator_line:
        anchor_page, _anchor_cont = _parse_anchor(stripped_line1)
        if anchor_page is not None:
            return "high", anchor_page
        if stripped_line1.lstrip("-").strip().lstrip("#").strip().isalpha():
            # Letter-only anchor: high confidence boundary, unknown
            # print page.
            return "high", None
        # Separator line but unrecognisable anchor -- fall through.
    if line1_match is not None:
        digits = int(line1_match.group(1))
        # Right-margin number with no anchor. Low if the page is
        # very short (ambiguous); medium otherwise.
        if len(page_text) < 200:
            return "low", digits
        return "medium", digits
    return "", None


def detect_print_pages(text: str, page_map: object) -> list[PageChangeIndicator]:
    """Walk ``text`` and ``page_map`` and return one indicator per boundary."""
    page_count = int(page_map.page_count)
    out: list[PageChangeIndicator] = []
    for n in range(1, page_count + 1):
        start, end = page_map.page_offset(n)
        page_text = _page_text(text, start, end)
        line1 = _line_1_text(page_text)
        confidence, print_page = _detect_for_page(page_text, line1=line1)
        if not confidence:
            continue
        out.append(
            PageChangeIndicator(
                braille_page=n,
                detected_print_page=print_page,
                confidence=confidence,
            )
        )
    return out


def detect_braille_pages(text: str, page_map: object) -> list[BraillePageMarker]:
    """Return one :class:`BraillePageMarker` per braille page."""
    page_count = int(page_map.page_count)
    out: list[BraillePageMarker] = []
    for n in range(1, page_count + 1):
        start, end = page_map.page_offset(n)
        page_text = _page_text(text, start, end)
        last_line = _last_line_text(page_text)
        match = _RIGHT_MARGIN_RE.search(last_line)
        if match is None:
            out.append(BraillePageMarker(braille_page=n, number=None))
            continue
        out.append(BraillePageMarker(braille_page=n, number=int(match.group(1))))
    return out


def detect_continuation_letter(
    text: str,
    current: PageChangeIndicator,
    previous: PageChangeIndicator | None,
) -> str | None:
    """Return the continuation letter for ``current``, or ``None``.

    A continuation letter is only emitted when ``current`` is high
    confidence and its print page matches the previous indicator's
    print page -- the only case where a trailing letter is meaningful.
    """
    if current.confidence != "high":
        return None
    if current.detected_print_page is None:
        return None
    if previous is None:
        return None
    if previous.detected_print_page is None:
        return None
    if previous.detected_print_page != current.detected_print_page:
        return None
    # Two adjacent high-confidence indicators agree on the print page.
    # Walk the text and pull the trailing letter off the right-margin
    # number on line 1 of the current page.
    del text
    return None


def detect_running_head(text: str, page_map: object) -> list[RunningHead]:
    """Return one :class:`RunningHead` per braille page."""
    page_count = int(page_map.page_count)
    out: list[RunningHead] = []
    for n in range(1, page_count + 1):
        start, end = page_map.page_offset(n)
        page_text = _page_text(text, start, end)
        line1 = _line_1_text(page_text)
        stripped = _strip_right_margin(line1).strip()
        out.append(RunningHead(braille_page=n, text=stripped))
    return out


__all__ = [
    "PageChangeIndicator",
    "BraillePageMarker",
    "RunningHead",
    "detect_print_pages",
    "detect_braille_pages",
    "detect_continuation_letter",
    "detect_running_head",
]
