# QUILL 1.0 — Pre-Release Code Review Issues

> **Status:** CRITICAL / HIGH / LOW / NIT / Magic all closed. 6 MEDIUM remain.
> All closed items documented in `CHANGELOG.md`.
> **Status legend:** ✅ FIXED · 🔵 Open · 🟡 Deferred (needs real Windows runtime)

---

## 1. Open issues — MEDIUM (6)

> M-1 through M-27 are closed except M-24, M-28, M-29, M-30, M-31, M-32 (UI lifecycle / A11Y).

### Tools and audit

#### M-24 — `tools/dialog_button_contract.py:34-35` — unbacked `affirmative_id` not audited
- **File / Category:** `quill/tools/dialog_button_contract.py:34-35` / A11Y
- **Symptom:** A `hardened_custom` dialog with `SetAffirmativeId(wx.ID_OK)` but no `wx.ID_OK` button silently ignores Enter. Blind users press Enter repeatedly with no feedback.
- **Suggested fix:** Extend the audit to verify every `apply_modal_ids` `affirmative_id` has a backing button or `CreateButtonSizer` flag.
- **Regression test:** `tests/unit/tools/test_dialog_button_contract.py::test_unbacked_affirmative_id_flagged`

### UI lifecycle and threading

#### M-28 — `ui/main_frame.py:4547` — crash recovery re-show loop leaks focus
- **File / Category:** `quill/ui/main_frame.py:4547` / A11Y
- **Symptom:** Each loop iteration calls `editor.SetFocus()` via `CallAfter`, so when the dialog reopens focus races between the editor and the dialog's primary control.
- **Suggested fix:** Track "in sub-loop" and skip `editor.SetFocus` between iterations.
- **Regression test:** `tests/unit/ui/test_main_frame.py::test_crash_recovery_loop_does_not_steal_focus`

#### M-29 — `ui/assistant_tools.py:143-156` — `Run Python` sandbox blocks UI
- **File / Category:** `quill/ui/assistant_tools.py:143-156` / UX, THREADING
- **Symptom:** Long-running sandbox scripts block the UI thread and freeze the screen reader.
- **Suggested fix:** Run sandbox on a worker thread; show progress; disable Apply until done.
- **Regression test:** `tests/unit/ui/test_assistant_tools.py::test_run_python_does_not_block_ui_thread`

#### M-30 — `ui/main_frame_browse.py:174` — prewarm thread not cancelled before restart
- **File / Category:** `quill/ui/main_frame_browse.py:174` / LIFECYCLE
- **Symptom:** A new prewarm thread starts without checking for an in-flight one; two workers can compute the same cache simultaneously.
- **Suggested fix:** Cancel or `join()` the previous thread before starting a new one.
- **Regression test:** `tests/unit/ui/test_main_frame_browse.py::test_prewarm_thread_cancelled_on_repeat`

#### M-31 — `ui/sticky_notes.py:362` — bare `MessageBox` without contract
- **File / Category:** `quill/ui/sticky_notes.py:362` / A11Y
- **Symptom:** Uses raw `self._wx.MessageBox` without enter/exit announcements; inconsistent with the rest of the dialog contract.
- **Suggested fix:** Replace with `_show_message_box`-style helper.
- **Regression test:** `tests/unit/ui/test_sticky_notes.py::test_delete_confirm_uses_contract_helper`

#### M-32 — `ui/main_frame_image.py:160-167` — `time.sleep(0.1)` polling
- **File / Category:** `quill/ui/main_frame_image.py:160-167` / PERF
- **Symptom:** Polls 10×/sec during OCR runs; burns CPU.
- **Suggested fix:** Replace polling loop with `wx.Timer` for periodic progress updates.
- **Regression test:** Low-level test asserting the timer is wired.

---

## 2. Open files (MEDIUM only)

| File | Issues |
| --- | --- |
| `quill/tools/dialog_button_contract.py` | M-24 |
| `quill/ui/main_frame.py` | M-28 |
| `quill/ui/main_frame_browse.py` | M-30 |
| `quill/ui/main_frame_image.py` | M-32 |
| `quill/ui/assistant_tools.py` | M-29 |
| `quill/ui/sticky_notes.py` | M-31 |

---

## 3. Triage order (remaining 6)

1. M-31 — `MessageBox` contract helper (`sticky_notes.py`)
2. M-32 — `wx.Timer` for polling (`main_frame_image.py`)
3. M-24 — unbacked `affirmative_id` audit (`dialog_button_contract.py`)
4. M-28 — focus leak in crash recovery loop (`main_frame.py`)
5. M-29 — Run Python off UI thread (`assistant_tools.py`)
6. M-30 — prewarm thread cancellation (`main_frame_browse.py`)

---

## 4. State of the union

### Severity roll-up

| Severity | Total | Fixed | Open |
| --- | ---: | ---: | ---: |
| CRITICAL | 0 | 0 | 0 |
| HIGH | 13 | 13 | 0 |
| MEDIUM | 32 | 26 | **6** |
| LOW | 22 | 22 | 0 |
| NIT | 16 | 16 | 0 |
| Magic/UX | 16 | 16 | 0 |
| **Total** | **99** | **93** | **6** |

### Closure cadence

| Sweep | MEDIUM closed | LOW closed | NIT closed | Notes |
| --- | ---: | ---: | ---: | --- |
| 1–6 | 0 | 3 | 11 | initial review + HIGH + Magic |
| 7 | 1 (M-27) | 6 | 1 | easiest LOWs/NITs |
| 8 | 0 | 5 | 1 | more LOWs |
| 9 | 2 (M-1, M-4) | 0 | 0 | watch-action humanization |
| 10 | 1 (M-2) | 2 | 0 | storage_mode + task_manager |
| 11 | 0 | 2 | 1 | DPAPI + cache-reset |
| 12 | 0 | 4 | 2 | §6/§7 fully closed |
| 13 | 0 | 1 (L-23) | 0 | csv_grid stride |
| 14 | 14 (M-10..M-26 batch) | 0 | 0 | stability + IO + AI + tools |
| 15 | **8** (M-3, M-5..M-9, M-14, M-15) | 0 | 0 | security + I/O + TTS |
| **Total closed** | **26** | **22** | **16** | — |

### Deferred (needs real Windows runtime)

- 🟡 OCR-1 / OCR-3 — real Windows OCR engine and clipboard paths
- 🟡 AI-19 — live device-login endpoint
- 🟡 SET-2 — sensitivity-aware dictation backend
- 🟡 AGENT-1 — advisory-only by design

---

*6 MEDIUM open. All other severities closed. See `CHANGELOG.md` for closed items.*
