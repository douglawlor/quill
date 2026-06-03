"""DLG-3 Phase 5: startup / onboarding hardening characterization.

Phase 5 hardens the first-run / startup modal chain (screen-reader detection,
trust consent, crash recovery, first-run onboarding, watch folders). Two of its
three acceptance claims are pure-code contracts that these tests pin so they
cannot silently regress:

1. **The screen-reader startup-crash path is retired.** Every deferred startup
   step runs inside its own ``try/except`` in ``_run_deferred_startup_tasks``; a
   throwing step is recorded via ``_report_startup_task_failure`` and the app
   stays open and keeps running the remaining steps. (Historically an exception
   here killed Quill right after the startup tip with nothing in the log.)

2. **Explicit-consent requirements are preserved.** ``_show_trust_consent_onboarding``
   only marks consent complete when the user explicitly accepts; declining never
   records consent, and a decline during startup closes the app instead of
   silently continuing.

The third claim (deterministic focus across chained modal flows) is verified
live in Phase 8 (DLG-3.8) and structurally enforced by the dialog-hardening
contract gate; it is not re-asserted here.
"""

from __future__ import annotations

import quill.ui.main_frame as main_frame_module
from quill.ui.main_frame import MainFrame


class _Frame:
    def __init__(self) -> None:
        self.closed = 0

    def Close(self):  # noqa: N802 - mimics wx API
        self.closed += 1


class _Wx:
    ID_YES = 5103
    ID_NO = 5104
    YES_NO = 0x0008
    ICON_INFORMATION = 0x0002


def _build_frame() -> MainFrame:
    frame = MainFrame.__new__(MainFrame)
    frame.frame = _Frame()
    frame._wx = _Wx()
    frame.settings = type("Settings", (), {"auto_check_updates": False})()
    frame._safe_mode = False
    frame._status: list[str] = []
    frame._set_status = lambda message: frame._status.append(message)
    return frame


def test_deferred_startup_isolates_a_throwing_step_and_keeps_going(monkeypatch) -> None:
    frame = _build_frame()
    failures: list[str] = []
    frame._report_startup_task_failure = lambda label: failures.append(label)
    frame._start_ipc_poll = lambda: None
    frame._first_run_trust_consent_prompt = False

    ran: list[str] = []

    def _boom() -> None:
        raise RuntimeError("crash recovery exploded")

    frame._offer_crash_recovery = _boom
    frame._maybe_run_first_run_onboarding = lambda: ran.append("first-run")
    frame._maybe_start_watch_folder = lambda: ran.append("watch-folder")
    monkeypatch.setattr(
        main_frame_module,
        "detect_screen_reader",
        lambda: type("D", (), {"detected": False, "name": ""})(),
    )

    # Must not raise -- the startup-crash path is retired.
    frame._run_deferred_startup_tasks()

    # The throwing step was recorded, and the steps after it still ran.
    assert "crash recovery" in failures
    assert ran == ["first-run", "watch-folder"]
    assert frame.frame.closed == 0


def test_trust_consent_decline_does_not_record_consent(monkeypatch) -> None:
    frame = _build_frame()
    frame._show_modal_dialog = lambda dialog, title: _Wx.ID_NO
    marked: list[int] = []
    monkeypatch.setattr(main_frame_module, "mark_trust_consent_complete", lambda: marked.append(1))

    class _Dialog:
        def __init__(self, *a, **k) -> None:
            pass

        def SetYesNoLabels(self, *a):  # noqa: N802 - mimics wx API
            return True

        def Destroy(self):  # noqa: N802 - mimics wx API
            return True

    frame._wx.MessageDialog = _Dialog

    accepted = frame._show_trust_consent_onboarding(force=True)

    assert accepted is False
    assert marked == []


def test_trust_consent_accept_records_consent(monkeypatch) -> None:
    frame = _build_frame()
    frame._show_modal_dialog = lambda dialog, title: _Wx.ID_YES
    marked: list[int] = []
    monkeypatch.setattr(main_frame_module, "mark_trust_consent_complete", lambda: marked.append(1))

    class _Dialog:
        def __init__(self, *a, **k) -> None:
            pass

        def SetYesNoLabels(self, *a):  # noqa: N802 - mimics wx API
            return True

        def Destroy(self):  # noqa: N802 - mimics wx API
            return True

    frame._wx.MessageDialog = _Dialog

    accepted = frame._show_trust_consent_onboarding(force=True)

    assert accepted is True
    assert marked == [1]


def test_declined_startup_consent_closes_the_app(monkeypatch) -> None:
    frame = _build_frame()
    frame._report_startup_task_failure = lambda label: None
    frame._start_ipc_poll = lambda: None
    frame._first_run_trust_consent_prompt = True
    frame._show_trust_consent_onboarding = lambda force: False
    later_steps: list[str] = []
    frame._offer_crash_recovery = lambda: later_steps.append("crash")
    frame._maybe_run_first_run_onboarding = lambda: later_steps.append("first-run")
    frame._maybe_start_watch_folder = lambda: later_steps.append("watch")
    monkeypatch.setattr(
        main_frame_module,
        "detect_screen_reader",
        lambda: type("D", (), {"detected": False, "name": ""})(),
    )

    frame._run_deferred_startup_tasks()

    # Declining consent closes the app and short-circuits the rest of startup.
    assert frame.frame.closed == 1
    assert later_steps == []
    assert frame._status[-1] == "Startup consent declined. Quill is closing."
