"""全局热键管理 — 使用 keyboard 库"""
from PySide6.QtCore import QObject, Signal, QMetaObject, Qt, QTimer

import keyboard


class HotkeyManager(QObject):
    """全局热键管理器 — keyboard 回调在后台线程，通过标志位 + QTimer 回到主线程"""

    triggered = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hotkey_str = "ctrl+shift+v"
        self._pending = False
        self._poll_timer: QTimer | None = None

    def register(self, hotkey_str: str = "ctrl+shift+v") -> bool:
        try:
            self.unregister()
            self._hotkey_str = hotkey_str
            # keyboard 回调在后台线程，设置标志位
            keyboard.add_hotkey(hotkey_str, self._on_keyboard_trigger, suppress=False)
            # QTimer 在主线程轮询标志位
            self._poll_timer = QTimer()
            self._poll_timer.setInterval(50)
            self._poll_timer.timeout.connect(self._poll)
            self._poll_timer.start()
            return True
        except Exception:
            return False

    def unregister(self):
        if self._poll_timer:
            self._poll_timer.stop()
            self._poll_timer = None
        try:
            keyboard.unhook_all()
        except Exception:
            pass

    def _on_keyboard_trigger(self):
        """在 keyboard 的后台线程中调用，只设置标志位"""
        self._pending = True

    def _poll(self):
        """在主线程 QTimer 中检查标志位"""
        if self._pending:
            self._pending = False
            self.triggered.emit()

    @property
    def hotkey_str(self) -> str:
        return self._hotkey_str
