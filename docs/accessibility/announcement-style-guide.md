# Announcement style guide

This guide defines the shared grammar for every status message and
screen-reader announcement in Quill. A single predictable shape lets users of
NVDA, JAWS, and Narrator parse an outcome in one pass and builds trust that the
app always reports what it just did.

The grammar is implemented in [quill/core/announcements.py](../../quill/core/announcements.py)
(`format_announcement`, `format_progress`, `pluralize`). Use those helpers
rather than hand-building strings, and keep this document in sync with them.

## The grammar

```
<Verb> <object>[, <count> <unit>(s)][, <detail>].
```

- **Verb.** The action. Use past tense for outcomes ("Rewrote", "Saved",
  "Replaced") and present participle for progress that precedes a slow action
  ("Rewriting", "Summarizing").
- **Object.** What was acted on: "paragraph", "document", "selection". Optional
  for verb-only outcomes such as "Copied".
- **Count and unit.** An optional quantity with an automatically pluralized
  unit and a thousands separator: "42 words", "1 word", "1,200 words",
  "2 matches".
- **Detail.** An optional trailing clause, its own comma segment.
- The sentence is capitalized and ends with a period (unless it already ends in
  `.`, `!`, or `?`).

## Examples

| Situation | Announcement |
| --- | --- |
| Rewrote the paragraph at the cursor | Rewrote paragraph, 42 words. |
| Summarized the whole document | Summarized document, 1,200 words. |
| Saved the file | Saved document. |
| Copied with no measurable object | Copied. |
| Replaced a one-word selection | Replaced selection, 1 word. |
| Nothing was selectable to act on | Nothing to rewrite. |
| Starting a slow rewrite | Rewriting paragraph, 42 words. |

## Rules

1. **Always report the outcome.** Every action that changes the document or
   state announces what happened, including the scope it chose when there was
   no selection (paragraph at the cursor, or the whole document).
2. **State the scope and count for content actions.** When an action operates on
   a body of text, include the object and the word count so the user knows the
   size of what changed.
3. **Say so when nothing happened.** If there is nothing to act on, announce it
   ("Nothing to rewrite.") instead of staying silent or sending an empty
   request.
4. **Keep it one short sentence.** No nested clauses beyond a single optional
   detail segment. Screen-reader users should not have to wait through a
   paragraph.
5. **No raw punctuation tricks.** Do not pad with parentheses or trailing
   ellipses; the helpers produce a clean sentence.
6. **Reuse the helpers.** Do not duplicate phrasing logic. Import
   `format_announcement` / `format_progress` from `quill.core.announcements`.

## Verb reference (common actions)

| Action | Progress verb | Outcome verb |
| --- | --- | --- |
| Rewrite | Rewriting | Rewrote |
| Summarize | Summarizing | Summarized |
| Fix grammar | Checking grammar in | Fixed grammar in |
| Continue writing | Continuing | Continued |
| Save | Saving | Saved |
| Replace | Replacing | Replaced |
| Copy | Copying | Copied |
