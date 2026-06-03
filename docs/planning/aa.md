# Research: integrating Accessibility Agents (`s:\code\agents`) into QUILL

Status: research proposal for review. Nothing here is approved or built. If
accepted, this becomes a new tier inserted after Tier 3 (GLOW), pushing the
current Tiers 4, 5, and 6 down to 5, 6, and 7. A bookmark is recorded in
`ROADMAP.md` so the decision is not lost.

This document evaluates the `s:\code\agents` repository (the Community Access
"Accessibility Agents" project) and proposes a concrete, QUILL-shaped way to
adopt the parts that fit, while being honest about the parts that do not.

## 1. What the project is

Accessibility Agents is an MIT-licensed, open-source ecosystem of about 80
specialized AI agents plus a Node.js MCP server, organized into teams (web,
document, GitHub workflow, developer tools, standards, and orchestrators). Its
premise is that LLMs drop accessibility context by default, so it packages
accessibility expertise as agents, skills, instructions, and scanning tools that
run across five host platforms: Claude Code, GitHub Copilot, Gemini CLI, Codex
CLI, and a standalone MCP server.

Key facts that shape integration:

- License: MIT (Copyright 2026 Taylor Arndt). Permissive; compatible with QUILL.
- The agents themselves are Markdown/YAML/TOML prompt definitions meant to run on
  external LLMs (Claude, Copilot, Gemini). That conflicts with QUILL's
  local-first, no-silent-network rule unless gated behind explicit consent.
- The MCP server is Node.js. It exposes 24 scanning tools over MCP (stdio or HTTP
  on localhost:3100), several of which are pure local scanners.
- It already contains a "GLOW bridge" (`glow_audit_document`, `glow_fix_document`,
  `glow_convert_document`, `glow_generate_report`, `glow_health_check`), so the
  project and QUILL's Tier 3 GLOW engine are designed to interoperate, not
  compete.
- It ships a `wxpython-specialist`, a `desktop-a11y-specialist`, and a
  `desktop-a11y-testing-coach` agent — desktop, Windows-UIA, and NVDA/JAWS/Narrator
  knowledge directly relevant to QUILL's own development.

## 2. Honest fit assessment

Most of the project is built for web developers and CI pipelines, not for a
local-first desktop writing app. The table separates what realistically fits
QUILL from what does not.

| Component | Fits QUILL? | Why |
| --- | --- | --- |
| MCP server document scanners (Office, PDF, EPUB, Markdown) | Partial | Useful as an optional, local audit backend, but overlaps GLOW (Tier 3). Adopt only where additive. |
| MCP axe-core and Playwright web scanners | Yes | QUILL authors and exports HTML; axe-core/Playwright audit that live markup, which GLOW does not cover. Clean additive value. See Workstream E. |
| GLOW bridge MCP tools | Yes (inverted) | Instead of QUILL calling them, QUILL can expose its own GLOW engine the way the bridge expects, so the wider ecosystem can audit through QUILL. |
| `wxpython-specialist`, `desktop-a11y-specialist`, `desktop-a11y-testing-coach` agents | Yes | Read-only knowledge sources for QUILL's own contributors; can seed QUILL's repo instructions and testing docs. |
| The 80-agent Copilot/Claude/Gemini/Codex packs | No | They run on external LLMs and target web/GitHub workflows; not a runtime feature of a desktop app. |
| VS Code extension | No | QUILL is not a VS Code surface. |
| GitHub Action | Repo-only | Could guard the QUILL repo's own docs/sample-document accessibility in CI, but is not part of the shipped app. |
| Go CLI installers | No | Platform setup for the agents project itself. |

## 3. The core tension to resolve first

QUILL's non-negotiables are local-first operation, no silent network calls, and
explicit per-action consent before any document content leaves the machine. The
Accessibility Agents that add the most "magic" (the LLM-driven specialists) are
inherently networked. Therefore any agent-backed capability in QUILL must:

- be a feature behind `FeatureManager` (FLAG-1), off by default;
- reuse QUILL's existing consented AI provider layer (AI-13 and the connection
  error taxonomy already built), never a second parallel network path;
- pass the GATE-9 no-silent-network egress audit, with every outbound call
  reviewed and announced;
- degrade gracefully to the fully local GLOW engine when AI is off.

The local MCP scanners and the desktop-knowledge agents do not have this tension
and are the safe first steps.

## 4. Proposed integration shape (if approved)

The work splits into four workstreams, ordered from lowest risk and highest
certainty to highest ambition. These would become the backlog IDs of the new
tier (proposed prefix `AX-` for "accessibility agents").

### Workstream A: adopt the desktop-accessibility knowledge (no runtime change)

- Bring the `wxpython-specialist`, `desktop-a11y-specialist`, and
  `desktop-a11y-testing-coach` guidance into QUILL's own repository memory and
  contributor instructions, attributed under MIT, as a curated distillation (not
  a wholesale copy).
- Outcome: QUILL contributors get the community's wxPython and Windows-UIA and
  screen-reader testing patterns without any network or runtime dependency.
- Risk: none. Pure documentation. This can happen even if the rest is declined.

### Workstream B: a local accessibility-audit backend via the MCP server

- Treat the Accessibility Agents MCP server as an optional, locally spawned audit
  backend for the structured formats QUILL reads (DOCX, PPTX, XLSX, PDF, EPUB,
  Markdown), behind a new feature id (for example `core.ax_audit`), off by
  default.
- QUILL talks to it over stdio MCP from a small Python client in `core` (UI
  agnostic), spawning the Node process only on demand and only for local files.
- The findings are normalized into the same finding shape GLOW-3 already defines,
  so the existing navigable, screen-reader-pageable report surface renders them
  with no new UI.
- Honesty: this overlaps GLOW. The rule is that the MCP backend is only adopted
  where it is genuinely additive to GLOW (for example a format or check GLOW does
  not cover), and the report always names which engine produced each finding
  (consistent with GLOW-6).
- Dependency reality: this adds an optional Node.js runtime. It must be a clearly
  optional extra (like the `glow` extra), never a hard dependency, with a clean
  "backend unavailable" path and an announced reason.

### Workstream C: expose QUILL's GLOW engine the way the bridge expects

- The agents project already defines a GLOW bridge contract. Rather than QUILL
  consuming it, QUILL can present its Tier 3 GLOW capability through the same
  contract so the broader Accessibility Agents ecosystem can audit and fix
  through QUILL's engine.
- This is the cleanest division of labor: one shared accessibility engine
  (`quill-glow-core`, per Tier 3), surfaced to both QUILL's in-editor reports and
  any MCP client.
- Gated by the same GLOW consent rules (GLOW-7) and the no-silent-network audit.

### Workstream D: consented, agent-assisted remediation (most ambitious)

- For fixes that genuinely need an LLM (for example drafting alt text or plain
  language rewrites), reuse the agent prompts as the instruction layer on top of
  QUILL's own consented AI provider, never the agents' external LLM paths.
- Every such action is explicit, announced, reviewable (apply-and-undo, matching
  AI-7), and off by default.
- This is where the "agent team that will not let accessibility slide" idea meets
  QUILL's Accessibility agent (AGENT-1) flagship; the two should share one
  surface, not build two.

### Workstream E: axe-core / web accessibility check on authored and exported HTML

This is a strong, concrete fit that the rest of this proposal hinted at but is
worth calling out on its own, because QUILL is not only a plain-text editor: it
reads and writes HTML through `quill/io`, it has a browser preview surface, and
GLOW-5 will add accessible HTML export. So the HTML a user authors or is about to
publish is real web content that an axe-core check applies to directly.

- What it does: run an axe-core (WCAG 2.2 AA) audit over the current HTML
  document, the exported HTML, or a selection, and present the violations in the
  same navigable, screen-reader-pageable findings surface GLOW-3 defines (rule id,
  impact, the offending element, a plain-language explanation, and a one-key jump
  to the location in the editor).
- How it runs, honoring local-first: the agents project's MCP server already
  bundles axe-core and Playwright and exposes `run_axe_scan`,
  `run_playwright_keyboard_scan`, `run_playwright_contrast_scan`, and
  `run_playwright_state_scan`. QUILL spawns that local MCP backend on demand
  (the same Node process as Workstream B), feeds it a local file or a
  `file://` URL for the rendered HTML, and never touches the network. There is no
  remote service and no document content leaves the machine.
- Two depths, user's choice:
  - Static check: axe-core run against the HTML source or a headless render of
    it. Fast, covers structure, ARIA, contrast, labels, headings, link text,
    landmarks, and the common WCAG failures. This is the default.
  - Behavioral check: the Playwright scanners add keyboard-traversal,
    dynamic-state, and runtime-contrast passes for HTML with interactivity. This
    is heavier and opt-in.
- Where it surfaces: a Tools command ("Check web accessibility (axe-core)"), the
  QUILL key, and — for export — an optional pre-publish gate on GLOW-5 accessible
  HTML export so a user can choose to be warned before shipping inaccessible
  markup. It also slots cleanly into the WATCH-2 action registry so a watched
  folder of HTML files is audited automatically.
- Relationship to GLOW: complementary, not duplicative. GLOW's strength is
  document formats (DOCX, PPTX, XLSX, PDF, EPUB) and QUILL's own text-level
  checks; axe-core is the established engine for live HTML/DOM accessibility,
  which GLOW does not run. The findings surface names which engine produced each
  result (consistent with GLOW-6), so the user always knows whether a finding came
  from GLOW, QUILL, or axe-core.
- Guardrails: behind its own feature id (for example `core.ax_web_audit`), off by
  default, no hard Node.js dependency, a clean "axe-core backend unavailable"
  path with an announced reason, and registered in the GATE-9 egress audit even
  though the scan is local (so the no-silent-network promise is provably kept).
- Honest caveat to keep in the product: axe-core, like all automated tooling,
  catches roughly a third to a half of real issues. The surface should repeat the
  project's own warning that automated checks are a starting point, not a
  substitute for testing with NVDA, JAWS, and keyboard-only navigation.

#### The wider Web Accessibility team (beyond axe-core)

axe-core and the Playwright passes are the engine, but the project's Web
Accessibility team is mostly a set of LLM-driven specialist agents that explain
and remediate rather than just flag. They are the natural "explain and fix"
layer on top of the static scan, and they matter to QUILL because the HTML a user
authors or exports is exactly their domain. The relevant specialists:

- `aria-specialist` — ARIA roles, states, properties, and widget patterns
  (the First Rule of ARIA, allowed children, deprecated roles).
- `keyboard-navigator` — tab order, focus management, focus restoration,
  keyboard shortcuts.
- `contrast-master` — colour contrast, dark mode, focus-indicator visibility.
- `forms-specialist` — label association, error identification, validation
  messages, multi-step flows.
- `modal-specialist` — dialog focus trapping, escape behaviour, focus
  restoration.
- `live-region-controller` — dynamic announcements (toasts, loading states,
  ARIA live politeness).
- `alt-text-headings` — alt text for images and SVGs, heading hierarchy,
  landmarks.
- `tables-data-specialist` — data-table markup, scope, captions, complex-table
  descriptions.
- `link-checker` — ambiguous or repeated link text and link purpose.
- `i18n-accessibility` — language tagging, RTL, multilingual content.
- `web-issue-fixer` and `playwright-verifier` — apply a fix and then re-run the
  behavioural scan to confirm it actually resolved.

How these fit QUILL, honestly:

- They are prompt-defined agents that run on an LLM, so in QUILL they are not a
  separate runtime. They become the instruction layer on top of QUILL's own
  consented AI provider (the same rule as Workstream D), turning a raw axe-core
  violation into a plain-language explanation and a reviewable, apply-and-undo
  fix in the editor. A contrast finding is explained by `contrast-master`; a
  missing label is fixed by `forms-specialist`; a bad heading order is repaired
  by `alt-text-headings`.
- The split of labour is clean: the static scanners (axe-core, Playwright) find
  and locate the issue with zero network and zero AI; the specialist agents,
  only when the user turns AI on and consents, explain and propose the fix; the
  `web-issue-fixer`/`playwright-verifier` loop re-scans to prove the fix worked.
  A user who keeps AI off still gets the full local scan and the navigable
  findings list — they just do not get the AI-written explanations and fixes.
- This is the web counterpart of QUILL's Accessibility agent (AGENT-1). The two
  should share one findings-and-remediation surface, with these specialists as
  the web-specific knowledge the agent draws on, never a parallel UI.

What we would still leave out: the team's framework-specific agents (React, Vue,
Svelte, Tailwind, Next.js, design-system auditors, web components, email and
mobile) target code a writing app does not produce, so they stay out of QUILL.
QUILL adopts only the document-level HTML specialists that apply to authored and
exported pages.

#### Running axe-core with no Node.js, no network, and no visible UI

The question of whether axe-core needs Node.js is important, and the answer is
no. axe-core is a single self-contained JavaScript file with zero runtime
dependencies — Node.js is only one of several ways to host it. QUILL already
embeds the engine that hosts it best: the accessible Edge WebView2 component
(`wx-accessible-webview`, already used by the assistant panel and the web-form
helper). The plan is therefore to run axe-core inside QUILL's own process, not
through an external Node backend.

How it works, concretely:

- Vendor the single minified `axe.min.js` (about half a megabyte, MIT/MPL-2.0)
  into QUILL as a bundled asset. It ships inside the app; there is no download
  and no per-scan bandwidth at all.
- Create the WebView2 control off-screen and never attach it to a visible
  window, so the scan is a silent review: the user sees no browser, no flash, no
  pop-up. The control is created, used, and destroyed entirely in the background.
- Load the HTML to audit into that off-screen control from a local
  `file://`/temp source (the current document's HTML, the exported HTML, or a
  selection). Nothing leaves the machine.
- Inject the bundled `axe.min.js` and call `axe.run(...)` via the WebView's
  script-execution path (the same `RunScript`/`ExecuteScript` bridge QUILL
  already uses), then read back the JSON result.
- Normalize that JSON into the shared finding shape (GLOW-3) so the results are
  announced and reviewed through the existing surface — or, in pure-silent mode,
  simply counted and logged for a watch action with no surface at all.

Why this is the right fit for QUILL:

- No Node.js runtime, no npm, no separate process, and no MCP server are required
  for the static axe-core scan. WebView2 is already a QUILL dependency on
  Windows, so the only thing added is a vendored JS file. (The optional Node MCP
  backend from Workstream B remains relevant only for the heavier Playwright
  behavioural passes; the everyday HTML check does not need it.)
- It is genuinely zero-bandwidth after install: the engine is bundled, the scan
  is local, and the GATE-9 egress audit can prove no outbound call exists.
- It is silent by construction: an off-screen WebView means there is no UI to
  show, which is exactly the behaviour we want for a background or watch-driven
  review.

On a pure-Python alternative (no WebView at all): there is no faithful pure-Python
port of axe-core's full WCAG ruleset. The existing Python packages
(`axe-core-python`, `axe-selenium-python`) only drive axe-core through Selenium,
which means a real browser plus a webdriver — heavier and less self-contained
than QUILL's own WebView2, not lighter. Pure-Python HTML linters exist but apply
a small, different rule set and are not axe-core. So the recommended path is the
bundled-`axe.min.js`-in-the-offscreen-WebView approach above: it is the
lowest-bandwidth, no-Node, no-UI option and it reuses infrastructure QUILL
already ships. A small pure-Python structural pre-check (headings, alt text, link
text, lang) can run as a fast first pass for environments where WebView2 is
unavailable, with axe-core as the authoritative engine when it is present.

The silent-review default: unless the user explicitly opens the findings surface,
the axe-core check runs with no visible UI — created off-screen, executed,
results captured, control torn down — so it is safe to run as a background
pre-publish check or a WATCH-2 action over a folder of HTML without ever
interrupting the writer. The navigable findings dialog (GLOW-3) is shown only on
demand.

## 5. What we would deliberately not do

- Not bundle the 80-agent multi-platform packs into the shipped app.
- Not add the VS Code extension, Gemini, or Codex surfaces.
- Not introduce a second AI network path or a second settings or consent store.
- Not make Node.js a hard runtime dependency of QUILL.
- Not duplicate GLOW; where they overlap, GLOW is the engine and the agents are
  additive guidance or an optional alternate backend.

## 6. Open questions for review

1. Is the optional Node.js MCP backend (Workstreams B and E) acceptable, or
   should QUILL stay pure-Python and take only Workstreams A and C? Note that the
   axe-core web check (E) is the single most concrete user-facing win and the main
   reason to accept the optional Node backend.
2. Should agent-assisted remediation (Workstream D) be folded entirely into the
   existing Accessibility agent (AGENT-1) flagship rather than a separate tier?
3. Do we want QUILL to be a GLOW provider to the ecosystem (Workstream C), or keep
   the engine in-app only?
4. Sequencing: this tier is proposed to land after Tier 3 (GLOW) because B, C, and
   D all build on the shared GLOW engine. Confirm that ordering.

## 7. Proposed tier placement

If approved, insert as the new Tier 4, immediately after GLOW:

- Current Tier 4 (structural health and performance) becomes Tier 5.
- Current Tier 5 (BITS Whisperer transcription) becomes Tier 6.
- Current Tier 6 (documentation) becomes Tier 7.

Rationale: the valuable QUILL-shaped pieces (B, C, D) depend on the shared GLOW
engine from Tier 3, and documentation should still land last so it describes a
product that is already GLOW-native, agent-assisted, and transcription-capable.

## 8. Bottom line

The realistic value to QUILL is narrower than the project's breadth suggests, but
real: a curated desktop-accessibility knowledge base for contributors
(Workstream A, zero risk), an optional additive local audit backend that reuses
the existing report surface (Workstream B), a clean way to share one GLOW engine
with the wider ecosystem (Workstream C), a consented path to agent-assisted
remediation that folds into QUILL's own Accessibility agent (Workstream D), and an
axe-core / Playwright web accessibility check on the HTML a user authors or
exports (Workstream E) that runs entirely locally and fills the one gap GLOW does
not cover. The MIT license, the bundled axe-core engine, and the existing GLOW
bridge make this feasible; QUILL's local-first and no-silent-network rules define
the guardrails. Everything else in the project is for web teams and CI, and we
leave it there.
