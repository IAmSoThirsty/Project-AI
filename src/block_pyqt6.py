# [Qt Block Shim]                                [2026-04-03 14:15]
#                                          Productivity: Active
"""Qt loader shim for headless or degraded environments."""

from __future__ import annotations

import sys
import types
from collections.abc import Callable
from typing import Any


class _DummySignal:
    """Tiny signal stand-in used by the shimmed Qt modules."""

    def connect(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def emit(self, *_args: Any, **_kwargs: Any) -> None:
        return None


class _DummyQtObject:
    """Generic no-op Qt object replacement."""

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        self._children: list[Any] = []

    def __call__(self, *_args: Any, **_kwargs: Any) -> _DummyQtObject:
        return self

    def __getattr__(self, _name: str) -> _DummyQtObject:
        return self

    def __bool__(self) -> bool:
        return False

    def __iter__(self):
        return iter(())

    def __repr__(self) -> str:
        return "<PyQt6 shim>"

    def show(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def close(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def deleteLater(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def setLayout(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def setText(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def text(self) -> str:
        return ""

    def setWindowTitle(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def exec(self, *_args: Any, **_kwargs: Any) -> int:
        return 0

    exec_ = exec

    @classmethod
    def instance(cls) -> None:
        return None

    @classmethod
    def singleShot(cls, *_args: Any, **_kwargs: Any) -> None:
        return None


class _DummyApplication(_DummyQtObject):
    """QApplication replacement."""

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        super().__init__()


class _DummyFont(_DummyQtObject):
    """QFont replacement."""


class _DummyQtEnum:
    """Simple enum namespace for Qt constants."""

    AlignCenter = 0
    Horizontal = 1
    Vertical = 2
    LeftButton = 3
    RightButton = 4
    KeepAspectRatio = 5
    Checked = 6
    Unchecked = 7


def _dummy_signal_factory(*_args: Any, **_kwargs: Any) -> _DummySignal:
    return _DummySignal()


def _dummy_slot_decorator(*_args: Any, **_kwargs: Any) -> Callable[[Any], Any]:
    def decorator(func: Any) -> Any:
        return func

    return decorator


def _build_module(name: str) -> types.ModuleType:
    module = types.ModuleType(name)
    module.__file__ = f"<{name} shim>"
    module.__package__ = name.rpartition(".")[0] or name
    module.__dict__["__getattr__"] = _module_getattr
    module.__dict__["__all__"] = []
    return module


def _module_getattr(attr: str):
    if attr.startswith("__"):
        _raise_attr(attr)
    return _DummyQtObject


def _raise_attr(name: str):
    raise AttributeError(name)


def _install_shim() -> None:
    pyqt6 = _build_module("PyQt6")
    pyqt6.__path__ = []  # type: ignore[attr-defined]

    qt_widgets = _build_module("PyQt6.QtWidgets")
    qt_gui = _build_module("PyQt6.QtGui")
    qt_core = _build_module("PyQt6.QtCore")

    qt_widgets.QApplication = _DummyApplication
    qt_widgets.QWidget = _DummyQtObject
    qt_widgets.QMainWindow = _DummyQtObject
    qt_widgets.QDialog = _DummyQtObject
    qt_widgets.QLabel = _DummyQtObject
    qt_widgets.QPushButton = _DummyQtObject
    qt_widgets.QLineEdit = _DummyQtObject
    qt_widgets.QTextEdit = _DummyQtObject
    qt_widgets.QPlainTextEdit = _DummyQtObject
    qt_widgets.QVBoxLayout = _DummyQtObject
    qt_widgets.QHBoxLayout = _DummyQtObject
    qt_widgets.QGridLayout = _DummyQtObject
    qt_widgets.QSplitter = _DummyQtObject
    qt_widgets.QTabWidget = _DummyQtObject
    qt_widgets.QListWidget = _DummyQtObject
    qt_widgets.QListWidgetItem = _DummyQtObject
    qt_widgets.QSystemTrayIcon = _DummyQtObject
    qt_widgets.QMessageBox = _DummyQtObject

    qt_gui.QFont = _DummyFont
    qt_gui.QIcon = _DummyQtObject
    qt_gui.QPixmap = _DummyQtObject
    qt_gui.QAction = _DummyQtObject
    qt_gui.QColor = _DummyQtObject
    qt_gui.QCursor = _DummyQtObject

    qt_core.QObject = _DummyQtObject
    qt_core.QThread = _DummyQtObject
    qt_core.QTimer = _DummyQtObject
    qt_core.QEvent = _DummyQtObject
    qt_core.QSize = _DummyQtObject
    qt_core.QPoint = _DummyQtObject
    qt_core.QRect = _DummyQtObject
    qt_core.Qt = _DummyQtEnum
    qt_core.pyqtSignal = _dummy_signal_factory
    qt_core.pyqtSlot = _dummy_slot_decorator
    qt_core.Signal = _dummy_signal_factory
    qt_core.Slot = _dummy_slot_decorator

    pyqt6.QtWidgets = qt_widgets
    pyqt6.QtGui = qt_gui
    pyqt6.QtCore = qt_core

    sys.modules["PyQt6"] = pyqt6
    sys.modules["PyQt6.QtWidgets"] = qt_widgets
    sys.modules["PyQt6.QtGui"] = qt_gui
    sys.modules["PyQt6.QtCore"] = qt_core


def ensure_pyqt6_available(force: bool = False) -> bool:
    """Ensure PyQt6 imports succeed, installing a shim if required."""

    if not force:
        try:
            import PyQt6.QtCore  # noqa: F401
            import PyQt6.QtGui  # noqa: F401
            import PyQt6.QtWidgets  # noqa: F401

            return False
        except Exception:
            pass

    _install_shim()
    return True


__all__ = ["ensure_pyqt6_available"]
