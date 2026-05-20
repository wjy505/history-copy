"""系统托盘图标和菜单"""
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject


class SystemTray(QObject):
    """系统托盘管理"""

    show_requested = Signal()
    settings_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tray = QSystemTrayIcon(parent=None)
        self._tray.setToolTip("历史粘贴板")

        # 图标：尝试加载资源文件，失败则使用系统默认图标
        icon = self._load_icon()
        self._tray.setIcon(icon)

        # 菜单
        menu = QMenu()
        show_action = QAction("显示历史面板", menu)
        show_action.triggered.connect(self.show_requested.emit)
        menu.addAction(show_action)

        menu.addSeparator()

        settings_action = QAction("设置...", menu)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)

        menu.addSeparator()

        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)

        # 左键点击显示面板
        self._tray.activated.connect(self._on_activated)

    def _load_icon(self) -> QIcon:
        """加载图标，优先用自定义图标，回退到系统图标"""
        import os
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        ico_path = os.path.join(app_dir, "resources", "icon.ico")
        if os.path.exists(ico_path):
            return QIcon(ico_path)
        # 用系统内置图标回退
        return QIcon.fromTheme("edit-copy")

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_requested.emit()

    def show(self):
        self._tray.show()

    def hide(self):
        self._tray.hide()

    def set_count(self, count: int):
        self._tray.setToolTip(f"历史粘贴板 - {count} 条记录")

    def show_message(self, title: str, message: str):
        self._tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)

    def is_visible(self) -> bool:
        return self._tray.isVisible()
