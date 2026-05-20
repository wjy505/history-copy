"""淡蓝色主题 QSS 样式表"""
from PySide6.QtGui import QColor, QPalette

# 色彩常量
PRIMARY = "#4A90D9"
PRIMARY_DARK = "#357ABD"
BACKGROUND = "#F0F4F8"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#2C3E50"
TEXT_SECONDARY = "#7F8C8D"
ACCENT = "#5DADE2"
DANGER = "#E74C3C"
BORDER = "#D5DDE5"
HOVER_BG = "#F8FAFB"
PIN_BORDER = "#4A90D9"


def get_stylesheet() -> str:
    return """
/* 全局 */
* {
    font-family: "Microsoft YaHei", "微软雅黑", sans-serif;
    font-size: 13px;
}

/* 面板窗口 */
QWidget#panel {
    background-color: #F0F4F8;
    border: 1px solid #D5DDE5;
    border-radius: 8px;
}

/* 滚动区域 */
QScrollArea {
    border: none;
    background: transparent;
}

QScrollArea > QWidget > QWidget {
    background: transparent;
}

QScrollBar:vertical {
    width: 6px;
    background: transparent;
    border: none;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #C0CCD8;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #8FA0B0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

/* 搜索栏 */
QLineEdit#searchBar {
    background: #FFFFFF;
    border: 1px solid #D5DDE5;
    border-radius: 18px;
    padding: 8px 16px;
    font-size: 13px;
    color: #2C3E50;
}

QLineEdit#searchBar:focus {
    border-color: #4A90D9;
}

QLineEdit#searchBar::placeholder {
    color: #B0BEC5;
}

/* 卡片 */
QFrame#card {
    background: #FFFFFF;
    border: 1px solid #D5DDE5;
    border-radius: 6px;
    padding: 10px 12px;
}

QFrame#card:hover {
    background: #F8FAFB;
    border-color: #B8C8D8;
}

QFrame#card[pinned="true"] {
    border-left: 3px solid #4A90D9;
}

/* 文字内容 */
QLabel#contentLabel {
    color: #2C3E50;
    font-size: 12px;
    line-height: 1.5;
}

QLabel#timeLabel {
    color: #7F8C8D;
    font-size: 10px;
}

QLabel#appLabel {
    color: #A0AEC0;
    font-size: 10px;
}

/* 按钮 */
QPushButton#pinBtn, QPushButton#deleteBtn {
    background: transparent;
    border: none;
    border-radius: 4px;
    padding: 4px;
    font-size: 14px;
}

QPushButton#pinBtn:hover {
    background: #E8F0FE;
}

QPushButton#pinBtn[active="true"] {
    color: #4A90D9;
    font-weight: bold;
}

QPushButton#deleteBtn:hover {
    background: #FEE8E8;
    color: #E74C3C;
}

/* 确认按钮 */
QPushButton#confirmBtn {
    background: #4A90D9;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 20px;
    font-weight: bold;
}

QPushButton#confirmBtn:hover {
    background: #357ABD;
}

/* 菜单 */
QMenu {
    background: #FFFFFF;
    border: 1px solid #D5DDE5;
    border-radius: 4px;
    padding: 4px 0;
}

QMenu::item {
    padding: 8px 32px;
    color: #2C3E50;
}

QMenu::item:selected {
    background: #E8F0FE;
    color: #4A90D9;
}

QMenu::separator {
    height: 1px;
    background: #D5DDE5;
    margin: 4px 12px;
}

/* 对话框 */
QDialog {
    background: #FFFFFF;
    border-radius: 8px;
}

QLabel#dialogTitle {
    font-size: 16px;
    font-weight: bold;
    color: #2C3E50;
}

/* 下拉框 */
QComboBox {
    background: #FFFFFF;
    border: 1px solid #D5DDE5;
    border-radius: 4px;
    padding: 6px 12px;
    color: #2C3E50;
}

QComboBox:hover {
    border-color: #4A90D9;
}

QComboBox QAbstractItemView {
    background: #FFFFFF;
    border: 1px solid #D5DDE5;
    selection-background-color: #E8F0FE;
    selection-color: #4A90D9;
}

/* 复选框 */
QCheckBox {
    color: #2C3E50;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #D5DDE5;
    border-radius: 3px;
    background: #FFFFFF;
}

QCheckBox::indicator:checked {
    background: #4A90D9;
    border-color: #4A90D9;
}

/* 工具提示 */
QToolTip {
    background: #2C3E50;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 11px;
}
"""


def apply_light_blue_palette(app):
    """设置 Qt 调色板为基础淡蓝色风格"""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BACKGROUND))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(CARD_BG))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(BACKGROUND))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(CARD_BG))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(CARD_BG))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(PRIMARY))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(CARD_BG))
    app.setPalette(palette)
