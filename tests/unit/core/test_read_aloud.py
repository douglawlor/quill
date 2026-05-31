from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from quill.core import read_aloud as read_aloud_module
from quill.core.read_aloud import (
    ReadAloudUnavailableError,
    ReadAloudController,
    discover_piper_executable,
    list_dectalk_voices,
    list_voices,
    sentence_spans,
    synthesize_with_piper,
)


def test_sentence_spans() -> None:
    spans = sentence_spans("One. Two! Three?")
    assert [(span.start, span.end) for span in spans] == [(0, 5), (5, 10), (10, 16)]


def test_list_voices_uses_backend(monkeypatch) -> None:
    class FakeVoice:
        id = "voice-1"
        name = "Voice 1"

    class FakeEngine:
        def __init__(self) -> None:
            self.spoken: list[str] = []
            self.properties: dict[str, object] = {}

        def getProperty(self, name: str):  # noqa: N802
            if name == "voices":
                return [FakeVoice()]
            return None

        def setProperty(self, name: str, value: object) -> None:  # noqa: N802
            self.properties[name] = value

        def say(self, text: str) -> None:
            self.spoken.append(text)

        def runAndWait(self) -> None:  # noqa: N802
            return None

        def stop(self) -> None:
            return None

    engine = FakeEngine()
    monkeypatch.setattr(read_aloud_module, "pyttsx3", SimpleNamespace(init=lambda: engine))

    voices = list_voices()
    assert [(voice.id, voice.name) for voice in voices] == [("voice-1", "Voice 1")]


def test_read_aloud_controller_speaks_sentences(monkeypatch) -> None:
    class FakeEngine:
        def __init__(self) -> None:
            self.spoken: list[str] = []
            self.properties: dict[str, object] = {}

        def getProperty(self, name: str):  # noqa: N802
            return []

        def setProperty(self, name: str, value: object) -> None:  # noqa: N802
            self.properties[name] = value

        def say(self, text: str) -> None:
            self.spoken.append(text)

        def runAndWait(self) -> None:  # noqa: N802
            return None

        def stop(self) -> None:
            return None

    engine = FakeEngine()
    monkeypatch.setattr(read_aloud_module, "pyttsx3", SimpleNamespace(init=lambda: engine))

    controller = ReadAloudController()
    controller.start("One. Two!", 0, "voice-1")
    assert controller._thread is not None
    controller._thread.join(timeout=1)

    assert engine.properties["voice"] == "voice-1"
    assert engine.spoken == ["One.", "Two!"]


def test_list_dectalk_voices_has_expected_defaults() -> None:
    voices = list_dectalk_voices()
    assert voices
    assert voices[0].id == "paul"
    assert any(voice.id == "betty" for voice in voices)


def test_build_dectalk_payload_includes_voice_and_rate() -> None:
    controller = ReadAloudController()
    payload = controller._build_dectalk_payload("Hello there", "paul", 200)
    assert "[:np]" in payload
    assert "[:ra 200]" in payload
    assert "Hello there" in payload


def test_discover_piper_executable_uses_explicit_path(tmp_path: Path) -> None:
    exe = tmp_path / "piper.exe"
    exe.write_text("binary", encoding="utf-8")
    discovered = discover_piper_executable(str(exe))
    assert discovered == exe.resolve()


def test_synthesize_with_piper_runs_process(monkeypatch, tmp_path: Path) -> None:
    exe = tmp_path / "piper.exe"
    model = tmp_path / "voice.onnx"
    output = tmp_path / "speech.wav"
    exe.write_text("binary", encoding="utf-8")
    model.write_text("model", encoding="utf-8")

    class Completed:
        returncode = 0
        stdout = ""
        stderr = ""

    called: dict[str, object] = {}

    def fake_run(command, **kwargs):
        called["command"] = command
        called["kwargs"] = kwargs
        return Completed()

    monkeypatch.setattr(read_aloud_module.subprocess, "run", fake_run)

    synthesize_with_piper(
        "Hello from piper",
        output,
        executable_path=exe,
        model_path=model,
    )
    assert called["command"] == [
        str(exe),
        "--model",
        str(model),
        "--output_file",
        str(output),
    ]
    assert called["kwargs"]["input"] == "Hello from piper"


def test_synthesize_with_piper_raises_for_failure(monkeypatch, tmp_path: Path) -> None:
    exe = tmp_path / "piper.exe"
    model = tmp_path / "voice.onnx"
    output = tmp_path / "speech.wav"
    exe.write_text("binary", encoding="utf-8")
    model.write_text("model", encoding="utf-8")

    class Completed:
        returncode = 1
        stdout = ""
        stderr = "bad model"

    monkeypatch.setattr(read_aloud_module.subprocess, "run", lambda *_args, **_kwargs: Completed())

    try:
        synthesize_with_piper(
            "Hello from piper",
            output,
            executable_path=exe,
            model_path=model,
        )
    except ReadAloudUnavailableError as exc:
        assert "Piper failed" in str(exc)
    else:
        raise AssertionError("Expected ReadAloudUnavailableError")
