# QUILL 0.7.0 Comprehensive Verbosity System Plan

## Purpose

QUILL 0.7.0 should ship a complete, screen-reader-first Verbosity System as a core product pillar.

This system is not merely a preference for “more speech” or “less speech.” It is the communication layer between QUILL and the user. For screen reader users, spoken, braille, sound, and status announcements are not secondary polish. They are the interface.

The goal of QUILL 0.7.0 is to make QUILL feel calm, understandable, powerful, recoverable, personal, community-extensible, and trustworthy.

This document merges the existing Verbosity Rebuild Plan with additional product recommendations intended to make the feature more magical while preserving the practical implementation detail needed to build it.

---

# 1. Product Thesis

## Verbosity is the interface

For a blind or screen reader user, every announcement is part of the application’s user interface.

A good announcement builds confidence.

A noisy announcement slows the user down.

A missing announcement creates uncertainty.

A confusing announcement breaks trust.

QUILL should treat announcements with the same seriousness that visual-first editors give to layout, menus, color, animation, whitespace, toolbar design, and visual feedback.

The Verbosity System should give the user direct control over:

* What QUILL says.
* How much QUILL says.
* Where QUILL says it.
* Whether QUILL uses speech, braille, sound, visual status, or a combination.
* Why QUILL said something.
* How to replay something that was missed.
* How to safely customize announcements.
* How to share announcement styles with the community.
* How to recover when customization creates confusion.

QUILL 0.7.0 should establish this as a foundation, not a later afterthought.

---

# 2. Release Target

## Version target

Target release: QUILL 0.7.0

The earlier plan referenced 0.7.1 as a patch rebuild target, but for this comprehensive product direction, the complete Verbosity System should be treated as part of the 0.7.0 milestone.

All version references, QVP minimum version gates, release notes, installer versioning, and documentation should target 0.7.0 unless the implementation team intentionally splits the feature after planning.

---

# 3. Why This Belongs in 0.7.0

The Verbosity System affects every major user experience in QUILL:

* Opening files.
* Saving files.
* Moving by line, word, character, page, section, heading, and document boundary.
* Selecting text.
* Searching.
* Replacing.
* Editing Markdown.
* Editing code.
* Reviewing documents.
* Working in quiet environments.
* Using braille.
* Using Keyboard Manager.
* Installing community customizations.
* Debugging user feedback.
* Testing accessibility expectations.
* Supporting future BRF and transcription workflows.

A partial verbosity preference would create long-term technical debt.

A complete announcement architecture gives QUILL a durable foundation for:

* Screen-reader-first editing.
* Braille workflows.
* Keyboard-driven power use.
* Beginner onboarding.
* Expert quiet operation.
* Community packs.
* Testing and support.
* Future Quillin extension points.
* Future task-aware workflows.

QUILL should not bolt this on later. QUILL should build the communication layer now.

---

# 4. Core Design Commitments

The 0.7.0 Verbosity System should follow these commitments:

1. Screen reader users are the primary audience.
2. Visual feedback is supplementary, not primary.
3. Speech, braille, sound, and visual status are separate channels.
4. Users can choose simple presets or deeply customize behavior.
5. Users can recover missed announcements.
6. Users can understand why an announcement happened.
7. Users can safely reset broken customization.
8. Templates are data-only and safe.
9. Community packs are possible without executing code.
10. Every announcement behavior should be testable.
11. Every UI path should be keyboard accessible.
12. Every control should expose name, role, and value.
13. Color must never be the only signal.
14. Expert users should not be slowed down.
15. Beginners should be taught as they work.

---

# 5. Locked Design Decisions

## Profile UX

Use a hybrid profile model.

QUILL provides four ladder presets:

* Beginner
* Normal
* Expert
* Quiet

Each preset populates four channel checkboxes:

* Speech
* Braille
* Sound
* Visual

The user may edit the channel checkboxes after selecting a preset.

When channel edits diverge from the selected preset, QUILL should expose a “Modified” state.

Switching profiles should announce that the preset has reset the channel mix.

Example:

> Switched to Expert. Channels reset to Expert defaults: speech on, braille on, sound errors only, visual on. Your previous edits were discarded. Press Ctrl+S to keep them as a Custom profile.

## Channels

Channels:

* Speech
* Braille
* Sound
* Visual

Visual is the accessibility floor and should always remain on.

Visual should be exposed as disabled but checked, with an accessible name such as:

> Visual status bar, always on, cannot be disabled.

## Sound Channel

Sound should be independent and per-event aware.

The system should support:

* Master sound channel.
* Per-event sound gating.
* Sound off during Quiet Mode.
* Sound error-only in Expert mode.
* Sound character varying by profile.
* Friendly Beginner chimes.
* Subtle Expert clicks.
* Quiet-hours style when sound is off.

## Validation Timing

Default validation mode should be On-button.

Validation should speak when the user explicitly chooses Validate or Preview.

Validation should not constantly interrupt the user while editing.

Available modes:

* Live
* On-focus
* On-button

Default:

* On-button

## Audio Defaults

Only validation-spoken feedback should be on by default.

The following should be opt-in:

* Auto-play on editor open.
* Palette token audio.
* Focus-out read-back.

## Token Editor Shape

Use two modes:

* Simple
* Advanced

Simple should be the default.

Simple uses a sentence-builder ListBox.

Advanced uses a raw multiline TextCtrl.

Both views share backing data.

Use a wx.RadioBox for switching modes rather than a wx.Notebook, because a notebook implies separate pages rather than two views of the same data.

## Per-Verb Default UX

“Use default” should be the headline.

Custom per-verb behavior is opt-in.

Per-row dropdowns should show `—` when using default.

Rendered and syntax preview should appear only when customized.

## Templates Library

Version 1 should support full CRUD:

* Save
* Apply
* Delete
* Rename

Use a flat wx.ListBox or ListCtrl for browsing.

Use per-row dropdown apply.

Do not include drag-and-drop in 0.7.0.

## Library Cross-Verb Behavior

When applying a template to a verb that does not support all referenced tokens, QUILL should auto-filter invalid tokens and warn.

Example:

> Applied template Concise. Removed 2 tokens because this verb does not track them: cell, region.

## Per-Verb Table

Use master/detail with filter, not a grid.

Left side:

* Virtual wx.ListCtrl, report style, virtual mode.

Right side:

* Detail pane for selected verb.

Filter:

* wx.SearchCtrl.
* Matches verb name and namespace.

This is more screen-reader friendly than a complex grid.

## QVP Files

QVP files should be JSON-only `.qvp.json`.

They should be:

* Data-only.
* Schema-validated.
* No executable code.
* No signing in v1.
* Namespaced by author.
* Minimum QUILL version gated.
* Manually installed from the Library tab.

Required metadata:

* Name
* Author
* Description
* Version
* License

Optional metadata:

* Preview text
* Tags
* Dependencies

---

# 6. Profile Model

## Built-in presets

| Preset   | Speech | Braille | Sound       | Visual | Purpose                                     |
| -------- | ------ | ------- | ----------- | ------ | ------------------------------------------- |
| Beginner | On     | On      | On          | On     | Verbose hints, teaching style, full context |
| Normal   | On     | On      | On          | On     | Concise but complete default                |
| Expert   | On     | On      | Errors only | On     | Drops routine confirmations, keeps errors   |
| Quiet    | Off    | On      | Off         | On     | Braille and status bar without speech/sound |

## Beginner

Beginner should be warm, complete, and instructional.

It should include:

* Full context.
* Helpful hints.
* Confirmation of important state changes.
* Explanatory announcements for new concepts.
* More complete navigation descriptions.
* Safer error messages.

## Normal

Normal should be the default.

It should be:

* Concise.
* Complete.
* Predictable.
* Suitable for most users.
* Not overly chatty.

## Expert

Expert should be fast.

It should:

* Suppress routine confirmations.
* Preserve errors.
* Preserve warnings.
* Use subtle sound only for important events.
* Avoid repeating obvious context.
* Support rapid movement and editing.

## Quiet

Quiet should be safe silence.

It should:

* Turn off speech.
* Turn off sound.
* Preserve braille.
* Preserve visual status.
* Clearly announce when it is entered and exited.
* Be easy to undo.

---

# 7. Channel System

## Channel enum

Recommended core model:

```python
class Channel(enum.Flag):
    SPEECH = enum.auto()
    BRAILLE = enum.auto()
    SOUND = enum.auto()
    VISUAL = enum.auto()
```

Visual is always on.

## Routing

Every announcement should route through the VerbosityEngine.

The engine should decide:

* Which verb fired.
* Which profile is active.
* Which channels are active.
* Whether Quiet Mode applies.
* Whether Meeting Mode applies.
* Whether per-verb overrides apply.
* Whether per-chord overrides apply.
* Whether a QVP template applies.
* Whether an announcement should be suppressed.
* Whether sound should play.
* What output should go to speech.
* What output should go to braille.
* What output should go to status bar.
* What sound event should occur.

There should not be multiple competing announcement systems.

Legacy `_announce()` calls should route through a legacy verb path until converted.

---

# 8. Sound Design

Sound should reinforce meaning without creating noise.

## Per-event sound gating

The sound channel should have:

* Master enabled/disabled state.
* Per-event enabled/disabled state.
* Error-only setting for Expert.
* Profile-based sound character.
* QVP-provided sound voice metadata in the future.

## Sound character by profile

Suggested sound themes:

* Beginner: friendly chime pack.
* Normal: modest confirmation tones.
* Expert: subtle clicks.
* Quiet: no sound.

## Speech pause before announce

The engine should insert approximately 200ms of silence before each speech announcement to reduce truncation by screen readers.

This pause belongs inside the engine so callers do not have to implement it repeatedly.

---

# 9. Quiet Mode

## Commands

Recommended:

* `Ctrl+Shift+Q`: toggle Quiet Mode.
* `QUILL key + Q`: toggle Quiet Mode.

## Entry announcement

When Quiet Mode turns on:

> Quiet mode on. Speech and sound silenced. Press Ctrl+Shift+Q to turn off.

## Exit announcement

When Quiet Mode turns off:

> Quiet mode off. Speech restored.

## Status

Show a `[Q]` badge in the status bar.

The badge is supplementary.

The spoken announcement is canonical.

## Behavior

Quiet Mode should route announcements to:

* Braille
* Visual status

Quiet Mode should suppress:

* Speech
* Sound

Unless an emergency or blocking error requires an assertive recovery path.

---

# 10. Meeting Mode

## Command

Recommended:

* `Ctrl+Shift+B`: toggle Meeting Mode.

## Entry announcement

> Meeting mode on. Quiet hours engaged until you press Ctrl+Shift+B again.

## Exit announcement

> Meeting mode off. Normal announcements restored.

## Status

Show `[M]` in the status bar.

## Purpose

Meeting Mode is for:

* Live calls.
* Classrooms.
* Presentations.
* Workshops.
* Screen sharing.
* Shared spaces.
* Situations where the user needs reduced audio output.

Meeting Mode should be distinct from Quiet Mode because the user may want specific meeting-safe behaviors rather than total speech suppression.

---

# 11. Quiet Undo

## Command

Recommended:

* `Ctrl+Shift+Z`: undo quiet-hours entry or restore prior verbosity state.

## Announcement

> Quiet hours reverted. Speech restored.

This is a safety feature. Users should never feel trapped in a silent state.

---

# 12. Token System

The token system is the centerpiece of customizable announcements.

## TokenSpec

Each verb declares supported tokens.

Recommended model:

```python
@dataclass(frozen=True)
class TokenSpec:
    name: str
    type: Literal["str", "int", "float", "bool", "datetime", "duration"]
    description: str
    derive: Callable[[Context], Any]
    filters: tuple[str, ...] = ()
```

## Template syntax

Supported syntax:

```text
{name}
${filter:name}
${filter:arg:name}
```

Examples:

```text
Line {line}, column {column}
Page {print_page} of {print_page_total}
${truncate:20:file_name}
${ordinal:heading_level} heading
```

## Allowed filters

Engine-implemented filters:

* `upper`
* `lower`
* `title`
* `ordinal`
* `pad:N`
* `pluralize`
* `singular`
* `duration_human`
* `date_long`
* `date_short`
* `time`
* `truncate:N`

Custom filters should not be supported in 0.7.0.

This prevents injection and keeps QVP files data-only.

---

# 13. Template Validation

Validation should be strict and safe.

## Strict allowlist

Every token used in a template must match the selected verb’s TokenSpec list.

Unknown tokens are errors.

Templates with unknown tokens cannot be saved.

## Type checking

Filters should be checked against token types.

Examples:

* `pad:N` requires numeric or integer-compatible tokens.
* `date_long` requires datetime tokens.
* `duration_human` requires duration tokens.

## Filter allowlist per token

Each token declares allowed filters.

If a filter is not allowed for a token, QUILL should warn or error depending on severity.

## Validation messages

Spoken summary:

> Validation: 3 tokens, 1 warning, 0 errors.

Detailed review field:

```text
[X] {garbage} → unknown token
[!] {pad:4:line} → pad not allowed for line
[OK] {column} → 14
```

## Save behavior

Save should be disabled when the template contains blocking errors.

The Save button should have a tooltip:

> 1 unknown token — fix to save.

When focus lands on the disabled Save button, screen reader users should hear:

> Save disabled, 1 error.

## Validation command

Inside token editor:

* `Ctrl+T`: Validate

## Preview command

Inside token editor:

* `Ctrl+Shift+P`: Preview Announcement

If preview is already playing:

> Preview already playing.

Use a 250ms debounce on preview.

---

# 14. Data Ordering

Some users do not need a full custom template. They only need to reorder the data QUILL announces.

## DataOrder model

```python
@dataclass(frozen=True)
class DataOrder:
    verb_id: str
    fields: tuple[str, ...]
    separator: str = ", "
```

## Editor

Use a wx.ListBox with:

* Move Up
* Move Down
* Reset
* Preview

## Template precedence

If both a custom template and a custom data order exist for a verb, the template wins.

---

# 15. Verb Registry

Every announcement should map to a verb.

## VerbSpec

Each verb should include:

* Verb ID.
* Namespace.
* Human-readable name.
* Firing context.
* Default profile behavior.
* Supported tokens.
* Default template.
* Default data order.
* Description.
* Whether it is routine, warning, error, progress, navigation, editing, or document state.

## Example verbs

Navigation:

* `nav.next_line`
* `nav.previous_line`
* `nav.next_word`
* `nav.previous_word`
* `nav.next_character`
* `nav.previous_character`
* `nav.document_start`
* `nav.document_end`
* `nav.next_print_page`
* `nav.previous_print_page`

Editing:

* `edit.insert_text`
* `edit.delete_character`
* `edit.delete_word`
* `edit.select_word_right`
* `edit.select_line`
* `edit.unquote_lines`

Document:

* `doc.open`
* `doc.save`
* `doc.save_as`
* `doc.modified`
* `doc.read_only`
* `doc.encoding_changed`

Search:

* `search.find`
* `search.find_next`
* `search.find_previous`
* `search.no_results`
* `search.replace`
* `search.replace_all`

System:

* `system.error`
* `system.warning`
* `system.info`
* `system.progress`
* `system.operation_complete`

Legacy:

* `_legacy`

---

# 16. Per-Verb Preferences

## UI pattern

Use master/detail, not a grid.

Left side:

* Filter bar.
* Namespace choice.
* Virtual ListCtrl of verbs.

Right side:

* Selected verb details.
* Current profile behavior.
* Channel overrides.
* Style choice.
* Template preview.
* Data order summary.
* Edit button.
* Reset button.
* Library template dropdown.

## Verb row announcement

Each row should announce:

> Next Print Page, fired by Ctrl+Page Down, currently Beginner.

This avoids forcing screen reader users to cross-reference Keyboard Manager.

## Reset behavior

When resetting a verb:

> Reset Next Print Page to profile default; custom template cleared, ladder cleared.

---

# 17. Verbosity Preferences UI

Recommended structure:

```text
VerbosityPrefsPanel
├── ProfilePicker
├── ChannelMixBox
├── MasteryBox
├── ValidationModeBox
├── SafeModeBox
├── PreviewLabButton
├── AnnouncementHistoryButton
├── CollapsibleVerbTable
│   └── VerbTablePanel
│       ├── FilterBar
│       └── MasterSplit
│           ├── VerbList
│           └── VerbDetailPanel
└── StatusLine
```

## Initial focus

Initial focus should land on the Filter SearchCtrl because power users often come to this panel to find a specific verb.

Profile picker should be second in tab order.

## Status line

Use a status/live region style approach.

Name:

```text
verbosity_status
```

Use polite announcements for nonblocking updates and assertive behavior for blocking errors.

---

# 18. Token Editor UI

Recommended structure:

```text
VerbosityTokenEditor
├── EditorPane
│   ├── ModeBar
│   ├── ReviewField
│   ├── SimpleView
│   ├── AdvancedView
│   └── ButtonRow
└── Palette
    ├── Position
    ├── Count
    ├── Document
    ├── Time
    └── LibrarySection
```

## Simple mode

Simple mode should use a sentence-builder ListBox.

Users can arrow through fragments and swap pieces.

Enter should activate a fragment replacement.

Important wxPython note:

Use `EVT_CHAR_HOOK` at the dialog level for Enter when ListBox has focus.

Do not rely only on `EVT_KEY_DOWN` on the ListBox because NVDA may swallow WM_KEYDOWN before the ListBox sees it.

## Advanced mode

Advanced mode uses raw template syntax in a multiline TextCtrl.

The token palette inserts tokens at the caret.

## Review field

Review field should be read-only and multiline.

First line:

* Rendered announcement.

Second line:

* Raw template.

Use separate styles so rendered text and raw template do not bleed styles into each other.

## Hotkeys

Inside the modal editor:

* `Ctrl+T`: Validate.
* `Ctrl+Shift+P`: Preview.
* `Ctrl+R`: Read assembled template aloud.
* `Ctrl+S`: Save as template.
* `Escape`: Cancel.

These should be handled with dialog-level `EVT_CHAR_HOOK`, not global keymap.

---

# 19. Templates Library

## Surfaces

The Templates Library should appear in two places:

1. Library tab in Verbosity Preferences.
2. Per-row dropdown in the VerbDetailPanel.

## Library tab

The Library tab should support:

* Search/filter.
* Browse built-in templates.
* Browse user templates.
* Browse QVP-installed templates.
* Save.
* Apply.
* Delete.
* Rename.
* Install QVP from file.
* Uninstall QVP pack.
* Preview template.
* Explain applicability.

## Per-row dropdown

Options:

* Built-in Default
* Built-in Concise
* Built-in Verbose
* Separator
* User templates
* QVP-installed templates
* Browse library…

Use wx.Choice, not wx.ComboBox.

## Library item announcement

Each item should announce:

> Template name, last modified date, source User or QVP-installed, verb count, applies to this verb yes or no.

## Built-in templates

Read-only.

## User templates

Editable and deletable.

## QVP templates

Read-only.

Removing QVP templates should require uninstalling the whole pack.

---

# 20. QVP Files

QVP means QUILL Verbosity Pack.

File extension:

```text
.qvp.json
```

## QVP requirements

QVP files should be:

* JSON-only.
* Data-only.
* No code.
* No Python execution.
* Schema validated.
* Namespaced.
* Minimum QUILL version gated.
* Manually installed in v1.
* Read-only once installed unless copied as user template.

## Example QVP

```json
{
  "schema_version": 1,
  "kind": "quill-verbosity-pack",
  "min_quill_version": "0.7.0",
  "pack": {
    "name": "Audio Descriptive Concise",
    "author": "kellyford",
    "description": "Concise templates optimized for audio description workflows.",
    "version": "1.0.0",
    "license": "MIT",
    "tags": ["screen-reader", "concise", "audio-descriptive"],
    "preview_text": "Now reading page 7, line 14.",
    "depends": ["kellyford.audio-descriptive-core"]
  },
  "templates": [
    {
      "id": "kellyford.audio-descriptive-concise",
      "name": "Concise",
      "applies_to": ["nav.*"],
      "template": "{running_head}, page {print_page} of {print_page_total}.",
      "speech_template": "{running_head}, page {print_page} of {print_page_total}.",
      "braille_template": "{running_head} p{print_page}/{print_page_total}",
      "visual_template": "{running_head}, page {print_page} of {print_page_total}",
      "data_order": ["running_head", "print_page", "print_page_total"],
      "separator": ", ",
      "preview": "Chapter 2, page 7 of 87."
    }
  ]
}
```

## Required fields

Top-level:

* `schema_version`
* `kind`
* `min_quill_version`
* `pack`
* `templates`

Pack metadata:

* `name`
* `author`
* `description`
* `version`
* `license`

Template metadata:

* `id`
* `name`
* `applies_to`
* `template`

Optional fields:

* `tags`
* `preview_text`
* `depends`
* `data_order`
* `separator`
* `preview`
* `speech_template`
* `braille_template`
* `visual_template`
* `sound_event`

---

# 21. QVP Install Flow

Library tab button:

> Install QVP from file…

Flow:

1. Open file picker.
2. Validate JSON.
3. Validate schema.
4. Check `kind`.
5. Check `min_quill_version`.
6. Check required metadata.
7. Check template IDs.
8. Check namespace collisions.
9. Resolve dependencies if supported.
10. Validate templates against known verbs where possible.
11. Install pack.
12. Announce result.

Example spoken sequence:

> Validating pack.
> Minimum QUILL version 0.7.0, you have 0.7.0. OK.
> Pack installed. 2 templates added. Author: Kelly Ford.

## Dependency behavior

If dependencies are listed but missing:

> This pack depends on kellyford.audio-descriptive-core, which is not installed.

The user should be able to cancel or proceed only if dependencies are optional.

---

# 22. Profile Preview

When a user changes profiles, QUILL should preview the practical difference.

## Behavior

Replay the last three announcements using the new profile.

## Command

Recommended:

* `Ctrl+Shift+Enter`: replay profile preview when profile picker has focus.

## Purpose

Users should not have to guess what Beginner, Normal, Expert, and Quiet mean.

They should hear the difference.

---

# 23. Preview Lab

QUILL 0.7.0 should include a Preview Lab.

The Preview Lab lets users test profiles, templates, channel mixes, and QVP packs against canned scenarios.

## Scenarios

Recommended built-in scenarios:

* Plain text editing.
* Long document navigation.
* Markdown document.
* Code file.
* Search results.
* Replace operation.
* Save file.
* Open file.
* Error state.
* Warning state.
* Selection movement.
* Print page navigation.
* Status/progress update.
* Future BRF/braille workflow sample.

## Output

For each scenario, show or expose:

* Speech output.
* Braille output.
* Visual status output.
* Sound event.
* Suppressed content.
* Active profile.
* Active template.
* Active channel mix.

## Value

Preview Lab makes the system understandable before the user commits changes.

It also gives QVP authors a way to test their packs.

---

# 24. Announcement History

Announcement History should be included in 0.7.0.

This should not be deferred.

For screen reader users, spoken output disappears quickly. Announcement History gives users recovery, confidence, debugging power, and copyability.

## Commands

Recommended:

* `QUILL key + H`: repeat last announcement.
* `QUILL key + Shift+H`: open Announcement History.
* `QUILL key + Ctrl+H`: copy last announcement to clipboard.

## History entries

Each announcement history item should store:

* Timestamp.
* Verb ID.
* Human-readable verb name.
* Trigger/chord.
* Active profile.
* Channel mix.
* Speech output.
* Braille output.
* Visual output.
* Sound event.
* Template source.
* Token values.
* Suppressed content.
* Quiet/Meeting state.
* Per-verb override state.
* Per-chord override state.
* QVP source if applicable.
* Severity: routine, info, warning, error.

## History UI

Announcement History should support:

* Review recent announcements.
* Replay selected announcement.
* Copy selected announcement.
* Explain selected announcement.
* Search/filter.
* Filter by verb.
* Filter by channel.
* Filter by profile.
* Filter warnings/errors.
* Compare selected announcement across profiles.
* Clear history.
* Privacy-safe behavior.

## Privacy

Announcement History may contain document text.

Add settings:

* Enable/disable history.
* Maximum number of entries.
* Clear on exit.
* Exclude selected document content.
* Clear now.

Default can keep a limited local history, but the user should have control.

---

# 25. “Why Did QUILL Say That?”

QUILL 0.7.0 should include an explanation layer.

For any recent announcement, the user should be able to ask why it happened.

## Explanation should include

* Verb fired.
* Triggering command or chord.
* Active profile.
* Active channel mix.
* Template source.
* Token values used.
* Output per channel.
* Suppressed content.
* Whether Quiet Mode affected it.
* Whether Meeting Mode affected it.
* Whether a per-verb override applied.
* Whether a per-chord override applied.
* Whether a QVP template applied.
* Whether sound was suppressed.
* Whether routine confirmation was hidden.
* Whether validation warnings existed.

## Example

```text
Verb: nav.next_print_page
Trigger: Ctrl+Page Down
Profile: Expert
Channels: speech, braille, visual
Template source: QVP KellyFord Concise
Speech output: Page 7 of 87
Braille output: p7/87
Visual output: Page 7 of 87
Suppressed: Running head hidden by Expert profile
```

## Value

This builds trust.

It also helps:

* Support.
* Bug reports.
* Contributors.
* QVP authors.
* Testers.
* Accessibility reviews.

---

# 26. Too Much / Too Little / Just Right

QUILL should include lightweight local tuning feedback.

## Commands

Recommended:

* `QUILL key + Minus`: That was too much.
* `QUILL key + Plus`: I needed more detail.
* `QUILL key + 0`: That was just right.

## Behavior

Store local preference signals per verb.

After repeated feedback, QUILL may suggest a change.

Example:

> You often reduce detail for selection movement. Switch Select Word Right to Expert?

This should be:

* Local only.
* No telemetry.
* No cloud required.
* User-controlled.
* Reversible.
* Non-pushy.

---

# 27. Mastery-Based Step Down

QUILL should support mastery detection.

When the user repeatedly succeeds with a command, QUILL can offer to reduce verbosity for that verb.

## Behavior

* Track successful repeated use per verb.
* When threshold is crossed, offer step-down.
* Use a 10-second timeout.
* Speak countdown at 3 seconds.
* Let user accept or ignore.
* Do not repeatedly nag.

## Example

> You seem comfortable with Select Word Right. Switch this command to Expert? Press Enter to accept or Escape to keep current verbosity.

## Controls

Settings should include:

* Enable mastery suggestions.
* Mastery threshold.
* Reset mastery data.
* Per-verb disable.

---

# 28. Channel-Specific Templates

Speech and braille should not be forced to use the same text.

## Need

Speech can be natural and descriptive.

Braille often needs compact output.

Visual status may need a short summary.

Sound may need an event ID.

## Recommended template fields

* `template`
* `speech_template`
* `braille_template`
* `visual_template`
* `sound_event`

## Example

Speech:

```text
Now reading Chapter 2. Print page 7 of 87. Line 14.
```

Braille:

```text
Ch2 p7/87 l14
```

Visual:

```text
Chapter 2, page 7 of 87, line 14
```

Even if the first UI exposes only global templates, the 0.7.0 schema and engine should support channel-specific template fields to avoid future breaking changes.

---

# 29. Safe Mode and Reset

Powerful customization needs safe recovery.

QUILL 0.7.0 should include Verbosity Safe Mode.

## Safe Mode should support

* Temporarily disable all custom verbosity.
* Reset this verb.
* Reset this chord.
* Reset this profile.
* Disable all QVP packs.
* Restore built-in verbosity.
* Export current settings before reset.
* Start QUILL with built-in verbosity only.

## UI

Add a Safe Mode section in Verbosity Preferences.

Suggested actions:

* Disable custom verbosity temporarily.
* Reset selected verb.
* Reset selected chord.
* Disable QVP packs.
* Restore built-in defaults.
* Export before reset.

## Purpose

Users should never fear customization.

They should always have a clear path back to a known good state.

---

# 30. Import and Export

QVP files are for template packs.

QUILL should also support full verbosity profile import/export.

## Suggested extension

```text
.quill-verbosity-profile.json
```

## Export may include

* Custom profiles.
* Channel choices.
* Per-verb overrides.
* Per-chord overrides.
* User templates.
* Validation mode.
* Quiet Mode preferences.
* Meeting Mode preferences.
* Mastery settings.
* Too Much / Too Little preferences.
* Preview Lab sample overrides if applicable.

## Use cases

* Jeff’s quiet meeting setup.
* Kelly’s screen-reader optimized setup.
* Beginner classroom setup.
* Expert authoring setup.
* Braille-first editing setup.
* Markdown authoring setup.
* Training lab setup.

## Security

Profile imports should be data-only and schema-validated.

They should not run code.

---

# 31. Task-Aware Profiles

The architecture should support task-aware profiles.

## Possible task profiles

* Writing mode.
* Coding mode.
* Markdown mode.
* Review mode.
* Braille/transcription mode.
* Presentation mode.
* Meeting mode.
* Training mode.

## Initial 0.7.0 behavior

0.7.0 does not need to force automatic switching.

It should support optional suggestions.

Example:

> Markdown file detected. Use Markdown verbosity profile?

Automatic switching should be:

* Off by default.
* User-approved.
* Reversible.
* Per file type configurable.

---

# 32. First-Run Verbosity Tour

Setup Wizard should include a friendly Verbosity page.

Instead of a raw settings panel, ask:

> How much should QUILL talk while you learn?

Suggested choices:

* Teach me as I go.
* Keep me informed.
* Stay out of my way.
* Be silent except for braille/status.

After choosing, QUILL should preview:

* Moving by line.
* Saving a file.
* Encountering an error.
* Navigating by page.
* Performing a repeated command.

This helps users understand the consequences of the profile selection immediately.

---

# 33. Keyboard Manager Integration

The Keyboard Manager should include a Verbosity tab.

Each chord should expose a verbosity choice.

## Options

* Profile default
* Quiet
* Beginner
* Normal
* Expert
* Custom for this chord…

## Example table

| Chord            | Action            | Verbosity              |
| ---------------- | ----------------- | ---------------------- |
| Ctrl+Home        | Document Start    | Profile default        |
| Ctrl+Shift+Right | Select Word Right | Quiet                  |
| Ctrl+G           | Go to Line        | Custom for this chord… |

## Mini-editor

Choosing “Custom for this chord…” opens a mini-editor scoped only to the verbs fired by that chord.

Entry announcement:

> Ctrl+Shift+Right fires Select Word Right. Mini-editor will scope to this verb.

## Grouping

Group chords by category:

* Navigation
* Editing
* Document
* Search
* System

Support `Ctrl+1..N` to jump between groups.

---

# 34. Hotkey Plan

Recommended global hotkeys:

| Command             | Feature                                 |
| ------------------- | --------------------------------------- |
| Ctrl+Shift+Q        | Toggle Quiet Mode                       |
| QUILL key + Q       | Toggle Quiet Mode                       |
| Ctrl+Shift+B        | Toggle Meeting Mode                     |
| Ctrl+Shift+M        | Open Verbosity Preferences              |
| Ctrl+Shift+Z        | Undo quiet-hours/verbosity state change |
| QUILL key + H       | Repeat last announcement                |
| QUILL key + Shift+H | Open Announcement History               |
| QUILL key + Ctrl+H  | Copy last announcement                  |
| QUILL key + Minus   | Mark last announcement as too much      |
| QUILL key + Plus    | Mark last announcement as too little    |
| QUILL key + 0       | Mark last announcement as just right    |

Recommended token editor hotkeys:

| Command      | Feature                 |
| ------------ | ----------------------- |
| Ctrl+T       | Validate announcement   |
| Ctrl+Shift+P | Preview announcement    |
| Ctrl+R       | Read assembled template |
| Ctrl+S       | Save as template        |
| Escape       | Cancel/close            |

Recommended profile preview hotkey:

| Command          | Feature                |
| ---------------- | ---------------------- |
| Ctrl+Shift+Enter | Replay profile preview |

Conflict note:

If `Ctrl+Shift+Q` was previously used for unquote lines, move unquote lines to `Alt+Shift+Q`.

---

# 35. Storage

## Main settings

Add VerbositySettings to core settings.

Recommended fields:

* `current_profile`
* `custom_profiles`
* `channels_modified`
* `mastery_enabled`
* `mastery_threshold`
* `validation_mode`
* `quiet_mode`
* `meeting_mode`
* `quiet_hours_enabled`
* `verbosity_custom_overrides`
* `announcement_history_enabled`
* `announcement_history_limit`
* `announcement_history_clear_on_exit`
* `qvp_enabled_packs`
* `safe_mode_enabled`
* `task_profile_suggestions_enabled`

## Custom data file

Suggested file:

```text
verbosity_custom.json
```

Should include:

* User templates.
* Per-verb overrides.
* Per-chord overrides.
* Custom profiles.
* Data order overrides.
* Mastery state.
* Too much/too little preference signals.

Use atomic writes.

Reject invalid overrides on load with a nonblocking warning dialog.

---

# 36. Core Modules

Recommended new core package:

```text
quill/core/verbosity/
```

## New core files

* `__init__.py`
* `channels.py`
* `styles.py`
* `profiles.py`
* `tokens.py`
* `parser.py`
* `verbs.py`
* `registry.py`
* `data_order.py`
* `engine.py`
* `mastery.py`
* `quiet.py`
* `meeting.py`
* `storage.py`
* `schema.py`
* `preview.py`
* `qvp.py`
* `library.py`
* `history.py`
* `explain.py`
* `safe_mode.py`
* `import_export.py`
* `task_profiles.py`
* `feedback_tuning.py`

## Responsibilities

### channels.py

Defines Channel enum and helpers.

### styles.py

Defines verbosity style concepts.

### profiles.py

Defines built-in profiles and custom profile model.

### tokens.py

Defines TokenSpec, filters, type checks, and token helpers.

### parser.py

Parses templates and returns structured validation output.

### verbs.py

Defines VerbSpec and built-in verbs.

### registry.py

Central verb lookup and registration.

### data_order.py

Handles ordered token rendering.

### engine.py

Central routing engine for all announcements.

### mastery.py

Tracks mastery and step-down suggestions.

### quiet.py

Quiet Mode controller.

### meeting.py

Meeting Mode controller.

### storage.py

Reads/writes verbosity customization data.

### schema.py

JSON schema for settings, custom data, QVP, and profile import/export.

### preview.py

Renders sample announcements for preview.

### qvp.py

Loads, validates, installs, and uninstalls QVP files.

### library.py

Manages built-in, user, and QVP templates.

### history.py

Stores and retrieves recent announcements.

### explain.py

Generates “Why did QUILL say that?” traces.

### safe_mode.py

Disables custom verbosity and restores known good state.

### import_export.py

Handles full verbosity profile import/export.

### task_profiles.py

Supports task-aware profile suggestions.

### feedback_tuning.py

Stores local “too much / too little / just right” signals.

---

# 37. UI Modules

Recommended new UI files:

* `quill/ui/verbosity_prefs.py`
* `quill/ui/verbosity_token_editor.py`
* `quill/ui/verbosity_data_order.py`
* `quill/ui/verbosity_chord_editor.py`
* `quill/ui/verbosity_library.py`
* `quill/ui/verbosity_history.py`
* `quill/ui/verbosity_preview_lab.py`
* `quill/ui/verbosity_safe_mode.py`
* `quill/ui/verbosity_import_export.py`
* `quill/ui/about_dialog.py`

## verbosity_prefs.py

Embeddable Preferences panel and optional dialog.

## verbosity_token_editor.py

Simple and Advanced token editor.

## verbosity_data_order.py

Data order editor.

## verbosity_chord_editor.py

Mini-editor scoped to chord-fired verbs.

## verbosity_library.py

Templates Library and QVP install flow.

## verbosity_history.py

Announcement History viewer.

## verbosity_preview_lab.py

Scenario-based preview tool.

## verbosity_safe_mode.py

Recovery and reset UI.

## verbosity_import_export.py

Import/export UI for full verbosity profiles.

## about_dialog.py

Three-tab About dialog:

* Overview
* Dependencies
* Links

---

# 38. Files to Modify

## Core

* `quill/core/feature_command_map.py`
* `quill/core/keymap.py`
* `quill/core/settings.py`
* `quill/core/settings_specs.py`
* `quill/core/about_info.py`

## UI

* `quill/ui/main_frame.py`
* `quill/ui/main_frame_menu.py`
* `quill/ui/main_frame_quill_key.py`
* `quill/ui/main_frame_statusbar.py`
* `quill/ui/info_pages.py`
* `quill/ui/keyboard_manager_dialog.py`
* `quill/ui/setup_wizard_pages.py`

## Quillins

* `quill/quillins_bundled/doc-guardian/extension.py`

Add hook for Quillins to register custom verbs.

## Scripts

* `scripts/build_windows_distribution.py`

Include:

* `verbosity_custom.json`
* `qvps/*.qvp.json`
* exported verbosity profiles if needed

## Tooling

* `quill/tools/module_size_budgets.json`

Rebaseline after integration.

## Versioning

* `quill/__init__.py`
* `installer/quill.iss`

Set to 0.7.0.

---

# 39. Feature Commands to Register

Recommended feature commands:

* `feature.verbosity_prefs`
* `feature.quiet_mode_toggle`
* `feature.meeting_mode_toggle`
* `feature.undo_quiet_hours`
* `feature.about_dialog`
* `feature.validate_announcement`
* `feature.preview_announcement`
* `feature.replay_profile_preview`
* `feature.qvp_install`
* `feature.qvp_uninstall`
* `feature.announcement_history`
* `feature.repeat_last_announcement`
* `feature.copy_last_announcement`
* `feature.explain_last_announcement`
* `feature.verbosity_safe_mode`
* `feature.verbosity_reset_selected`
* `feature.verbosity_import`
* `feature.verbosity_export`
* `feature.feedback_too_much`
* `feature.feedback_too_little`
* `feature.feedback_just_right`
* `feature.preview_lab`

---

# 40. Accessibility Requirements

The system must be screen-reader-first.

## General

* Every dialog must have a useful initial focus.
* Every control must have an accessible name.
* Every interactive element must expose name, role, and value.
* Every button must have a real text label.
* No icon-only buttons.
* Every action must have a keyboard path.
* Tab order must be logical.
* Focus indicators must not be obscured.
* Color must not be the only signal.
* Shape prefixes should accompany validation states.
* No motion-only feedback.
* Plain language should be used throughout.
* Visual badges are supplementary.
* Spoken and braille output are primary.

## Live regions/status

* Nonblocking warnings: polite.
* Blocking errors: assertive.
* Status line should be named and discoverable.
* Validation should be reviewable without sight.

## Screen reader commitments

* Test with NVDA.
* Test with JAWS.
* Verify wx.CollapsiblePane behavior.
* Verify modal hotkeys.
* Verify ListBox Enter behavior.
* Verify disabled Save announcement.
* Verify status bar updates.
* Verify Announcement History workflow.
* Verify Quiet Mode recovery.
* Verify Meeting Mode recovery.

---

# 41. Testing Plan

## Core tests

* `tests/unit/core/test_verbosity.py`
* `tests/unit/core/test_verbosity_channels.py`
* `tests/unit/core/test_verbosity_profiles.py`
* `tests/unit/core/test_verbosity_tokens.py`
* `tests/unit/core/test_verbosity_filters.py`
* `tests/unit/core/test_verbosity_parser.py`
* `tests/unit/core/test_verbosity_data_order.py`
* `tests/unit/core/test_verbosity_preview.py`
* `tests/unit/core/test_verbosity_storage.py`
* `tests/unit/core/test_verbosity_qvp.py`
* `tests/unit/core/test_verbosity_library.py`
* `tests/unit/core/test_verbosity_mastery.py`
* `tests/unit/core/test_verbosity_quiet.py`
* `tests/unit/core/test_verbosity_meeting.py`
* `tests/unit/core/test_verbosity_history.py`
* `tests/unit/core/test_verbosity_explain.py`
* `tests/unit/core/test_verbosity_safe_mode.py`
* `tests/unit/core/test_verbosity_import_export.py`
* `tests/unit/core/test_verbosity_feedback_tuning.py`
* `tests/unit/core/test_verbosity_task_profiles.py`
* `tests/unit/core/test_about_info.py`

## UI tests

* `tests/unit/ui/test_verbosity_prefs.py`
* `tests/unit/ui/test_verbosity_token_editor.py`
* `tests/unit/ui/test_verbosity_data_order.py`
* `tests/unit/ui/test_verbosity_chord_editor.py`
* `tests/unit/ui/test_verbosity_library.py`
* `tests/unit/ui/test_verbosity_qvp_install.py`
* `tests/unit/ui/test_keyboard_manager_verbosity.py`
* `tests/unit/ui/test_quiet_mode.py`
* `tests/unit/ui/test_meeting_mode.py`
* `tests/unit/ui/test_verbosity_history.py`
* `tests/unit/ui/test_verbosity_preview_lab.py`
* `tests/unit/ui/test_verbosity_safe_mode.py`
* `tests/unit/ui/test_verbosity_import_export.py`
* `tests/unit/ui/test_info_pages.py`
* `tests/unit/ui/test_post_show_foreground.py`
* `tests/unit/ui/test_main_frame_quill_key.py`
* `tests/unit/core/test_quill_key_help.py`

## Script tests

* `tests/unit/scripts/test_build_windows_distribution.py`

---

# 42. Golden Announcement Tests

Add golden tests for announcement output.

Suggested location:

```text
tests/golden/verbosity/
```

Each test should define:

* Verb.
* Context.
* Profile.
* Channel mix.
* Template source.
* Expected speech.
* Expected braille.
* Expected visual.
* Expected sound.
* Expected suppressed content.
* Expected explanation trace.

## Example golden case

```json
{
  "name": "next_print_page_expert",
  "verb": "nav.next_print_page",
  "profile": "expert",
  "channels": ["speech", "braille", "visual"],
  "context": {
    "running_head": "Chapter 2",
    "print_page": 7,
    "print_page_total": 87,
    "line": 14
  },
  "expected": {
    "speech": "Page 7 of 87.",
    "braille": "p7/87",
    "visual": "Page 7 of 87",
    "sound": null,
    "suppressed": ["running_head", "line"]
  }
}
```

Golden tests protect user trust.

If a future refactor changes how QUILL speaks, tests should catch it.

---

# 43. Documentation Plan

Update:

* `docs/Product Requirement Documents and Specifications/QUILL-PRD.md`
* `docs/user guide/userguide.md`
* `docs/CONTROL_REFERENCE.md`
* `docs/release notes/release0.7.0.md`
* `CHANGELOG.md`
* Developer docs for verbs.
* Developer docs for tokens.
* Developer docs for QVP.
* Developer docs for announcement testing.

## User guide chapter

Include:

* What verbosity means.
* Choosing Beginner/Normal/Expert/Quiet.
* Quiet Mode.
* Meeting Mode.
* Announcement History.
* Why did QUILL say that?
* Simple token editor.
* Advanced token editor.
* Templates Library.
* QVP install.
* Keyboard Manager verbosity.
* Preview Lab.
* Safe Mode.
* Import/export.

## Developer docs

Include:

* How to register a verb.
* How to declare tokens.
* How to create safe templates.
* How to add filters.
* How to write golden announcement tests.
* How to create QVP packs.
* How to support channel-specific templates.
* How Quillins can register custom verbs.

---

# 44. Manual Smoke Test

Golden path:

1. Launch QUILL.
2. Open Preferences > Verbosity.
3. Verify four profiles appear: Beginner, Normal, Expert, Quiet.
4. Switch to Beginner.
5. Confirm announcements are verbose and full-context.
6. Switch to Expert.
7. Confirm routine confirmations are suppressed and errors still speak.
8. Edit a channel checkbox.
9. Confirm Modified state appears.
10. Switch profiles.
11. Confirm spoken reset announcement.
12. Type in the per-verb filter.
13. Confirm the list narrows.
14. Select a verb.
15. Confirm detail pane shows current override.
16. Open token editor.
17. Confirm Simple view is default.
18. Arrow through fragments.
19. Press Ctrl+R.
20. Confirm assembled template is read.
21. Switch to Advanced.
22. Insert `{column}` from palette.
23. Confirm review field shows rendered output.
24. Type `{garbage}`.
25. Confirm Save is disabled.
26. Press Ctrl+T.
27. Confirm validation is spoken.
28. Press Ctrl+Shift+P.
29. Confirm preview speaks and updates status.
30. Press Ctrl+Shift+Q.
31. Confirm Quiet Mode announcement and `[Q]` badge.
32. Press Ctrl+Shift+B.
33. Confirm Meeting Mode announcement and `[M]` badge.
34. Press Ctrl+Shift+Z.
35. Confirm quiet state undo.
36. Open Announcement History.
37. Replay last announcement.
38. Copy last announcement.
39. Use “Why did QUILL say that?”
40. Confirm explanation includes verb, trigger, profile, channels, template source, token values, and suppressed content.
41. Open Preview Lab.
42. Preview Beginner, Normal, Expert, and Quiet against the same scenario.
43. Save a custom template.
44. Confirm it appears in Library.
45. Install a sample QVP.
46. Confirm metadata is spoken.
47. Apply QVP template.
48. Confirm invalid cross-verb tokens are removed with warning.
49. Open Keyboard Manager.
50. Set a chord to Quiet.
51. Press that chord.
52. Confirm only that action is quiet.
53. Use Too Much / Too Little / Just Right feedback.
54. Trigger mastery threshold.
55. Confirm step-down suggestion.
56. Enable Safe Mode.
57. Confirm custom verbosity is disabled.
58. Disable Safe Mode.
59. Confirm custom behavior returns.
60. Export a verbosity profile.
61. Import it.
62. Confirm settings restore.
63. Open Help > About.
64. Confirm 3-tab dialog appears.
65. Run full test suite.

---

# 45. Verification Commands

Required verification:

```powershell
pytest -q
ruff check .
ruff format --check .
mypy quill\core quill\io
python -m quill.tools.quillin_lint quill\quillins_bundled --strict
```

Additional gates:

* Pre-commit hooks pass.
* Module size gate passes or is intentionally rebaselined after final wiring.
* Dialog inventory passes.
* Banned patterns pass.
* Network egress checks pass.
* Button contract passes.
* Golden announcement tests pass.
* Manual NVDA smoke test passes.
* Manual JAWS smoke test passes.

---

# 46. Order of Work

Recommended implementation order:

1. Core channels.
2. Profiles.
3. Styles.
4. TokenSpec.
5. Filters.
6. Parser.
7. Parser tests to high coverage before UI.
8. VerbSpec.
9. Verb registry.
10. Data order.
11. Preview renderer.
12. Engine.
13. Quiet Mode.
14. Meeting Mode.
15. Mastery.
16. Announcement History.
17. Explain trace system.
18. Safe Mode.
19. Feedback tuning.
20. QVP schema.
21. QVP loader/validator.
22. Library model.
23. Import/export.
24. Storage integration.
25. Settings integration.
26. Keymap integration.
27. Token editor UI.
28. Data order UI.
29. Verbosity Preferences UI.
30. Library UI.
31. QVP install UI.
32. Announcement History UI.
33. Preview Lab UI.
34. Safe Mode UI.
35. Chord mini-editor.
36. Keyboard Manager integration.
37. Main frame menu/status bar integration.
38. Setup Wizard integration.
39. About dialog.
40. Distribution script updates.
41. Documentation.
42. Release notes.
43. Version bump.
44. Full verification.
45. Manual screen reader smoke testing.
46. Rebaseline module size only after all wiring is complete.

---

# 47. Risks

## Parser risk

The token parser is the highest-risk module.

All safety, validation, QVP trust, and template rendering depend on it.

Mitigation:

* Parser tests first.
* High coverage before UI depends on it.
* Strict allowlist.
* No custom filters.
* No code execution.

## UI complexity risk

The preferences system could become too complex.

Mitigation:

* Master/detail UI.
* Search first.
* Simple mode default.
* Advanced mode available but not forced.
* Safe Mode visible.

## Sound annoyance risk

Sound could become noisy.

Mitigation:

* Per-event gating.
* Expert error-only sound.
* Quiet Mode.
* Meeting Mode.
* Sound defaults conservative.

## Silent failure risk

Users could accidentally silence needed feedback.

Mitigation:

* Visual always on.
* Braille preserved in Quiet.
* Safe Mode.
* Quiet Undo.
* Clear toggle announcements.
* Status badges.

## QVP trust risk

Community packs could be abused if they execute code.

Mitigation:

* JSON-only.
* Data-only.
* Schema validation.
* No custom filters.
* No scripting.
* No Python access.

## Module-size risk

Main frame files may grow.

Mitigation:

* Keep logic in dedicated modules.
* Rebaseline only after final wiring.
* Avoid moving engine logic into main_frame.py.

## Stash discipline risk

The original work was lost due to `git stash drop`.

Mitigation:

* Do not use git stash for this rebuild.
* Use a topic branch.
* Commit frequently.
* Use small checkpoints.
* Push remote backups.

## Accessibility regression risk

wx widgets may behave differently with NVDA, JAWS, or VoiceOver.

Mitigation:

* Test with NVDA and JAWS explicitly.
* Use real labels.
* Avoid grid-heavy UI.
* Use dialog-level key handling where needed.
* Verify focus behavior manually.

---

# 48. Out of Scope for 0.7.0 Unless Time Allows

The following can be designed for but not fully built in 0.7.0:

* QVP signing.
* QVP auto-update.
* QVP marketplace.
* Quillin Hub browsing.
* Drag-and-drop template application.
* Full automatic task switching.
* Advanced braille abbreviation logic.
* Quiet Hours scheduler.
* Cloud-synced verbosity profiles.
* AI-generated templates.
* Pack ratings/reviews.
* Visual screenshot-heavy documentation.

However, the architecture should not block these.

---

# 49. Non-Negotiables for 0.7.0

Do not cut:

1. Profile ladder.
2. Channel model.
3. Quiet Mode.
4. Meeting Mode.
5. Token parser.
6. Strict validation.
7. Simple and Advanced token editor.
8. Per-verb overrides.
9. Keyboard Manager integration.
10. Templates Library.
11. QVP JSON-only packs.
12. Announcement History.
13. Why did QUILL say that?
14. Safe Mode/reset.
15. Golden announcement tests.
16. Screen-reader-first accessibility commitments.

These define the system.

Without them, the feature becomes a preferences panel rather than a trusted announcement architecture.

---

# 50. Release Positioning

Suggested release framing:

> QUILL 0.7.0 introduces a complete screen-reader-first Verbosity System, giving users control over what QUILL says, where it says it, how much detail it provides, and how announcements can be reviewed, explained, customized, shared, and safely reset.

Suggested community framing:

> QUILL now meets you where you are. Whether you are learning, moving fast, working silently in a meeting, using braille, authoring documents, writing Markdown, reviewing code, or building your own community verbosity pack, QUILL gives you control over the communication layer of the editor.

Suggested accessibility framing:

> For screen reader users, verbosity is not decoration. It is the interface. QUILL 0.7.0 treats announcements as a first-class, testable, customizable, recoverable part of the product.

---

# 51. Success Criteria

QUILL 0.7.0 succeeds if:

* A beginner can choose Beginner mode and feel guided.
* A normal user can work without being overwhelmed.
* An expert can move quickly without routine chatter.
* A meeting participant can silence disruptive output.
* A braille user can keep meaningful output.
* A user can replay missed announcements.
* A user can ask why QUILL said something.
* A user can safely customize announcement wording.
* A user can install a community QVP pack.
* A user can recover from broken customization.
* A tester can verify announcement behavior with golden tests.
* A developer can add verbs without inventing a new announcement path.
* A Quillin author can register custom verbs safely.
* A support person can diagnose user reports from explanation traces.
* QUILL feels calm, intentional, trustworthy, and magical.

---

# 52. Final Statement

The QUILL 0.7.0 Verbosity System should be treated as a foundational product pillar.

This is not simply about changing how much the editor talks.

It is about building a trustworthy communication architecture for a screen-reader-first editor.

The complete system should include profiles, channels, quiet and meeting modes, tokenized templates, validation, preview, per-verb and per-chord overrides, QVP packs, announcement history, explanation traces, safe reset, local tuning, mastery suggestions, import/export, Preview Lab, and robust tests.

This is the kind of system that makes QUILL feel different from ordinary editors.

It gives users power without fear.

It gives beginners guidance.

It gives experts speed.

It gives braille users control.

It gives the community a way to contribute.

It gives testers something reliable to verify.

Most importantly, it gives screen reader users confidence that QUILL is communicating clearly, intentionally, and respectfully.

That is the magic of QUILL 0.7.0.
