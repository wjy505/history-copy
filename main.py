"""历史粘贴板 — 入口文件"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from src.app.application import Application


def check_single_instance() -> bool:
    """使用 Win32 互斥体确保单实例运行"""
    try:
        import win32event
        import win32api
        import winerror

        mutex = win32event.CreateMutex(None, False, "ClipboardHistory_SingleInstance")
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            return False
        return True
    except Exception:
        return True  # 如果 win32 API 不可用，允许运行


def main():
    if not check_single_instance():
        QApplication(sys.argv)  # 需要先创建 QApplication 才能显示对话框
        QMessageBox.information(
            None,
            "历史粘贴板",
            "历史粘贴板已在运行中。\n请查看系统托盘图标。",
        )
        sys.exit(0)

    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("历史粘贴板")
    app.setOrganizationName("ClipboardHistory")
    app.setQuitOnLastWindowClosed(False)

    application = Application()
    application.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
