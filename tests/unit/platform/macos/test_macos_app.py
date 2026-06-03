from __future__ import annotations

from quill.__main__ import main as _canonical_main
from quill.platform.macos import macos_app


def test_macos_app_reexports_canonical_main() -> None:
    # scripts/setup_macos.py points the py2app bundle's APP at this module, so
    # the .app entry point must dispatch to the single canonical CLI entry
    # point — the same `main` behind the `quill` console script — keeping the
    # bundle and the command line on identical startup behaviour.
    assert macos_app.main is _canonical_main
