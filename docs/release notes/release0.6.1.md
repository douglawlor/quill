# QUILL 0.6.1 Release Notes: Braille Mode Phase 2

This is a focused, point release on top of 0.6.0. It ships the second of
the six Braille Mode phases promised in the 0.6.0 release notes: print-
page and running-head detection, plus the navigation commands that
make that data actually useful. Nothing in 0.6.0 changes; this is
additive.

If you are upgrading from a build earlier than 0.6.0, please read the
0.6.0 release notes first. They cover the Braille menu, the Universal
BRF Pack, the AI Hub consolidation, the GLOW on-by-default change, the
Quillin Platform, and the rest of the larger release.

## What's new in Braille Mode 0.6.1

### Print-page and running-head detection (BR-013)

QUILL now reads the print page (and the chapter running head) directly
off the BRF, so a braille proofreader no longer has to keep that map in
their head. The new `brf_page_detection.py` engine is pure — it
imports nothing from `wx` and is exhaustively unit-tested — and walks
the page map once to emit confidence-labelled indicators:

- **High confidence** — a print-page-change separator line of five or
  more hyphens followed by an anchor (`---------#ab`, `---------#12a`,
  or `---------#1`); *or* a right-margin page number on line 1 that
  matches the previous detected page and carries a continuation letter.
- **Medium confidence** — a right-aligned number on line 1 with no
  other anchor; *or* a consistent sequence across several pages.
- **Low confidence** — an ambiguous right-margin number; *or* a short
  page with multiple candidates.

The detector also produces a `BraillePageMarker` per page (the
right-margin number on the last line of each braille page) and a
`RunningHead` per page (the leading text of line 1, after stripping the
right-margin number). When the detector has no anchor for the caret
page, the status bar's print segment still reads `Print ?` so the
fallback is visible, not silent.

### Detailed status and print-page navigation (BR-014)

Six new commands in the Braille menu turn the detector output into
something a proofreader can act on:

- **Go to Print Page…** — type a print-page number; QUILL snaps the
  caret to the start of the braille page that hosts it and announces
  the result. Default value is the indicator closest to your current
  caret position.
- **Next Print Page Change** / **Previous Print Page Change** — step
  the caret to the next / previous print-page boundary in the
  detector output. If there is none, QUILL tells you rather than
  looping.
- **Announce Running Head** — reads the running head of the caret
  page aloud (or "No running head detected for this page." when the
  line-1 text is empty or absent).
- **Include Running Head in Status** / **Omit Running Head from
  Status** — toggle the `braille_include_running_head` setting.
  Detailed status only includes the running head when the setting is
  on; the menu item is purely a preference, not a one-shot announce.

`Read Detailed Braille Status` now composes the full example string
from the spec — print page, continuation letter, running head,
proofing state, and detection confidence — pulling live data from the
new detector. A typical announcement reads:

> "Braille page 12 of 87. Line 14 of 25. Cell 31 of 40. Print page 7;
> continuation a; Running head: Chapter 2; Last proofed page: 9; 3
> pages marked needs review; detected with high confidence."

`Read Current Print Page` no longer hard-codes "Print page unknown"; it
announces the most recent detected print page at or before the caret
(or "Print page unknown" when the detector has nothing to report).

Every new command degrades gracefully on non-braille documents — it
simply tells you "This is not a braille document" rather than doing
anything. Default key bindings are intentionally left unset (matching
the Phase 1 convention) so nothing collides with your screen reader
or existing editor shortcuts; assign your own in the keyboard
customizer, or run the commands from the Command Palette.

## Where the new code lives

- `quill/core/brf_page_detection.py` — pure detector module; 12 unit
  tests in `tests/unit/core/test_brf_page_detection.py`, including a
  real-world corpus test against the 5-page sample at
  `tests/corpus/braille/one_crazy_night.brf`.
- `quill/ui/main_frame_braille.py` — the new commands, the new menu
  items, and the `_compose_detailed_status` helper that wires the
  detector output into `read_detailed_braille_status`. Source-level
  wiring tests in `tests/unit/ui/test_braille_print_navigation.py`.

Strict-typed; `mypy --strict` is clean for the new module. The wider
braille test suite — status strings, page map, position resolver,
translation worker — remains green.

## What is still on the roadmap

- **Phase 3 (Proofing and Progress)** — the sidecar JSON, the restore-
  on-open behaviour, and the proofing commands (mark proofed / mark
  needs review / list proofed / etc.). Tracked in issues #238, #239,
  #240.
- **Phase 4 (Validation)** — warning rules that combine the page map
  and the detector output to catch ambiguous page boundaries.
- **Phase 6 (Source-to-BRF)** — a workflow that takes a print-text
  document through the translator and into a clean BRF ready for
  proofreading.

The detailed design for each of these phases remains in
`docs/planning/planning.md` (Feature: Braille Mode), preserved as a
reference for the release where they ship.

## Acknowledgements

Thank you to the screen-reader users and braille proofreaders who
filed the issues that drove this phase, and to the maintainers of
liblouis and the Universal BRF Pack whose tables make the translation
side of Braille Mode possible.
