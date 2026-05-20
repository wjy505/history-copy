"""定时清理 — 删除超过存储期限的非置顶记录"""
from datetime import datetime, timedelta

from PySide6.QtCore import QObject, QTimer

from src.storage.database import ClipboardDatabase
from src.storage.image_store import delete_images


class CleanupScheduler(QObject):
    """每小时检查一次，清理过期记录"""

    def __init__(self, db: ClipboardDatabase, storage_days: int, parent=None):
        super().__init__(parent)
        self._db = db
        self._storage_days = storage_days

        self._timer = QTimer()
        self._timer.setInterval(60 * 60 * 1000)  # 每小时
        self._timer.timeout.connect(self.run)

    def set_storage_days(self, days: int):
        self._storage_days = days

    def start(self):
        # 启动 5 秒后先执行一次
        QTimer.singleShot(5000, self.run)
        self._timer.start()

    def stop(self):
        self._timer.stop()

    def run(self):
        cutoff = (datetime.now() - timedelta(days=self._storage_days)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        try:
            image_paths = self._db.delete_old_items(cutoff, exclude_pinned=True)
            for path in image_paths:
                if path:
                    try:
                        import os
                        img_dir = os.path.dirname(path)
                        item_id = int(os.path.basename(path).split(".")[0])
                        delete_images(item_id)
                    except Exception:
                        pass
        except Exception:
            pass
