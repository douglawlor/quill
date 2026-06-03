# Learning from Pi: deriving the magic for QUILL

Status: research note for review. Nothing here is approved or built. Pi itself is
not adoptable by QUILL (it is ~93% TypeScript, ships as npm packages, runs on
Node.js, and is a coding agent with a redraw-heavy TUI that fights screen
readers). But its *design* is excellent, and several of its ideas translate
directly into QUILL's accessible, local-first writing context. This note
separates the transferable magic from the parts we leave behind.

Source: `earendil-works/pi` (MIT), `pi.dev/docs/latest`. Identified as the Pi
Agent Harness: a minimal terminal coding agent plus a unified LLM API, agent
runtime, and TUI library.

## Why Pi is worth learning from

Pi's stated philosophy is "stay small at the core, extend everything else."
Around that core it has solved, unusually well, four problems QUILL also has:
managing AI providers, managing long conversations, carrying durable context,
and integrating from another language. Those solutions are the magic.

## The magic, mapped to QUILL

### 1. Subscription login, not just API keys (the biggest accessibility win)

Pi lets a user authenticate with an existing Claude Pro/Max, ChatGPT Plus/Pro, or
GitHub Copilot subscription via an interactive `/login` flow, storing credentials
locally — no API key required. For a blind or low-vision user, "sign in with the
subscription you already have" is dramatically more accessible than "create an
API key, copy this 51-character secret, paste it without seeing it."

For QUILL: add a guided, fully keyboard-and-screen-reader login that can use an
existing subscription where the provider supports it, alongside the current API
key path. Must honor QUILL's rules: credentials in DPAPI, explicit consent, no
silent network, and the GATE-9 egress audit. This is the single most user-facing
piece of magic to derive. Maps to AI-13 and the existing connection settings.

### 2. Conversation sessions that branch, fork, and resume

Pi treats the conversation as a durable, navigable tree: sessions auto-save,
`-c` continues the latest, `-r` browses past ones, and `/fork` and `/clone`
branch the conversation so a user can try two approaches without losing state.

For QUILL this is genuinely category-defining for *writing*, not just coding: a
writer could branch a draft ("rewrite this section two different ways and let me
compare"), keep both, and resume later, all by keyboard with announced state.
QUILL already has Save Session/Open Session and an assistant transcript; this
elevates them into a first-class, branchable, resumable writing-with-AI history.
The accessible surface is a navigable list/tree of session branches, each
announced, with one-key jump and compare. Candidate new backlog cluster.

### 3. Durable context/instruction files the AI cannot drop

Pi loads `AGENTS.md`/`CLAUDE.md` at startup (a global one plus a per-project one)
so the model always honors project-specific instructions, with `/reload` to pick
up edits live. The magic is that the guidance never falls out of context.

For QUILL: a per-document or per-project "writing instructions" file (house
style, tone, words to avoid, audience) that the assistant always honors and that
the user can edit and reload. This pairs naturally with QUILL's existing Train
Writing Style feature — train the voice, and pin the rules. Honest, visible, and
user-owned. Candidate backlog item.

### 4. A language-agnostic integration boundary (RPC / JSON event mode)

This is the most important architectural lesson and it solves the exact problem
that blocked direct adoption. Pi exposes three non-interactive surfaces: a
one-shot `-p` mode (pipe text or files in, get a result), a `--mode json`
structured event stream, and a `--mode rpc` that talks JSONL over stdin/stdout so
*any language* can drive it. Pi is TypeScript, yet a Python app can integrate it
cleanly over stdio without sharing a runtime.

For QUILL: this is the template for how QUILL should consume *any* external agent
engine — Pi, the Accessibility Agents MCP server (see `aa.md`), or future tools —
without language lock-in: spawn a local subprocess, speak JSONL/MCP over stdio,
keep it off by default, consent-gated, and covered by the egress audit. Adopt the
*pattern*, not the package. This directly de-risks the `aa.md` Workstream B/E
question about non-Python backends.

### 5. Model switching with speed/cost tiers, mid-session

Pi switches models mid-session (`/model`, Ctrl+L) and cycles "thinking levels"
(Shift+Tab): a fast cheap model to explore, a smarter one to finalize.

For QUILL: let the user pick a fast/local model for quick edits and a stronger
one for a careful rewrite, switchable mid-task with an announced change, surfaced
in the existing AI model panel. Local-first means the fast tier can be an
on-device model. Small, high-value refinement to the AI model surface.

### 6. Compaction for long sessions

Pi compacts context and summarizes branches so long sessions stay within the
window without losing the thread.

For QUILL: a long writing-and-editing session with the assistant should compact
gracefully and announce when it does, rather than silently truncating. A quietly
important reliability feature for real, long-form work.

### 7. Inline command output, with an opt-out from context

Pi's `!cmd` runs a command and feeds the output to the model; `!!cmd` runs it
without adding the output to the context window — explicit control over what the
model sees.

For QUILL the transferable idea is the *control*, not shell access: when a user
pulls in external text (a file, a quote, a snippet), they should be able to
choose whether it enters the AI's context. A small honesty-and-privacy
refinement, not a shell feature.

### 8. Supply-chain hardening as a posture

Pi pins exact dependency versions, sets a minimum release age to avoid same-day
supply-chain attacks, installs with `--ignore-scripts`, and treats the lockfile
as ground truth.

For QUILL: this matches the existing GATE/SEC ladder and is worth mirroring for
any new optional Node-based backend we add (per `aa.md`): pin it, age-gate it,
no install scripts, audited.

## What we deliberately do not take from Pi

- The TypeScript/Node codebase and npm packages — wrong runtime for QUILL.
- The coding-agent identity (read/write/edit/bash on a repo) — QUILL is a writing
  app for end users, not a dev tool.
- The differential-rendering TUI — dynamic terminal redraws are hostile to
  NVDA/JAWS/Narrator; QUILL stays with stock, accessible controls.
- `pi-ai` as a dependency — QUILL already has a consented multi-provider layer;
  we study Pi's API design, we do not import it.

## The one-line takeaway

Pi's reusable magic for QUILL is four ideas: subscription login instead of
pasted API keys, branchable/resumable AI sessions, durable per-document writing
instructions, and a language-agnostic stdio/JSON integration boundary for
external engines. The first three are user-facing delight; the fourth is the
architecture that makes both `aa.md` (Accessibility Agents) and any future
external engine safe to adopt from a Python app. We derive the patterns; we do
not take the code.
