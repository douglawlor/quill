from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import quill.core.ai.model_manager as model_manager
from quill.core.ai.model_manager import MODELS, ModelSpec


def test_all_models_pin_a_sha256() -> None:
    """Every shipped model must carry a non-empty SHA-256 for SEC-6 verification."""
    for spec in MODELS.values():
        assert spec.sha256, f"{spec.id} is missing a pinned sha256"
        assert len(spec.sha256) == 64


def test_phi_4_uses_an_open_non_gated_mirror() -> None:
    """The recommended >=8 GB model must not point at a gated repository."""
    spec = MODELS["phi-4-mini"]
    assert "bartowski/Phi-4-mini-instruct-GGUF" not in spec.url
    assert "lmstudio-community/Phi-4-mini-instruct-GGUF" in spec.url


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self.headers = {"Content-Length": str(len(payload))}
        self._read = False

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_args: object) -> bool:
        return False

    def read(self, _size: int = -1) -> bytes:
        if self._read:
            return b""
        self._read = True
        return self._payload


def _patch_download(monkeypatch: pytest.MonkeyPatch, payload: bytes) -> None:
    monkeypatch.setattr(
        model_manager.urllib.request,
        "urlopen",
        lambda *_args, **_kwargs: _FakeResponse(payload),
    )


def test_download_rejects_checksum_mismatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = b"corrupted model bytes"
    _patch_download(monkeypatch, payload)
    target = tmp_path / "model.gguf"
    wrong = "0" * 64
    with pytest.raises(RuntimeError) as excinfo:
        model_manager._download("https://example/model.gguf", target, None, wrong)
    assert "integrity check" in str(excinfo.value)
    assert not target.exists()
    # The partial file must be discarded on mismatch.
    assert not target.with_name(target.name + ".part").exists()


def test_download_accepts_matching_checksum(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = b"a valid model payload"
    _patch_download(monkeypatch, payload)
    target = tmp_path / "model.gguf"
    digest = hashlib.sha256(payload).hexdigest()
    model_manager._download("https://example/model.gguf", target, None, digest)
    assert target.exists()
    assert target.read_bytes() == payload


def test_ensure_model_verifies_pinned_checksum(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    payload = b"tiny gguf"
    spec = ModelSpec(
        "tiny",
        "Tiny",
        "tiny.gguf",
        "https://example/tiny.gguf",
        0.1,
        "",
        "deadbeef" * 8,  # deliberately wrong
    )
    monkeypatch.setattr(model_manager, "resolve_spec", lambda *_a, **_k: spec)
    monkeypatch.setattr(model_manager, "models_dir", lambda: tmp_path)
    monkeypatch.delenv("QUILL_LLAMA_MODEL", raising=False)
    _patch_download(monkeypatch, payload)
    with pytest.raises(RuntimeError) as excinfo:
        model_manager.ensure_model()
    assert "integrity check" in str(excinfo.value)
