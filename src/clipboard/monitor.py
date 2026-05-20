"""剪贴板监听器 — 主线程 QTimer 轮询"""
import time

from PySide6.QtCore import QObject, Signal, QTimer

from .reader import read_clipboard


class ClipboardMonitor(QObject):
    """使用 QTimer 在主线程轮询剪贴板变化"""

    new_item = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer()
        self._timer.setInterval(300)
        self._timer.timeout.connect(self._check_clipboard)
        self._last_hash: str = ""
        self._last_change_time = 0

    def start(self):
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def _check_clipboard(self):
        """检查剪贴板是否有新内容"""
        try:
            data = read_clipboard()
            if data is None:
                return

            now = time.time()
            # 防抖：忽略 300ms 内的重复
            if now - self._last_change_time < 0.3:
                return

            # 去重
            if data["hash"] == self._last_hash:
                return

            self._last_hash = data["hash"]
            self._last_change_time = now
            self.new_item.emit(data)
        except Exception:
            pass
