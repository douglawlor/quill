# QUILL 0.7.0 Verbosity System — Additional Magic, Settings, Knobs, and UX Enhancements

## Purpose of This Addendum

This addendum extends the QUILL 0.7.0 Verbosity System with additional user experience ideas, settings, knobs, and “magic” behaviors.

The goal is not to make the first-run experience complicated. The goal is to make QUILL feel deeply personal, screen-reader-first, recoverable, and intelligent while keeping the default experience calm.

The guiding design principle should be:

> Simple by default. Powerful when explored. Safe always.

---

# 1. Settings Should Have Three Layers

To prevent overwhelming users, QUILL should organize verbosity controls into three layers.

## Layer 1: Simple

Shown to everyone.

* Beginner
* Normal
* Expert
* Quiet
* Meeting Mode
* Announcement History
* Reset/Safe Mode

## Layer 2: Customize

For users who want more control.

* Channel checkboxes
* Per-verb overrides
* Per-chord overrides
* Token templates
* QVP packs
* Preview Lab
* Import/export

## Layer 3: Advanced

For power users, testers, pack authors, and contributors.

* Token parser details
* Golden test preview
* Explanation traces
* Channel-specific templates
* Suppression rules
* Repetition collapse settings
* Screen reader handoff behavior
* Braille compacting rules
* Debug logging

This avoids dumping every knob into one giant settings page.

---

# 2. Searchable Settings

QUILL should include a search box in Verbosity Preferences.

Users should be able to type:

* “quiet”
* “braille”
* “sound”
* “selection”
* “search results”
* “errors”
* “repeat”
* “history”
* “QVP”
* “keyboard”
* “too much”
* “page”

The settings UI should narrow to matching settings and actions.

This is especially valuable for screen reader users because it avoids arrowing through long settings lists.

---

# 3. Verbosity Recipes

QUILL should ship with ready-made “recipes” in addition to the four base profiles.

Examples:

* Beginner Writer
* Expert Editor
* Braille First
* Meeting Safe
* Classroom Training
* Markdown Author
* Code Reviewer
* Minimal Navigation
* Detailed Search
* Compare Review
* Document Cleanup
* Transcription Prep

A recipe is not a separate profile engine. It is a saved combination of profile, channel mix, per-verb defaults, and optional templates.

The UI could say:

> Start with a recipe.

Then the user can customize from there.

---

# 4. Announcement Budget

Add an “announcement budget” concept.

This prevents QUILL from becoming chatty during repeated actions.

Settings:

* Collapse repeated announcements.
* Suppress identical announcements after N repeats.
* Speak every Nth repeated movement.
* Always speak errors.
* Always speak document boundary changes.
* Always speak mode changes.
* Never suppress warnings.

Example:

If the user holds down Down Arrow, QUILL should not necessarily speak a full context message every time.

Instead:

> Line 14
> Line 15
> Line 16
> 10 more lines moved.

Or in Expert:

> 14
> 15
> 16

This makes QUILL feel calmer and faster.

---

# 5. Repetition Collapse

Repeated announcements should be collapsible.

Example:

If the same message happens repeatedly:

> No next heading.

Instead of saying it ten times, QUILL could say:

> No next heading. Repeated 5 times.

Settings:

* Collapse repeated routine messages.
* Collapse repeated errors.
* Collapse repeated navigation boundary messages.
* Delay before summarizing repeated messages.
* Never collapse critical errors.

This is a huge quality-of-life feature.

---

# 6. Screen Reader Handoff Mode

QUILL should avoid fighting the screen reader.

Some information should be spoken by QUILL. Some should be left to the screen reader.

Add a setting:

> Screen reader handoff

Options:

* QUILL speaks full context.
* QUILL speaks only editor-specific context.
* Let screen reader handle text; QUILL speaks state changes only.
* Expert handoff: only errors, modes, and structural changes.

This helps avoid double-speaking.

Example:

When arrowing through text, the screen reader may already read the line. QUILL may only need to add:

> Modified. Markdown heading level 2.

Or:

> Search result 3 of 12.

---

# 7. Typing Echo Controls

QUILL should expose typing echo preferences separate from screen reader behavior.

Settings:

* Character echo
* Word echo
* No typing echo
* Punctuation echo
* Whitespace echo
* Indentation echo
* Speak tabs
* Speak spaces
* Speak blank lines
* Speak autocorrect or expansion results

This is especially useful for users writing Markdown, code, or structured text.

---

# 8. Indentation and Whitespace Verbosity

For coding and Markdown, indentation matters.

Add settings:

* Speak indentation changes.
* Speak indentation level only when it changes.
* Speak tabs as “tab” or “4 spaces.”
* Speak trailing spaces.
* Warn on mixed tabs and spaces.
* Warn on indentation-sensitive files.
* Suppress indentation in plain prose.
* Enable indentation detail for Python, YAML, Markdown lists, and code blocks.

Example:

> Indent level 2, list item.

Or:

> Python block, 4 spaces.

This should be task-aware, not noisy everywhere.

---

# 9. Selection Verbosity Knobs

Selection feedback needs its own controls.

Settings:

* Speak selected text.
* Speak selection length only.
* Speak start and end positions.
* Speak line count.
* Speak word count.
* Speak character count.
* Speak first N characters of selection.
* Speak last N characters of selection.
* Suppress selection text above N characters.
* Announce selection direction.
* Announce rectangular/block selection if supported.

Examples:

Beginner:

> Selected “accessibility agents,” 2 words.

Expert:

> Selected 2 words.

Quiet/Braille:

> sel 2w

---

# 10. Clipboard Verbosity Knobs

Clipboard actions deserve careful control.

Settings:

* Speak copied text.
* Speak copied length only.
* Speak cut text.
* Speak pasted text.
* Speak paste length only.
* Warn when pasting multiline content.
* Warn when clipboard is empty.
* Warn when copied content includes hidden characters.
* Suppress clipboard text above N characters.

Examples:

> Copied 3 lines, 42 words.

> Pasted 12 lines.

> Clipboard empty.

This avoids accidental huge speech dumps.

---

# 11. Search Result Verbosity Knobs

Search is one of the most important places for verbosity control.

Settings:

* Speak result number.
* Speak total results.
* Speak surrounding context.
* Speak line number.
* Speak column.
* Speak wrap-around.
* Speak no-results suggestions.
* Speak replacement count.
* Speak skipped binary/large files if applicable.
* Speak first result automatically.
* Suppress repeated “not found” messages.

Examples:

Beginner:

> Result 3 of 12. Line 42. Found “keyboard manager” in heading level 2.

Expert:

> 3 of 12, line 42.

---

# 12. Error Coaching

Errors should be more helpful in Beginner mode.

Instead of only:

> Error.

QUILL should support error coaching.

Example:

> Could not save file. The folder may be read-only. Press Ctrl+Shift+E for details.

Settings:

* Beginner error coaching on/off.
* Include likely cause.
* Include suggested next action.
* Include technical details only on request.
* Copy error details to clipboard.
* Add error to Announcement History.

Expert mode can stay concise:

> Save failed. Access denied.

---

# 13. “Details on Demand”

QUILL should avoid over-speaking by making more details available on demand.

Pattern:

Say the short version first.

Then offer:

> Press QUILL key + D for details.

Examples:

> Save failed. Press QUILL key + D for details.

> 12 replacements made. Press QUILL key + D for details.

Settings:

* Enable details-on-demand.
* Timeout for details prompt.
* Always offer details for errors.
* Offer details for warnings.
* Never offer details for routine confirmations.

This keeps the main flow fast but keeps help nearby.

---

# 14. Announcement Detail Levels Per Category

Instead of only global Beginner/Normal/Expert, let users tune categories independently.

Categories:

* Navigation
* Editing
* Selection
* Search
* Replace
* File operations
* Markdown
* Code
* Errors
* Warnings
* Progress
* Git/GitHub integration later
* Braille/BRF workflow later

Each category can use:

* Beginner
* Normal
* Expert
* Quiet
* Profile default

Example:

A user might want:

* Expert navigation
* Normal editing
* Beginner search
* Detailed errors
* Quiet selection

This gives real-world flexibility.

---

# 15. Boundary Announcements

Boundary messages should be configurable.

Settings:

* Speak top of document.
* Speak bottom of document.
* Speak start/end of line.
* Speak start/end of selection.
* Speak first/last search result.
* Speak beginning/end of paragraph.
* Speak beginning/end of heading region.
* Speak when navigation wraps.
* Use sound for boundary.
* Use braille-only boundary markers.

Examples:

> Top of document.

> Bottom.

> Wrapped to first result.

Expert users may want very short boundary announcements.

---

# 16. Progress Announcement Controls

Long operations need thoughtful progress speech.

Settings:

* Speak progress every N percent.
* Speak progress every N seconds.
* Speak only start and finish.
* Speak errors immediately.
* Braille progress updates.
* Sound on completion.
* Quiet completion behavior.
* Cancel announcement detail.

Examples:

> Converting Markdown to EPUB, 40 percent.

> Complete. 12 files converted, 1 warning.

This will matter for QUILL workflows involving conversion, validation, compare, search across files, and document processing.

---

# 17. Mode Change Announcements

QUILL should treat mode changes as high-priority announcements.

Examples:

* Insert/overwrite mode.
* Read-only mode.
* Markdown mode.
* Code mode.
* Quiet Mode.
* Meeting Mode.
* Search panel active.
* Compare mode.
* Preview mode.
* Snippet expansion mode.
* Abbreviation mode.
* Console mode if added later.

Settings:

* Always speak mode changes.
* Play sound for mode changes.
* Show status badge.
* Repeat mode on demand.

Command:

* `QUILL key + M`: speak current modes.

Example:

> Markdown file. Expert profile. Quiet Mode off. Meeting Mode off. Modified document.

---

# 18. “Where Am I?” Command

Add a command for complete current context.

Recommended:

* `QUILL key + W`: Where am I?

It should speak a profile-aware summary.

Beginner:

> You are in Chapter 2, heading “Token Editor,” line 14 of 80, column 5. Markdown file. Modified. Expert verbosity is off.

Expert:

> Token Editor, line 14, column 5, modified.

Braille:

> Token Editor l14 c5 mod

Settings:

* Include file name.
* Include path.
* Include heading.
* Include line/column.
* Include page.
* Include selection.
* Include modified state.
* Include profile/modes.
* Include encoding.
* Include indentation mode.

This would be one of the most useful screen-reader-first commands in QUILL.

---

# 19. “What Changed?” Command

Add a command that summarizes what changed recently.

Recommended:

* `QUILL key + Shift+W`: What changed?

Examples:

> Since last checkpoint: 3 lines inserted, 1 heading changed, document modified.

Or:

> Last action: replaced 12 occurrences of “foo” with “bar.”

This can be powered by the same announcement history and event trace infrastructure.

---

# 20. “Speak Status Bar” Command

The status bar should be reachable.

Recommended:

* `QUILL key + S`: speak status bar.

Output should include:

* File state.
* Line/column.
* Selection.
* Encoding.
* Profile.
* Quiet/Meeting state.
* Modified/read-only state.
* Active mode.
* Current operation if any.

This gives parity with visual users.

---

# 21. Braille-Specific Knobs

Braille users need dedicated controls.

Settings:

* Use compact braille announcements.
* Use full braille announcements.
* Clip braille output to display width.
* Preferred braille display width.
* Use short labels: `ln`, `col`, `p`, `sel`.
* Include page number.
* Include line number.
* Include heading.
* Include selection count.
* Prioritize position over prose.
* Prioritize errors over routine info.
* Use braille-only status markers.

Example compact braille:

> p7/87 l14 c3 mod

This should be separate from speech verbosity.

---

# 22. Punctuation and Symbol Profiles

QUILL should have symbol verbosity presets.

Useful for Markdown and code.

Profiles:

* None
* Some
* Most
* All
* Code
* Markdown
* Math
* Custom

Settings:

* Speak asterisk as star or asterisk.
* Speak backtick.
* Speak hash as heading marker in Markdown.
* Speak brackets.
* Speak quotes.
* Speak underscores.
* Speak indentation.
* Speak list markers.
* Speak table pipes.
* Speak code fences.

Example:

Markdown mode:

> Heading level 2, Verbosity System

Instead of:

> number number space Verbosity System

But in raw/code mode, users may want the actual symbols.

---

# 23. Markdown-Aware Verbosity

QUILL should eventually include Markdown-specific verbosity knobs.

Settings:

* Announce heading level.
* Announce list nesting.
* Announce task list checked/unchecked.
* Announce blockquote.
* Announce code block language.
* Announce link text and URL on demand.
* Announce image alt text.
* Announce table cell coordinates.
* Announce horizontal rule.
* Suppress raw Markdown markers when helpful.
* Speak raw markers in code/review mode.

Examples:

> Heading level 2, Token Editor.

> Bullet, level 2.

> Link: QUILL homepage. Press details for URL.

This would make QUILL feel deeply aware of authoring workflows.

---

# 24. Code-Aware Verbosity

For code files, QUILL should have optional code-aware output.

Settings:

* Speak function/class boundaries.
* Speak indentation changes.
* Speak syntax errors if known.
* Speak matching bracket context.
* Speak comment line.
* Speak docstring start/end.
* Speak folded region if folding exists.
* Speak current symbol.
* Speak current scope.
* Speak line diagnostics.
* Speak imports section.
* Speak TODO/FIXME comments.

Examples:

> Function save_template, line 42.

> Indent level 3.

> Closing bracket for if statement.

This should be opt-in and language-aware where possible.

---

# 25. Compare/Diff Verbosity

QUILL’s compare workflows should get special verbosity.

Settings:

* Speak change type: inserted, deleted, modified.
* Speak changed text.
* Speak line number.
* Speak previous/next change count.
* Speak surrounding context.
* Speak only summary.
* Braille compact diff mode.
* Sound on change boundary.
* Collapse repeated unchanged lines.

Examples:

Beginner:

> Change 4 of 12. Modified line 83. Original: “Normal profile.” New: “Expert profile.”

Expert:

> Change 4 of 12, modified, line 83.

This would be powerful for screen reader users reviewing documents or code.

---

# 26. File Operation Verbosity

Opening, saving, and exporting should have knobs.

Settings:

* Speak full path.
* Speak file name only.
* Speak extension.
* Speak encoding.
* Speak line ending style.
* Speak modified state.
* Speak read-only state.
* Speak file size.
* Speak autosave status.
* Speak backup status.
* Warn on format conversion.
* Warn on destructive overwrite.

Examples:

> Saved verbosity.md.

> Saved. UTF-8, Windows line endings.

> Warning: saving as plain text may remove formatting.

---

# 27. Encoding and Line Ending Verbosity

Since QUILL cares about text formats, expose settings for technical users.

Settings:

* Announce encoding on open.
* Announce encoding on save.
* Announce line endings.
* Warn on mixed line endings.
* Warn before changing encoding.
* Speak minimum encoding decision.
* Speak Unicode normalization warnings.
* Speak invalid character replacement warnings.

This pairs nicely with QUILL’s broader document/format ambitions.

---

# 28. Notification Priority Levels

Announcements should have priorities.

Priority levels:

* Silent
* Trace
* Routine
* Info
* Success
* Warning
* Error
* Critical

Each profile can decide what to do with each priority.

Example:

Expert:

* Routine: suppress
* Info: braille/status only
* Success: short speech
* Warning: speech + braille
* Error: speech + braille + sound
* Critical: assertive speech + sound

This creates a clean architecture for future features.

---

# 29. Verbosity Rules Engine

Add an advanced rules layer later, but design for it now.

Example rules:

* If document is Markdown and line starts with `#`, announce heading level.
* If selection is more than 500 characters, speak count only.
* If command repeats more than 5 times, switch to compact output.
* If Meeting Mode is on, route routine messages to braille only.
* If error occurs, always override Quiet Mode with status/braille and optional speech prompt.

Rules should be data-only and safe.

No arbitrary Python.

---

# 30. Per-Workspace Verbosity

QUILL could support workspace-level verbosity.

Examples:

* Writing project uses Normal.
* Coding project uses Expert with indentation details.
* Training folder uses Beginner.
* Meeting notes folder uses Quiet/Meeting Safe.
* Braille transcription folder uses Braille First.

Settings:

* Use global defaults.
* Use workspace profile.
* Ask when opening folder.
* Remember choice for this folder.

This makes QUILL adapt to real work contexts.

---

# 31. Per-File Verbosity

Some files need different behavior.

Examples:

* Markdown guide: heading/list verbosity.
* Python file: indentation/symbol verbosity.
* BRF file: page/line/braille position.
* Log file: timestamp and severity verbosity.
* CSV file: row/column verbosity.

Settings:

* Ask when file type is detected.
* Remember for this file.
* Remember for this extension.
* Never ask again.

---

# 32. Temporary Verbosity Boost

Sometimes users need more detail for just a moment.

Add:

* `QUILL key + Up`: temporarily increase verbosity for next command.
* `QUILL key + Down`: temporarily decrease verbosity for next command.

Examples:

A user normally works in Expert but wants the next command explained in Beginner.

> Next command will use Beginner detail.

After one command, QUILL returns to the prior profile.

This is magical and very useful.

---

# 33. Hold-to-Explain

A variation of temporary boost:

If the user holds a command slightly longer or uses a modified chord, QUILL gives more detail.

Example:

* Press command normally: concise.
* Press command with QUILL key: detailed explanation.

This should be used carefully, but it could make learning easier.

---

# 34. Training Mode

Training Mode is different from Beginner.

Beginner changes announcement detail.

Training Mode teaches commands.

Training Mode might say:

> You moved to the next word. The shortcut was Ctrl+Right. You can customize this in Keyboard Manager.

Settings:

* Teach shortcuts.
* Teach concepts.
* Teach related commands.
* Stop teaching after N successful uses.
* Always offer details on demand.
* Include link to help topic.
* Include “do not teach this again.”

This could be wonderful for new users.

---

# 35. Contextual Help Hooks

Announcements could connect to help.

Example:

> Unknown token. Press F1 for token help.

Or:

> QVP install failed. Press F1 for pack requirements.

Settings:

* Offer help hints in Beginner.
* Suppress help hints in Expert.
* Always show help in status bar.
* Add help link to explanation trace.

---

# 36. Friendly Names for Technical Concepts

Some settings should use plain language but expose technical terms.

Example:

User-facing:

> Be quiet during meetings.

Technical:

> Meeting Mode: suppress routine speech and sound.

User-facing:

> Say less when I repeat a command.

Technical:

> Repetition collapse.

User-facing:

> Let me hear that again.

Technical:

> Announcement History replay.

This keeps the product friendly without hiding power.

---

# 37. “Confidence Check” Wizard

After setup, QUILL could run a short confidence check.

It asks:

> Did that feel like too much, too little, or just right?

For sample actions:

* Move by line.
* Save file.
* Search result.
* Error.
* Selection.

This can tune the initial profile.

No AI needed. No telemetry needed.

---

# 38. Community Pack Preview and Diff

When installing a QVP, QUILL should show what it will change.

Before install:

* Pack name.
* Author.
* Version.
* License.
* Applies to which verbs.
* New templates.
* Conflicting templates.
* Required QUILL version.
* Sample preview.

Add “Compare with current profile.”

Example:

> Current: Page 7 of 87.
> Pack: Chapter 2, page 7 of 87.

This makes QVP install trustworthy.

---

# 39. QVP Trust Labels

Even without signing in v1, QUILL can provide trust labels.

Labels:

* Built-in
* User-created
* Imported from file
* QVP installed
* Unknown author
* Requires newer QUILL
* Contains unsupported tokens
* Safe data-only pack

This helps users understand source and risk.

---

# 40. QVP “Copy as User Template”

Users should be able to copy a QVP template into their own library.

Action:

> Copy to My Templates

Then they can edit it without modifying the installed pack.

This respects pack integrity while allowing customization.

---

# 41. Verbosity Conflict Checker

QUILL should detect conflicting settings.

Examples:

* Speech disabled globally but user expects speech template.
* Quiet Mode on while Preview Lab tests speech.
* Per-chord override conflicts with per-verb override.
* QVP template applies to no verbs.
* Braille template exists but braille channel off.
* Sound event configured but sound channel off.

Offer explanations:

> This template has a speech version, but speech is currently off in Quiet Mode.

This prevents confusion.

---

# 42. “Explain My Settings”

Add a summary command:

> Explain my verbosity settings.

Output:

> You are using Expert profile. Speech and braille are on. Sound is errors only. Quiet Mode is off. Meeting Mode is off. Selection movement is set to Quiet. Search results use Beginner detail. Announcement History keeps the last 100 items.

This helps users and support people.

---

# 43. Export Support Bundle

For bug reports and community support, QUILL should export a safe support bundle.

Include:

* Verbosity settings.
* Enabled QVP metadata.
* Recent announcement traces with document text redacted.
* Version.
* Screen reader if detectable.
* OS.
* Active profile.
* Keymap conflicts.

Exclude or redact:

* Document content.
* File paths if privacy mode is enabled.
* Clipboard contents.
* Personal text.

This would make troubleshooting much easier.

---

# 44. Privacy Controls

Because Announcement History and traces can contain document text, include privacy settings.

Settings:

* Store announcement history.
* Store document text in history.
* Redact document text in history.
* Clear history on exit.
* Clear history now.
* Do not include text in support exports.
* Private mode for current document.
* Disable history for files in specific folders.

This is important for trust.

---

# 45. Private Document Mode

Add a per-document mode:

> Private Document Mode

When enabled:

* Do not store announcement history for this file.
* Do not include text in traces.
* Do not include text in support bundle.
* Copy/replay only structural info unless user explicitly allows.

Useful for:

* Legal documents.
* Medical information.
* Personal writing.
* Password notes.
* Confidential work.

---

# 46. Speech Rate and Pause Knobs

Some users may want announcement pacing controls.

QUILL may not control screen reader speech rate directly, but it can control pacing.

Settings:

* Pause before announcements.
* Pause after mode changes.
* Pause between multi-part announcements.
* Delay details-on-demand prompt.
* Keep announcements short during rapid navigation.
* Interrupt previous announcement on new command.
* Queue announcements.
* Drop stale routine announcements.

This matters when users move quickly.

---

# 47. Announcement Queue Policy

QUILL should define how it handles rapid events.

Options:

* Interrupt routine announcements.
* Queue warnings.
* Always speak latest position.
* Drop stale navigation messages.
* Never drop errors.
* Collapse repeated messages.
* Finish current announcement before preview.

This prevents speech backlog.

---

# 48. “Last Important Announcement”

In addition to last announcement, support last important announcement.

Command:

* `QUILL key + Shift+I`: repeat last important announcement.

Important means:

* Warning
* Error
* Mode change
* Save failure
* Operation complete
* Search no results

This helps when routine navigation has already replaced the last announcement.

---

# 49. Earcons With Text Equivalents

If QUILL uses sounds, every sound must have a text equivalent.

Settings:

* Sound only when text equivalent is available.
* Speak sound meaning on first use.
* Learn sounds mode.
* Disable decorative sounds.
* Error sound on/off.
* Success sound on/off.
* Boundary sound on/off.

Example first-use teaching:

> You heard the boundary sound. It means top or bottom of a region.

---

# 50. Learn Sounds Mode

A small onboarding feature:

> Learn QUILL sounds

The user can arrow through sounds:

* Success
* Warning
* Error
* Boundary
* Mode change
* Completion
* Search result

Each plays and explains its meaning.

This makes sound usable rather than mysterious.

---

# 51. Announcement Favorites

Let users mark helpful announcements or templates as favorites.

Use cases:

* Favorite a template.
* Favorite a QVP pack.
* Favorite a history entry.
* Favorite a Preview Lab scenario.
* Favorite a setting.

This may be optional, but it adds polish.

---

# 52. “Pin This Status”

Allow a user to pin one piece of status to the status bar or braille/status output.

Examples:

* Current heading
* Current page
* Current line/column
* Current profile
* Modified state
* Selection count
* Search result count

Braille users especially may appreciate persistent compact status.

---

# 53. Smart Status Rotation

For limited braille/status space, QUILL could rotate or prioritize status fields.

Priority order examples:

* Errors
* Warnings
* Current mode
* Selection
* Position
* Modified state
* Profile

Settings:

* Prioritize position.
* Prioritize document state.
* Prioritize search.
* Prioritize braille page.
* Custom order.

---

# 54. “Speak Current Template”

In token editor and per-verb settings, add:

> Speak current template

Command:

* `Ctrl+Shift+R`

This reads:

* Human preview.
* Raw template.
* Supported tokens.
* Validation state.
* Source.

Useful for template authors.

---

# 55. Token Help on Demand

In the token palette, pressing F1 on a token should explain it.

Example:

> print_page: The current print page number if available. Type: integer. Filters allowed: ordinal, pad. Available for print page navigation verbs.

This helps nontechnical users learn the system.

---

# 56. Template Examples Per Token

Each token should include examples.

Example for `{selection_count}`:

* “3 characters selected”
* “2 words selected”
* “4 lines selected”

The token editor could expose:

> Examples for this token

This makes customization less intimidating.

---

# 57. Pack Author Mode

For QVP authors, add an advanced mode.

Features:

* Validate all templates.
* Preview against all built-in scenarios.
* Export sample QVP.
* Check unsupported tokens.
* Check missing metadata.
* Check channel-specific fields.
* Generate golden test fixtures.
* Copy pack summary.

This helps the community create high-quality packs.

---

# 58. Built-In Sample QVPs

Ship a few sample packs:

* Beginner Friendly
* Expert Minimal
* Braille Compact
* Markdown Author
* Meeting Safe
* Compare Review

These demonstrate the system and give users useful starting points.

---

# 59. “Make This My Default”

When a user customizes a verb, template, or profile, offer:

> Make this my default for similar actions?

Examples:

* All navigation commands.
* All selection commands.
* All search commands.
* All Markdown commands.
* All errors.

This reduces repetitive customization.

---

# 60. Bulk Editing

Advanced users should be able to bulk apply settings.

Examples:

* Set all navigation to Expert.
* Set all selection to Quiet.
* Set all errors to Beginner detail.
* Apply template to all search verbs.
* Reset all Markdown verbs.

This should live in Advanced or Library, not the basic UI.

---

# 61. Undo for Settings Changes

Verbosity settings changes should be undoable.

Examples:

> Applied Expert to 12 navigation verbs. Press Ctrl+Z to undo.

This is especially important for bulk changes and QVP applies.

---

# 62. Settings Change History

Keep a small local history of verbosity settings changes.

Useful actions:

* Undo last change.
* View recent changes.
* Restore previous verbosity state.
* Compare before/after.

This helps users experiment safely.

---

# 63. “Test My Current Settings”

Add a button:

> Test my current settings

It runs a short Preview Lab sequence:

* Navigation
* Selection
* Search
* Save
* Error

Then asks:

> Was that too much, too little, or just right?

This ties together Preview Lab and feedback tuning.

---

# 64. Recommended Settings Suggestions

QUILL can make local, rules-based suggestions.

Examples:

* “You use Quiet Mode often. Make Meeting Safe your default for this workspace?”
* “You often mark selection announcements as too much. Set selection to Expert?”
* “You installed a braille compact pack but braille is off. Turn braille channel on?”
* “You are editing Markdown files often. Enable Markdown-aware announcements?”

No AI required. No telemetry required.

---

# 65. Accessibility Persona Setup

Setup Wizard could ask what kind of experience the user wants.

Not medical or identity-based. Just workflow-based.

Examples:

* I am learning QUILL.
* I move quickly and want less speech.
* I use braille heavily.
* I often work in meetings.
* I write Markdown.
* I write code.
* I review documents.
* I want maximum guidance.

Then QUILL chooses a recipe.

---

# 66. Command Discovery Announcements

In Beginner or Training Mode, QUILL can occasionally teach related commands.

Example:

> You used Find. Press F3 for next result.

Or:

> You selected text. Press Ctrl+C to copy or Shift+Arrow to extend selection.

Settings:

* Enable command discovery.
* Only in Beginner.
* Stop after N times.
* Never repeat dismissed tips.
* Reset tips.

This makes QUILL feel like a teacher.

---

# 67. “Do Not Say This Again”

For any optional tip or repeated guidance, allow:

> Do not say this again.

Command:

* `QUILL key + Delete`: do not say this tip again.

This gives users control over teaching behavior.

---

# 68. Per-Announcement Suppression

Users should be able to suppress a specific announcement.

Example:

After QUILL says something annoying:

* `QUILL key + Shift+Minus`: make this specific announcement quieter.

QUILL asks:

> Suppress this exact announcement, this verb, or this category?

Options:

* This exact message.
* This verb.
* This category.
* Cancel.

This is powerful, but should be under Advanced or confirmation-driven.

---

# 69. Announcement Labels

Each announcement could have internal labels.

Examples:

* navigation
* selection
* repeated
* boundary
* error
* warning
* markdown
* code
* search
* progress
* clipboard

Labels enable:

* Filtering history.
* Applying rules.
* Bulk editing.
* Explanation.
* Golden tests.
* Category settings.

---

# 70. “What Will This Change?” Confirmation

Before applying a big change, QUILL should summarize.

Example:

> This will set 18 navigation verbs to Expert and suppress routine movement confirmations. Continue?

For QVP:

> This pack will add 12 templates and apply none automatically.

For reset:

> This will remove 7 custom verb overrides and 2 chord overrides.

This prevents surprises.

---

# 71. Better Defaults for Experts

Expert should not merely be “less.”

It should be smarter.

Expert should prioritize:

* Position changes.
* Boundaries.
* Errors.
* Search results.
* Selection size.
* Mode changes.
* Operation completion.

Expert should suppress:

* Routine success confirmations.
* Obvious repeated context.
* Teaching hints.
* Long prose.

This distinction matters.

---

# 72. Better Defaults for Beginners

Beginner should not merely be “more.”

It should be educational.

Beginner should include:

* Context.
* Next action hints.
* Recovery hints.
* Meaning of sounds.
* Meaning of modes.
* Where settings can be changed.
* Clear plain-language errors.

But it should still use repetition collapse to avoid becoming exhausting.

---

# 73. Human-Friendly Names Everywhere

Avoid internal labels in the UI unless in advanced mode.

Use:

* “Say less during repeated commands”
* “Keep errors loud”
* “Use braille-friendly short messages”
* “Let me hear that again”
* “Explain why QUILL said this”
* “Preview before saving”
* “Restore safe defaults”

Instead of exposing only:

* `repetition_collapse`
* `error_priority`
* `braille_template`
* `history_replay`
* `trace_explain`
* `validation_mode`

Advanced mode can show internal IDs.

---

# 74. “Copy Debug Summary”

From “Why did QUILL say that?” provide:

> Copy debug summary

It should copy a clean support-ready report.

Example:

```text
QUILL Verbosity Debug Summary
Verb: nav.next_print_page
Trigger: Ctrl+Page Down
Profile: Expert
Channels: speech, braille, visual
Template source: QVP KellyFord Concise
Speech: Page 7 of 87
Braille: p7/87
Suppressed: running_head, line
Quiet Mode: off
Meeting Mode: off
```

This is great for bug reports.

---

# 75. “Report This Announcement”

Optional future integration:

> Report this announcement

It creates a local issue template or copies a GitHub-ready report.

Include:

* Debug summary.
* QUILL version.
* Profile.
* Verb.
* Template source.
* Expected behavior field.
* Actual behavior field.

No automatic upload required.

---

# 76. Documentation From Settings

Each setting should have:

* Plain-language description.
* Example.
* Recommended users.
* Default value.
* Related settings.

The UI can expose this through F1 or Help.

This makes the advanced system learnable.

---

# 77. Default Reset Granularity

Reset should be granular.

Options:

* Reset current control.
* Reset current verb.
* Reset current category.
* Reset current profile.
* Reset all custom templates.
* Reset all QVP packs.
* Reset all verbosity settings.
* Reset everything except user templates.
* Reset everything except QVP installs.

Granular reset makes users less afraid.

---

# 78. Settings Export Preview

Before exporting a profile, show what is included.

Options:

* Include user templates.
* Include QVP references.
* Include QVP contents.
* Include per-verb overrides.
* Include per-chord overrides.
* Include local tuning data.
* Include mastery data.
* Exclude history.
* Exclude private document rules.

This gives control and privacy.

---

# 79. Import Conflict Wizard

When importing a profile, handle conflicts accessibly.

Examples:

* Same template name.
* Same profile name.
* Missing QVP.
* Unsupported QUILL version.
* Unknown token.
* Chord no longer exists.

Offer:

* Rename imported item.
* Replace existing.
* Keep both.
* Skip.
* Cancel import.

Announce each conflict clearly.

---

# 80. “Try Without Applying”

For QVPs, recipes, and imported profiles, allow:

> Try temporarily

This applies settings for the current session only.

Then:

> Keep these settings?

Options:

* Keep.
* Revert.
* Save as new profile.

This encourages experimentation.

---

# 81. Session Profiles

Sometimes users want temporary settings.

Examples:

* “For this meeting only.”
* “For this file only.”
* “Until QUILL closes.”
* “For the next hour.”
* “Until I turn it off.”

Add session-scoped verbosity changes.

This is useful for Meeting Mode, training, demos, and one-off workflows.

---

# 82. Time-Based Quiet Hours

The original plan put Quiet Hours scheduler out of scope. It can remain later, but design hooks should exist.

Settings:

* Enable scheduled quiet hours.
* Start time.
* End time.
* Days.
* Use Meeting Safe profile.
* Allow errors through.
* Speak reminder before entering.
* Undo with Ctrl+Shift+Z.

This could be v0.7.x, but the architecture should allow it.

---

# 83. Focus Mode

Focus Mode is slightly different from Quiet Mode.

Focus Mode could reduce everything except:

* Errors
* Save failures
* Search results
* Explicit user-requested status

Useful for writing.

Command:

* `QUILL key + F`: Focus Mode toggle, if no conflict.

This could be a recipe built on the same engine.

---

# 84. Review Mode

Review Mode could increase structural announcements.

Useful for proofreading, Markdown review, compare, and accessibility checking.

It may announce:

* Heading levels.
* List nesting.
* Link text.
* Image alt text.
* Table position.
* Extra spaces.
* Repeated words.
* Unicode oddities.
* Formatting markers.

This aligns with QUILL’s broader document quality mission.

---

# 85. “Readability / Accessibility Verbosity”

Future GLOW/QUILL alignment could include announcements for document quality.

Examples:

> Heading level skipped from 2 to 4.

> Link text says click here.

> Image missing alt text.

> Table may need headers.

These should have their own verbosity category so users can control how much guidance they receive.

---

# 86. Microcopy Style Settings

Some users prefer different announcement language.

Settings:

* Friendly
* Professional
* Minimal
* Technical
* Teaching

Example:

Friendly:

> All set. Your file is saved.

Professional:

> File saved.

Technical:

> Save completed: verbosity.md, UTF-8.

This is not just verbosity; it is tone.

QVP packs could also define microcopy style.

---

# 87. “Use My Words” Custom Labels

Allow users to rename certain spoken labels.

Examples:

* Say “chapter” instead of “running head.”
* Say “page” instead of “print page.”
* Say “quiet” instead of “silenced.”
* Say “mark” instead of “bookmark.”

This is advanced, but it helps users personalize QUILL.

---

# 88. Abbreviation Dictionary for Announcements

Add an optional abbreviation layer.

Examples:

* “column” → “col”
* “selection” → “sel”
* “modified” → “mod”
* “heading” → “hdg”
* “paragraph” → “para”

Separate dictionaries for:

* Speech
* Braille
* Visual status

This supports compact output without requiring every template to be rewritten.

---

# 89. Language and Localization Readiness

Design announcement strings so they can be localized.

Requirements:

* Avoid concatenating untranslatable fragments.
* Token templates should support localization.
* QVP metadata should declare language.
* Built-in templates should be localizable.
* Date/time filters should be locale-aware.
* Pluralization should be locale-aware where possible.

This matters if QUILL becomes international.

---

# 90. Accessibility Testing Assistant Mode

A future testing mode could speak more diagnostic information.

Example:

> Button has accessible name Save. Role button. Enabled.

For QUILL UI development, this could help contributors verify accessibility.

This is advanced and probably not default, but it fits QUILL’s mission.

---

# 91. Developer “Trace Verbosity”

Developers should be able to enable trace output.

Settings:

* Log every verb fired.
* Log suppressed announcements.
* Log channel routing.
* Log template chosen.
* Log token derivation failure.
* Log QVP source.
* Log timing.
* Log screen reader handoff.

This should be separate from user Announcement History.

---

# 92. Performance Knobs

For very large files or rapid navigation, QUILL should stay responsive.

Settings/engine behavior:

* Drop stale routine messages.
* Limit token derivation cost.
* Cache expensive token values.
* Avoid blocking UI thread.
* Use async where safe.
* Never block typing for speech.
* Time out expensive preview render.

Performance should be part of the design.

---

# 93. Status Badges

Status bar badges should be consistent.

Possible badges:

* `[Q]` Quiet
* `[M]` Meeting
* `[F]` Focus
* `[R]` Review
* `[B]` Braille-first
* `[T]` Training
* `[P]` Private document
* `[H]` History enabled

Badges are sighted supplementary indicators. They must always have accessible equivalents.

---

# 94. Braille Status Cell

If possible, create a compact status string optimized for braille:

Example:

```text
Q off | M off | Expert | l14 c3 | mod
```

Or compact:

```text
Exp l14 c3 mod
```

Users could choose status order.

---

# 95. “Command Echo”

Some users like hearing the command they invoked.

Settings:

* Speak command name.
* Speak shortcut.
* Speak result only.
* Speak both command and result.
* Speak command only in Training Mode.
* Suppress command echo in Expert.

Example:

> Ctrl+S, Save file. Saved.

Or Expert:

> Saved.

---

# 96. “Before and After” Announcements

For actions that transform text, QUILL could optionally speak before/after summaries.

Examples:

* Case conversion.
* Trim whitespace.
* Sort lines.
* Format document.
* Replace all.
* Markdown conversion.

Example:

> Converted 12 lines to title case.

Details on demand can expose before/after examples.

---

# 97. Destructive Action Warnings

Verbosity should include special handling for destructive actions.

Examples:

* Delete file.
* Replace all.
* Clear document.
* Close unsaved file.
* Reset settings.
* Uninstall QVP.
* Bulk apply template.

Settings:

* Always confirm destructive actions.
* Speak full consequence in Beginner.
* Speak concise warning in Expert.
* Require typed confirmation for high-risk actions.

---

# 98. “Undo Available” Announcements

After actions that can be undone, QUILL may announce undo availability.

Beginner:

> Replaced 12 occurrences. Press Ctrl+Z to undo.

Expert:

> Replaced 12. Undo available.

Settings:

* Speak undo hints in Beginner.
* Suppress undo hints in Expert.
* Always speak undo after destructive bulk changes.

---

# 99. Multi-Monitor / Presentation Safety

For users presenting or teaching, Meeting Mode could include presentation safety.

Settings:

* Suppress private file paths.
* Suppress clipboard contents.
* Suppress selected text.
* Speak only structural summaries.
* Disable history storage during presentation.
* Hide private status fields.

This helps during workshops and screen sharing.

---

# 100. Final Recommendation

Add these ideas as optional expansion sections to the 0.7.0 plan, but do not expose all knobs at once.

The highest-value additions to consider for 0.7.0 are:

1. Searchable verbosity settings.
2. Announcement budget and repetition collapse.
3. Screen reader handoff mode.
4. Typing echo and indentation controls.
5. Selection and clipboard verbosity knobs.
6. Search result verbosity knobs.
7. Where Am I command.
8. Speak Status Bar command.
9. Braille-specific knobs.
10. Details on Demand.
11. QVP preview/diff before install.
12. Privacy controls for history and traces.
13. Import conflict wizard.
14. Try Without Applying.
15. Temporary verbosity boost.

These features would make QUILL feel truly screen-reader-first, not merely accessible.

They preserve the core philosophy:

> QUILL should meet users where they are, let them work the way they want, and always give them a safe way back.
