"""设置对话框"""
import os

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QCheckBox, QMessageBox, QLineEdit,
)
from PySide6.QtCore import Qt, Signal

from src.ui.theme import TEXT_PRIMARY, PRIMARY, PRIMARY_DARK, DANGER, BORDER


class SettingsDialog(QDialog):
    """设置窗口"""

    hotkey_changed = Signal(str)
    duration_changed = Signal(int)
    clear_all_requested = Signal()
    start_with_windows_changed = Signal(bool)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self._config = config
        self._capturing_hotkey = False
        self._new_hotkey = config.hotkey

        self.setWindowTitle("设置")
        self.setFixedSize(340, 280)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # 标题
        title = QLabel("设置")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TEXT_PRIMARY};")
        layout.addWidget(title)

        # 存储期限
        dur_layout = QHBoxLayout()
        dur_label = QLabel("存储期限:")
        dur_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        self._duration_combo = QComboBox()
        self._duration_combo.addItems(["1 天", "3 天", "5 天"])
        idx = {1: 0, 3: 1, 5: 2}.get(config.storage_duration_days, 1)
        self._duration_combo.setCurrentIndex(idx)
        self._duration_combo.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px 8px;
                color: {TEXT_PRIMARY};
            }}
        """)
        dur_layout.addWidget(dur_label)
        dur_layout.addWidget(self._duration_combo, 1)
        layout.addLayout(dur_layout)

        # 快捷键
        hk_layout = QHBoxLayout()
        hk_label = QLabel("快捷键:")
        hk_label.setStyleSheet(f"color: {TEXT_PRIMARY};")
        self._hotkey_btn = QPushButton(config.hotkey)
        self._hotkey_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 4px 16px;
                color: {TEXT_PRIMARY};
                background: white;
            }}
            QPushButton:hover {{
                border-color: {PRIMARY};
            }}
        """)
        self._hotkey_btn.clicked.connect(self._start_capture_hotkey)
        hk_layout.addWidget(hk_label)
        hk_layout.addWidget(self._hotkey_btn, 1)
        layout.addLayout(hk_layout)

        # 开机启动
        self._startup_check = QCheckBox("开机时自动启动")
        self._startup_check.setChecked(config.start_with_windows)
        self._startup_check.setStyleSheet(f"color: {TEXT_PRIMARY};")
        layout.addWidget(self._startup_check)

        # 清空历史
        clear_btn = QPushButton("清空所有历史记录")
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {DANGER};
                border-radius: 4px;
                padding: 6px 16px;
                color: {DANGER};
                background: white;
            }}
            QPushButton:hover {{
                background: #FFF0F0;
            }}
        """)
        clear_btn.clicked.connect(self._on_clear_all)
        layout.addWidget(clear_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        # 确认/取消
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {BORDER};
                border-radius: 4px;
                padding: 6px 20px;
                color: {TEXT_PRIMARY};
                background: white;
            }}
            QPushButton:hover {{
                background: #F5F5F5;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("确认")
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: 4px;
                padding: 6px 20px;
                background: {PRIMARY};
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {PRIMARY_DARK};
            }}
        """)
        ok_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def _start_capture_hotkey(self):
        self._capturing_hotkey = True
        self._hotkey_btn.setText("按下新快捷键...")
        self.setFocus()

    def keyPressEvent(self, event):
        if self._capturing_hotkey:
            modifiers = event.modifiers()
            key = event.key()
            parts = []
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                parts.append("ctrl")
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                parts.append("shift")
            if modifiers & Qt.KeyboardModifier.AltModifier:
                parts.append("alt")

            # 获取按键名
            key_map = {
                Qt.Key.Key_A: "a", Qt.Key.Key_B: "b", Qt.Key.Key_C: "c",
                Qt.Key.Key_D: "d", Qt.Key.Key_E: "e", Qt.Key.Key_F: "f",
                Qt.Key.Key_G: "g", Qt.Key.Key_H: "h", Qt.Key.Key_I: "i",
                Qt.Key.Key_J: "j", Qt.Key.Key_K: "k", Qt.Key.Key_L: "l",
                Qt.Key.Key_M: "m", Qt.Key.Key_N: "n", Qt.Key.Key_O: "o",
                Qt.Key.Key_P: "p", Qt.Key.Key_Q: "q", Qt.Key.Key_R: "r",
                Qt.Key.Key_S: "s", Qt.Key.Key_T: "t", Qt.Key.Key_U: "u",
                Qt.Key.Key_V: "v", Qt.Key.Key_W: "w", Qt.Key.Key_X: "x",
                Qt.Key.Key_Y: "y", Qt.Key.Key_Z: "z",
                Qt.Key.Key_0: "0", Qt.Key.Key_1: "1", Qt.Key.Key_2: "2",
                Qt.Key.Key_3: "3", Qt.Key.Key_4: "4", Qt.Key.Key_5: "5",
                Qt.Key.Key_6: "6", Qt.Key.Key_7: "7", Qt.Key.Key_8: "8",
                Qt.Key.Key_9: "9",
                Qt.Key.Key_Space: "space",
            }
            key_str = key_map.get(key, "")
            if key_str and parts:
                parts.append(key_str)
                self._new_hotkey = "+".join(parts)
                self._hotkey_btn.setText(self._new_hotkey)
                self._capturing_hotkey = False
        else:
            super().keyPressEvent(event)

    def _on_confirm(self):
        # 存储期限
        days_map = {0: 1, 1: 3, 2: 5}
        new_days = days_map[self._duration_combo.currentIndex()]
        self.duration_changed.emit(new_days)

        # 快捷键
        if self._new_hotkey != self._config.hotkey:
            self.hotkey_changed.emit(self._new_hotkey)

        # 开机启动
        self.start_with_windows_changed.emit(self._startup_check.isChecked())

        self.accept()

    def _on_clear_all(self):
        reply = QMessageBox.question(
            self, "确认清空",
            "确定要删除所有历史记录吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_all_requested.emit()
