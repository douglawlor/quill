from __future__ import annotations

from quill.core.menu_customization import MenuCustomization
from quill.ui.main_frame import (
    _TOP_MENU_DEFS,
    MainFrame,
    _normalize_menu_label,
)


class _FakeMenu:
    """Minimal stand-in for a wx.Menu used by the transform pass."""

    def __init__(self, key: str) -> None:
        self.key = key
        self.destroyed = False

    def Destroy(self) -> None:
        self.destroyed = True


class _FakeMenuBar:
    """Records the Append/Remove operations the transform pass performs."""

    def __init__(self) -> None:
        # Start in the factory order with factory labels.
        self._menus: list[tuple[_FakeMenu, str]] = [
            (_FakeMenu(key), label) for key, label in _TOP_MENU_DEFS
        ]

    def GetMenuCount(self) -> int:
        return len(self._menus)

    def GetMenu(self, index: int) -> _FakeMenu:
        return self._menus[index][0]

    def GetMenuLabelText(self, index: int) -> str:
        # wx returns the label without the mnemonic ampersand.
        return _normalize_menu_label(self._menus[index][1])

    def Remove(self, index: int) -> _FakeMenu:
        menu, _label = self._menus.pop(index)
        return menu

    def Append(self, menu: _FakeMenu, label: str) -> None:
        self._menus.append((menu, label))

    def keys(self) -> list[str]:
        return [menu.key for menu, _label in self._menus]

    def labels(self) -> list[str]:
        return [label for _menu, label in self._menus]


def _build_frame(customization: MenuCustomization) -> MainFrame:
    frame = MainFrame.__new__(MainFrame)
    frame._menu_customization = customization
    return frame


def test_no_customization_leaves_menu_bar_untouched() -> None:
    frame = _build_frame(MenuCustomization())
    bar = _FakeMenuBar()

    frame._apply_menu_customization(bar)

    assert bar.keys() == [key for key, _ in _TOP_MENU_DEFS]


def test_reorder_applies_desired_order() -> None:
    cust = MenuCustomization()
    default_order = [key for key, _ in _TOP_MENU_DEFS]
    new_order = ["help", *[k for k in default_order if k != "help"]]
    cust.set_top_order(new_order)
    frame = _build_frame(cust)
    bar = _FakeMenuBar()

    frame._apply_menu_customization(bar)

    assert bar.keys()[0] == "help"


def test_hidden_menu_is_removed_and_destroyed() -> None:
    cust = MenuCustomization()
    cust.set_top_hidden("whisperer", True)
    frame = _build_frame(cust)
    bar = _FakeMenuBar()
    whisperer_menu = next(m for m, _l in bar._menus if m.key == "whisperer")

    frame._apply_menu_customization(bar)

    assert "whisperer" not in bar.keys()
    assert whisperer_menu.destroyed is True


def test_rename_uses_custom_label_with_mnemonic() -> None:
    cust = MenuCustomization()
    cust.rename_top("file", "&Document")
    frame = _build_frame(cust)
    bar = _FakeMenuBar()

    frame._apply_menu_customization(bar)

    file_index = bar.keys().index("file")
    assert bar.labels()[file_index] == "&Document"


def test_unrecognized_label_bails_out_without_changes() -> None:
    cust = MenuCustomization()
    cust.set_top_order(["help", "file"])
    frame = _build_frame(cust)
    bar = _FakeMenuBar()
    # Corrupt one menu's label so its key cannot be resolved.
    menu, _label = bar._menus[0]
    bar._menus[0] = (menu, "Totally Unknown")

    frame._apply_menu_customization(bar)

    # The bail-out path leaves the (corrupted) bar in its original order.
    assert bar.keys() == [key for key, _ in _TOP_MENU_DEFS]
