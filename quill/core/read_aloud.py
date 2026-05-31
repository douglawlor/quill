from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

try:
    import pyttsx3  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - optional runtime dependency
    pyttsx3 = None


@dataclass(frozen=True, slots=True)
class VoiceOption:
    id: str
    name: str


@dataclass(frozen=True, slots=True)
class SentenceSpan:
    start: int
    end: int


DECTALK_VOICE_COMMANDS: dict[str, str] = {
    "paul": "[:np]",
    "harry": "[:nh]",
    "dennis": "[:nd]",
    "frank": "[:nf]",
    "betty": "[:nb]",
    "ursula": "[:nu]",
    "rita": "[:nr]",
    "wendy": "[:nw]",
    "kit": "[:nk]",
}

DECTALK_RELEASE_ZIP_URL = "https://github.com/dectalk/dectalk/releases/download/2023-10-30/vs2022.zip"


def discover_dectalk_executable(configured_path: str = "") -> Path | None:
    if configured_path.strip():
        candidate = Path(configured_path).expanduser()
        if candidate.exists():
            return candidate.resolve()
    app_root = os.environ.get("QUILL_APP_ROOT", "").strip()
    if app_root:
        bundled = Path(app_root) / "tools" / "speech" / "dectalk"
        for relative in ("speak.exe", "AMD64/speak.exe", "IA32/speak.exe"):
            probe = bundled / relative
            if probe.exists():
                return probe.resolve()
    return None


def download_dectalk_runtime(target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    archive = target_dir / "vs2022.zip"
    with urllib.request.urlopen(DECTALK_RELEASE_ZIP_URL, timeout=180) as response:  # noqa: S310
        archive.write_bytes(response.read())
    extract_root = target_dir / "release"
    if extract_root.exists():
        shutil.rmtree(extract_root)
    extract_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(extract_root)
    for candidate in (
        extract_root / "AMD64" / "speak.exe",
        extract_root / "speak.exe",
    ):
        if candidate.exists():
            return candidate.resolve()
    raise ReadAloudUnavailableError("Downloaded DECtalk package did not contain speak.exe")


def list_dectalk_voices() -> list[VoiceOption]:
    return [
        VoiceOption(id="paul", name="Paul"),
        VoiceOption(id="harry", name="Harry"),
        VoiceOption(id="dennis", name="Dennis"),
        VoiceOption(id="frank", name="Frank"),
        VoiceOption(id="betty", name="Betty"),
        VoiceOption(id="ursula", name="Ursula"),
        VoiceOption(id="rita", name="Rita"),
        VoiceOption(id="wendy", name="Wendy"),
        VoiceOption(id="kit", name="Kit"),
    ]


def list_voices() -> list[VoiceOption]:
    if pyttsx3 is None:
        return []
    engine = pyttsx3.init()
    try:
        voices = []
        for voice in engine.getProperty("voices") or []:
            voice_id = str(getattr(voice, "id", "")).strip()
            if not voice_id:
                continue
            name = str(getattr(voice, "name", voice_id)).strip() or voice_id
            voices.append(VoiceOption(id=voice_id, name=name))
        return voices
    finally:
        engine.stop()


def sentence_spans(text: str) -> list[SentenceSpan]:
    spans: list[SentenceSpan] = []
    for match in re.finditer(r".+?(?:[.!?]+(?:\s+|$)|\n+|$)", text, re.DOTALL):
        start, end = match.span()
        if text[start:end].strip():
            spans.append(SentenceSpan(start=start, end=end))
    if not spans and text.strip():
        spans.append(SentenceSpan(0, len(text)))
    return spans


class ReadAloudUnavailableError(RuntimeError):
    pass


class ReadAloudController:
    def __init__(self) -> None:
        self._state = "idle"
        self._cursor = 0
        self._thread: threading.Thread | None = None
        self._active_process: subprocess.Popen[bytes] | None = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            return self._state

    @property
    def cursor(self) -> int:
        with self._lock:
            return self._cursor

    def start(
        self,
        text: str,
        cursor: int,
        voice_id: str,
        *,
        engine_name: str = "pyttsx3",
        rate: int | None = None,
        volume: float | None = None,
        pitch: int | None = None,
        dectalk_executable: str = "",
        dectalk_voice: str = "",
        dectalk_rate: int = 180,
        dectalk_dictionary: str = "",
        end: int | None = None,
        on_progress: Callable[[int, int], None] | None = None,
        on_state_change: Callable[[str], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ) -> None:
        normalized_engine = engine_name.strip().lower() or "pyttsx3"
        if normalized_engine == "pyttsx3" and pyttsx3 is None:
            raise ReadAloudUnavailableError("pyttsx3 is not available")
        if normalized_engine == "dectalk":
            executable = discover_dectalk_executable(dectalk_executable)
            if executable is None:
                raise ReadAloudUnavailableError("DECtalk executable was not found")
        if normalized_engine not in {"pyttsx3", "dectalk"}:
            raise ReadAloudUnavailableError(f"Unsupported read-aloud engine: {normalized_engine}")
        self.stop()
        spans = [span for span in sentence_spans(text) if span.end > cursor]
        if end is not None:
            spans = [span for span in spans if span.start < end]
        if not spans:
            stop_at = len(text) if end is None else min(len(text), max(cursor, end))
            spans = [SentenceSpan(cursor, stop_at)]
        with self._lock:
            self._state = "playing"
            self._cursor = cursor
        self._stop_event.clear()
        self._pause_event.clear()

        def worker() -> None:
            try:
                if normalized_engine == "pyttsx3":
                    self._run_pyttsx3(
                        spans,
                        text,
                        voice_id=voice_id,
                        rate=rate,
                        volume=volume,
                        pitch=pitch,
                        on_progress=on_progress,
                    )
                else:
                    self._run_dectalk(
                        spans,
                        text,
                        executable=discover_dectalk_executable(dectalk_executable) or Path(
                            dectalk_executable
                        ).expanduser(),
                        voice_id=dectalk_voice,
                        rate=dectalk_rate,
                        dictionary_path=Path(dectalk_dictionary).expanduser()
                        if dectalk_dictionary.strip()
                        else None,
                        on_progress=on_progress,
                    )
            except Exception as exc:  # noqa: BLE001
                with self._lock:
                    self._state = "idle"
                if on_error is not None:
                    on_error(str(exc))
                if on_state_change is not None:
                    on_state_change("error")
                return

            with self._lock:
                if self._pause_event.is_set():
                    self._state = "paused"
                else:
                    self._state = "idle"
            if on_state_change is not None:
                on_state_change(self.state)

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def _run_pyttsx3(
        self,
        spans: list[SentenceSpan],
        text: str,
        *,
        voice_id: str,
        rate: int | None,
        volume: float | None,
        pitch: int | None,
        on_progress: Callable[[int, int], None] | None,
    ) -> None:
        engine = pyttsx3.init()
        try:
            if voice_id:
                engine.setProperty("voice", voice_id)
            if rate is not None:
                engine.setProperty("rate", int(rate))
            if volume is not None:
                engine.setProperty("volume", max(0.0, min(float(volume), 1.0)))
            if pitch is not None:
                try:
                    engine.setProperty("pitch", int(pitch))
                except Exception:  # noqa: BLE001
                    pass
            for span in spans:
                if self._stop_event.is_set() or self._pause_event.is_set():
                    break
                sentence = text[span.start : span.end].strip()
                if not sentence:
                    continue
                if on_progress is not None:
                    on_progress(span.start, span.end)
                engine.say(sentence)
                engine.runAndWait()
                with self._lock:
                    self._cursor = span.end
        finally:
            engine.stop()

    def _run_dectalk(
        self,
        spans: list[SentenceSpan],
        text: str,
        *,
        executable: Path,
        voice_id: str,
        rate: int,
        dictionary_path: Path | None,
        on_progress: Callable[[int, int], None] | None,
    ) -> None:
        working_dir = executable.parent
        self._ensure_dectalk_dictionary(working_dir, dictionary_path)
        for span in spans:
            if self._stop_event.is_set() or self._pause_event.is_set():
                break
            sentence = text[span.start : span.end].strip()
            if not sentence:
                continue
            if on_progress is not None:
                on_progress(span.start, span.end)
            payload = self._build_dectalk_payload(sentence, voice_id, rate)
            self._speak_sentence_dectalk(executable, payload)
            with self._lock:
                self._cursor = span.end

    def _build_dectalk_payload(self, sentence: str, voice_id: str, rate: int) -> str:
        parts: list[str] = []
        voice_cmd = DECTALK_VOICE_COMMANDS.get(voice_id.strip().lower(), "")
        if voice_cmd:
            parts.append(voice_cmd)
        bounded_rate = max(75, min(650, int(rate)))
        parts.append(f"[:ra {bounded_rate}]")
        parts.append(sentence)
        return " ".join(parts)

    def _ensure_dectalk_dictionary(self, working_dir: Path, dictionary_path: Path | None) -> None:
        target = working_dir / "dtalk_us.dic"
        if target.exists():
            return
        candidates: list[Path] = []
        if dictionary_path is not None:
            candidates.append(dictionary_path)
        candidates.extend(
            [
                working_dir / "dic" / "dtalk_us.dic",
                working_dir / "dtalk_us.dic",
            ]
        )
        source = next((path for path in candidates if path.exists()), None)
        if source is None:
            raise ReadAloudUnavailableError(
                "DECtalk dictionary dtalk_us.dic was not found. Configure dictionary path in Speech settings."
            )
        if source.resolve() == target.resolve():
            return
        target.write_bytes(source.read_bytes())

    def _speak_sentence_dectalk(self, executable: Path, payload: str) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            suffix=".txt",
            encoding="utf-8",
            errors="replace",
        ) as handle:
            handle.write(payload)
            temp_path = Path(handle.name)
        create_no_window = int(getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            process = subprocess.Popen(
                [str(executable), "-file", str(temp_path)],
                cwd=str(executable.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=create_no_window,
            )
            self._active_process = process
            while process.poll() is None:
                if self._stop_event.is_set() or self._pause_event.is_set():
                    process.terminate()
                    break
                time.sleep(0.05)
            exit_code = process.wait(timeout=2)
            if exit_code != 0 and not (self._stop_event.is_set() or self._pause_event.is_set()):
                raise ReadAloudUnavailableError(
                    f"DECtalk exited with code {exit_code}. Check executable and dictionary settings."
                )
        finally:
            self._active_process = None
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    def pause(self) -> None:
        with self._lock:
            if self._state != "playing":
                return
            self._state = "paused"
        self._pause_event.set()
        process = self._active_process
        if process is not None and process.poll() is None:
            process.terminate()

    def stop(self) -> None:
        self._stop_event.set()
        self._pause_event.clear()
        process = self._active_process
        if process is not None and process.poll() is None:
            process.terminate()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=0.2)
        with self._lock:
            self._state = "idle"
        self._thread = None
