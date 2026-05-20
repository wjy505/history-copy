"""历史面板主窗口"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QPushButton, QApplication,
)
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve, QTimer

from src.storage.database import ClipboardItem
from src.ui.card import ClipboardCard
from src.ui.search_bar import SearchBar
from src.ui.theme import TEXT_PRIMARY, TEXT_SECONDARY, BORDER


class HistoryPanel(QWidget):
    """历史面板 — 可呼出/隐藏的面板窗口"""

    paste_requested = Signal(int)
    pin_toggled = Signal(int, bool)
    delete_requested = Signal(int)
    search_requested = Signal(str)
    load_more_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self.setWindowTitle("历史粘贴板")
        self.setWindowFlags(
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.resize(400, 600)

        self._cards: list[ClipboardCard] = []
        self._current_page = 0
        self._has_more = True

        self._build_ui()
        self._apply_panel_style()

    def _apply_panel_style(self):
        """直接设置面板样式 — 白色背景黑色文字"""
        self.setStyleSheet(f"""
            QWidget#panel {{
                background-color: #FFFFFF;
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
            QWidget#panel QWidget {{
                background-color: transparent;
            }}
            QWidget#cardContainer {{
                background-color: transparent;
            }}
            QLabel#cardContent {{
                color: {TEXT_PRIMARY};
                font-size: 12px;
            }}
            QLabel#cardTime {{
                color: {TEXT_SECONDARY};
                font-size: 11px;
            }}
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background: #F5F5F5;
                width: 6px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: #CCCCCC;
                border-radius: 3px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #AAAAAA;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 6)
        layout.setSpacing(0)

        # 搜索栏
        self._search_bar = SearchBar()
        self._search_bar.search_changed.connect(self._on_search)
        layout.addWidget(self._search_bar)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        self._card_container = QWidget()
        self._card_container.setObjectName("cardContainer")
        self._card_layout = QVBoxLayout(self._card_container)
        self._card_layout.setContentsMargins(8, 4, 8, 4)
        self._card_layout.setSpacing(6)
        self._card_layout.addStretch()

        scroll.setWidget(self._card_container)
        layout.addWidget(scroll, 1)

        # 加载更多按钮
        self._load_more_btn = QPushButton("加载更多...")
        self._load_more_btn.setStyleSheet(f"""
            QPushButton {{
                background: #4A90D9;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #357ABD;
            }}
        """)
        self._load_more_btn.clicked.connect(self._load_more)
        self._load_more_btn.hide()
        layout.addWidget(self._load_more_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # 空状态提示
        self._empty_label = QLabel("暂无剪贴板记录\n\n按 Ctrl+C 复制任意内容开始记录")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {TEXT_SECONDARY}; padding: 60px 20px; font-size: 14px;")

    def show_panel(self):
        if self.isVisible():
            self.hide_panel()
            return
        self._current_page = 0
        self._has_more = True
        # 静默清空搜索栏（不触发搜索信号）
        self._search_bar.blockSignals(True)
        self._search_bar._clear()
        self._search_bar.blockSignals(False)
        # 定位到鼠标附近
        cursor_pos = self.cursor().pos()
        x = cursor_pos.x() - self.width() // 2
        y = cursor_pos.y() - self.height() // 2
        screen = QApplication.screenAt(cursor_pos)
        if screen:
            geo = screen.availableGeometry()
            x = max(geo.left(), min(x, geo.right() - self.width()))
            y = max(geo.top(), min(y, geo.bottom() - self.height()))
        self.move(x, y)
        self._fade_in()
        self._search_bar.set_focus()

    def hide_panel(self):
        self._fade_out()

    def _fade_in(self):
        self.setWindowOpacity(0.0)
        self.show()
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(180)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.start()

    def _fade_out(self):
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(120)
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self._anim.finished.connect(self.hide)
        self._anim.start()

    def set_items(self, items: list[ClipboardItem], has_more: bool = False):
        if self._current_page == 0:
            self._clear_cards()

        for item in items:
            card = ClipboardCard(item)
            card.double_clicked.connect(lambda iid=item.id: self.paste_requested.emit(iid))
            card.pin_toggled.connect(self.pin_toggled.emit)
            card.delete_requested.connect(self.delete_requested.emit)
            self._cards.append(card)
            self._card_layout.insertWidget(self._card_layout.count() - 1, card)

        self._has_more = has_more
        self._load_more_btn.setVisible(has_more)
        self._update_empty_state()

    def _clear_cards(self):
        for card in self._cards:
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()

    def _update_empty_state(self):
        if len(self._cards) == 0:
            self._card_layout.insertWidget(0, self._empty_label)
        else:
            self._empty_label.setParent(None)

    def _load_more(self):
        self._current_page += 1
        self.load_more_requested.emit()

    def _on_search(self, query: str):
        self._current_page = 0
        self._clear_cards()
        self.search_requested.emit(query)

    def refresh_card(self, item_id: int, item: ClipboardItem):
        for card in self._cards:
            if card._item.id == item_id:
                card.update_item(item)
                break

    def remove_card(self, item_id: int):
        for card in self._cards:
            if card._item.id == item_id:
                card.setParent(None)
                card.deleteLater()
                self._cards.remove(card)
                break
        self._update_empty_state()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide_panel()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        QTimer.singleShot(200, self._check_focus)

    def _check_focus(self):
        # 如果面板不再活跃且没有子窗口打开，隐藏
        if not self.isActiveWindow() and self.isVisible():
            # 检查是否有模态对话框打开
            from PySide6.QtWidgets import QApplication
            for widget in QApplication.topLevelWidgets():
                if widget.isModal() and widget.isVisible():
                    return
            self.hide_panel()
