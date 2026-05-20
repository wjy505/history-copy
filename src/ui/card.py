"""历史卡片组件"""
from datetime import datetime

from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget,
)
from PySide6.QtCore import Signal, Qt, QEvent
from PySide6.QtGui import QPixmap, QMouseEvent


def format_time(iso_string: str) -> str:
    try:
        dt = datetime.strptime(iso_string, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return iso_string
    now = datetime.now()
    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "刚刚"
    elif seconds < 3600:
        return f"{int(seconds / 60)} 分钟前"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} 小时前"
    elif seconds < 172800:
        return f"昨天 {dt.strftime('%H:%M')}"
    elif seconds < 604800:
        return f"{int(seconds / 86400)} 天前"
    else:
        return dt.strftime("%Y-%m-%d %H:%M")


CARD_STYLE = """
    QFrame#clipCard {
        background: #FFFFFF;
        border: 1px solid #E5E8EC;
        border-radius: 6px;
    }
    QFrame#clipCard:hover {
        background: #F8FAFB;
        border-color: #C0C8D0;
    }
"""

PINNED_CARD_STYLE = """
    QFrame#clipCard {
        background: #FFFFFF;
        border: 1px solid #E5E8EC;
        border-left: 3px solid #4A90D9;
        border-radius: 6px;
        border-top-left-radius: 3px;
        border-bottom-left-radius: 3px;
    }
    QFrame#clipCard:hover {
        background: #F8FAFB;
        border-color: #C0C8D0;
        border-left: 3px solid #4A90D9;
    }
"""

DELETE_STYLE = """
    QFrame#clipCard {
        background: #FFF0F0;
        border: 1px solid #E74C3C;
        border-radius: 6px;
    }
"""


class ClipboardCard(QFrame):
    double_clicked = Signal(int)
    pin_toggled = Signal(int, bool)
    delete_requested = Signal(int)

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self._item = item
        self._delete_clicks = 0
        self.setObjectName("clipCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()
        self._build_ui()

    def _apply_style(self):
        if self._item.is_pinned:
            self.setStyleSheet(PINNED_CARD_STYLE)
        else:
            self.setStyleSheet(CARD_STYLE)

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 8, 8)
        main_layout.setSpacing(8)

        if self._item.content_type == "image" and self._item.thumbnail_path:
            content = self._build_image_widget()
        else:
            content = self._build_text_widget()

        # 安装事件过滤器，让子控件的双击事件能传到卡片
        content.installEventFilter(self)
        self._content_widget = content

        main_layout.addWidget(content, 1)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(2)

        pin_text = "📌" if self._item.is_pinned else "📍"
        pin_btn = QPushButton(pin_text)
        pin_btn.setFixedSize(24, 24)
        pin_btn.setToolTip("取消置顶" if self._item.is_pinned else "置顶")
        pin_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; font-size: 13px; }"
            "QPushButton:hover { background: #E8F0FE; border-radius: 4px; }"
        )
        pin_btn.clicked.connect(self._on_pin)
        btn_layout.addWidget(pin_btn)

        delete_btn = QPushButton("✕")
        delete_btn.setFixedSize(24, 24)
        delete_btn.setToolTip("删除")
        delete_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; color: #999; font-size: 13px; }"
            "QPushButton:hover { background: #FEE8E8; color: #E74C3C; border-radius: 4px; }"
        )
        delete_btn.clicked.connect(self._on_delete)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

    def _build_text_widget(self):
        from PySide6.QtWidgets import QWidget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        text = self._item.text_content or "(空)"
        preview = text[:200].replace("\n", " ").replace("\r", "")
        label = QLabel(preview)
        label.setWordWrap(True)
        label.setMaximumHeight(60)
        label.setToolTip(text[:500])
        label.setStyleSheet("color: #2C3E50; font-size: 12px;")
        layout.addWidget(label)

        time_label = QLabel(format_time(self._item.created_at))
        time_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        layout.addWidget(time_label)

        return widget

    def _build_image_widget(self):
        from PySide6.QtWidgets import QWidget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        pixmap = QPixmap(self._item.thumbnail_path)
        if pixmap.width() > 200:
            pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
        img_label = QLabel()
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(img_label)

        time_label = QLabel(f"📷 {format_time(self._item.created_at)}")
        time_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        layout.addWidget(time_label)

        return widget

    def _on_pin(self):
        pinned = not self._item.is_pinned
        self.pin_toggled.emit(self._item.id, pinned)

    def _on_delete(self):
        self._delete_clicks += 1
        if self._delete_clicks == 1:
            self.setStyleSheet(DELETE_STYLE)
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1500, self._reset_delete_state)
        else:
            self.delete_requested.emit(self._item.id)

    def _reset_delete_state(self):
        self._delete_clicks = 0
        self._apply_style()

    def eventFilter(self, obj, event):
        """将子控件的双击事件转发到卡片"""
        if event.type() == QEvent.Type.MouseButtonDblClick:
            self.double_clicked.emit(self._item.id)
            return True
        return super().eventFilter(obj, event)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit(self._item.id)
        if event is not None:
            super().mouseDoubleClickEvent(event)

    def update_item(self, item):
        self._item = item
        self._delete_clicks = 0
        self._apply_style()
