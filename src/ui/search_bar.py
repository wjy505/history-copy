"""搜索栏组件"""
from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QPushButton, QWidget
from PySide6.QtCore import Signal, QTimer


class SearchBar(QWidget):
    search_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #FFFFFF;")

        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(300)
        self._debounce_timer.timeout.connect(self._emit_search)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        icon_label = QPushButton("🔍")
        icon_label.setFlat(True)
        icon_label.setFixedSize(28, 28)
        icon_label.setStyleSheet("border: none; background: transparent; font-size: 14px;")

        self._input = QLineEdit()
        self._input.setPlaceholderText("搜索剪贴板历史...")
        self._input.setStyleSheet("""
            QLineEdit {
                background: #F5F6F8;
                border: 1px solid #E5E8EC;
                border-radius: 18px;
                padding: 8px 14px;
                font-size: 13px;
                color: #2C3E50;
            }
            QLineEdit:focus {
                border-color: #4A90D9;
                background: #FFFFFF;
            }
        """)
        self._input.textChanged.connect(self._on_text_changed)
        self._input.returnPressed.connect(self._emit_search_now)

        self._clear_btn = QPushButton("✕")
        self._clear_btn.setFlat(True)
        self._clear_btn.setFixedSize(24, 24)
        self._clear_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; color: #999; font-size: 12px; }"
            "QPushButton:hover { color: #333; }"
        )
        self._clear_btn.clicked.connect(self._clear)
        self._clear_btn.hide()

        layout.addWidget(icon_label)
        layout.addWidget(self._input, 1)
        layout.addWidget(self._clear_btn)

    def _on_text_changed(self, text):
        self._clear_btn.setVisible(bool(text))
        self._debounce_timer.start()

    def _emit_search(self):
        self.search_changed.emit(self._input.text())

    def _emit_search_now(self):
        self._debounce_timer.stop()
        self.search_changed.emit(self._input.text())

    def _clear(self):
        self._input.clear()
        self.search_changed.emit("")

    def set_focus(self):
        self._input.setFocus()
        self._input.selectAll()
