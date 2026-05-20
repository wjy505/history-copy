"""应用控制器 — 管理所有子系统的生命周期"""
import os
import sys

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QApplication

from src.storage.config import ConfigManager
from src.storage.database import ClipboardDatabase
from src.clipboard.monitor import ClipboardMonitor
from src.ui.theme import apply_light_blue_palette, get_stylesheet
from src.ui.tray import SystemTray
from src.ui.panel import HistoryPanel
from src.hotkey.manager import HotkeyManager
from src.cleanup.scheduler import CleanupScheduler


ITEMS_PER_PAGE = 30


class Application(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = ConfigManager()
        self._db: ClipboardDatabase | None = None
        self._monitor: ClipboardMonitor | None = None
        self._tray: SystemTray | None = None
        self._panel: HistoryPanel | None = None
        self._hotkey: HotkeyManager | None = None
        self._cleanup: CleanupScheduler | None = None
        self._current_search = ""

    def start(self):
        app = QApplication.instance()
        apply_light_blue_palette(app)
        app.setStyleSheet(get_stylesheet())

        # 数据库
        self._db = ClipboardDatabase()
        self._db.open()

        # 面板
        self._panel = HistoryPanel()
        self._panel.paste_requested.connect(self._on_paste)
        self._panel.pin_toggled.connect(self._on_pin_toggle)
        self._panel.delete_requested.connect(self._on_delete)
        self._panel.search_requested.connect(self._on_search)
        self._panel.load_more_requested.connect(self._on_load_more)

        # 全局热键
        self._hotkey = HotkeyManager()
        self._hotkey.triggered.connect(self._on_hotkey)
        self._hotkey.register(self._config.hotkey)

        # 定时清理
        self._cleanup = CleanupScheduler(self._db, self._config.storage_duration_days)
        self._cleanup.start()

        # 系统托盘
        self._tray = SystemTray()
        self._tray.show_requested.connect(self._on_show_panel)
        self._tray.settings_requested.connect(self._on_settings)
        self._tray.quit_requested.connect(self._on_quit)
        self._tray.show()
        self._tray.set_count(self._db.get_item_count())

        # 剪贴板监听
        self._monitor = ClipboardMonitor()
        self._monitor.new_item.connect(self._on_new_item)
        self._monitor.start()

    # ——— 剪贴板 ———

    def _on_new_item(self, data: dict):
        if self._db is None:
            return
        try:
            content_type = data["type"]
            content_hash = data["hash"]

            if self._db.is_duplicate(content_hash):
                return

            if content_type == "text":
                self._db.insert_item(
                    content_type="text",
                    text_content=data["text"],
                    content_hash=content_hash,
                )
            elif content_type == "image":
                from src.storage.image_store import save_image
                item_id = self._db.insert_item(
                    content_type="image",
                    content_hash=content_hash,
                )
                image = data["image"]
                img_path, thumb_path = save_image(
                    image, item_id, max_width=self._config.max_image_width
                )
                self._db.conn.execute(
                    "UPDATE clipboard_items SET image_path = ?, thumbnail_path = ? WHERE id = ?",
                    (img_path, thumb_path, item_id),
                )
                self._db.conn.commit()

            self._tray.set_count(self._db.get_item_count())
        except Exception:
            pass

    # ——— 热键 ———

    def _on_hotkey(self):
        self._on_show_panel()

    # ——— 面板 ———

    def _on_show_panel(self):
        if self._panel is None:
            return
        if self._panel.isVisible():
            self._panel.hide_panel()
            return
        self._panel.show_panel()
        self._current_search = ""
        self._load_panel_data()

    def _load_panel_data(self, page: int = 0):
        if self._db is None or self._panel is None:
            return
        offset = page * ITEMS_PER_PAGE
        search = self._current_search if self._current_search else None
        items = self._db.get_items(limit=ITEMS_PER_PAGE, offset=offset, search_query=search)
        total = self._db.get_item_count()
        has_more = (offset + ITEMS_PER_PAGE) < total if not search else len(items) == ITEMS_PER_PAGE
        self._panel.set_items(items, has_more=has_more)

    def _on_search(self, query: str):
        self._current_search = query
        self._load_panel_data(page=0)

    def _on_load_more(self):
        page = self._panel._current_page if self._panel else 0
        self._load_panel_data(page=page)

    def _on_paste(self, item_id: int):
        if self._db is None:
            return
        item = self._db.get_item_by_id(item_id)
        if item is None:
            return

        if item.content_type == "text" and item.text_content:
            from src.clipboard.writer import write_text
            write_text(item.text_content)
            self._db.update_accessed(item_id)
        elif item.content_type == "image" and item.image_path:
            from src.clipboard.writer import write_image
            from PIL import Image
            try:
                img = Image.open(item.image_path)
                write_image(img)
                self._db.update_accessed(item_id)
            except Exception:
                pass

        if self._panel:
            self._panel.hide_panel()

        import keyboard
        QTimer.singleShot(200, lambda: keyboard.send("ctrl+v"))

    def _on_pin_toggle(self, item_id: int, pinned: bool):
        if self._db is None:
            return
        self._db.pin_item(item_id, pinned)
        if self._panel and self._panel.isVisible():
            item = self._db.get_item_by_id(item_id)
            if item:
                self._panel.refresh_card(item_id, item)
            self._tray.set_count(self._db.get_item_count())

    def _on_delete(self, item_id: int):
        if self._db is None:
            return
        from src.storage.image_store import delete_images
        image_path = self._db.delete_item(item_id)
        if image_path:
            delete_images(item_id)
        if self._panel:
            self._panel.remove_card(item_id)
        self._tray.set_count(self._db.get_item_count())

    # ——— 设置 ———

    def _on_settings(self):
        from src.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self._config)
        dialog.duration_changed.connect(self._on_duration_changed)
        dialog.hotkey_changed.connect(self._on_hotkey_changed)
        dialog.clear_all_requested.connect(self._on_clear_all)
        dialog.start_with_windows_changed.connect(self._on_startup_changed)
        dialog.exec()

    def _on_duration_changed(self, days: int):
        self._config.set("storage_duration_days", days)
        if self._cleanup:
            self._cleanup.set_storage_days(days)
        if self._tray:
            self._tray.show_message("历史粘贴板", f"存储期限已设为 {days} 天")

    def _on_hotkey_changed(self, hotkey_str: str):
        self._config.set("hotkey", hotkey_str)
        if self._hotkey:
            self._hotkey.register(hotkey_str)
        if self._tray:
            self._tray.show_message("历史粘贴板", f"快捷键已设为 {hotkey_str}")

    def _on_clear_all(self):
        if self._db is None:
            return
        try:
            from src.storage.image_store import delete_all_images
            self._db.delete_all()
            delete_all_images()
            if self._panel:
                self._panel._clear_cards()
                self._panel._update_empty_state()
            if self._tray:
                self._tray.set_count(0)
                self._tray.show_message("历史粘贴板", "所有历史记录已清空")
        except Exception:
            pass

    def _on_startup_changed(self, enabled: bool):
        self._config.set("start_with_windows", enabled)
        startup_dir = os.path.join(
            os.getenv("APPDATA", ""),
            "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
        )
        shortcut_path = os.path.join(startup_dir, "ClipboardHistory.lnk")
        if enabled:
            try:
                from win32com.client import Dispatch
                shell = Dispatch("WScript.Shell")
                shortcut = shell.CreateShortcut(shortcut_path)
                shortcut.TargetPath = sys.executable
                project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                shortcut.Arguments = os.path.join(project_dir, "main.py")
                shortcut.WorkingDirectory = project_dir
                shortcut.save()
            except Exception:
                pass
        else:
            try:
                if os.path.exists(shortcut_path):
                    os.remove(shortcut_path)
            except Exception:
                pass

    # ——— 退出 ———

    def _on_quit(self):
        if self._cleanup:
            self._cleanup.stop()
        if self._hotkey:
            self._hotkey.unregister()
        if self._monitor:
            self._monitor.stop()
        if self._db:
            self._db.close()
        QApplication.instance().quit()
