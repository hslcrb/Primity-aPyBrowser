from PySide6.QtWidgets import QFrame

class MinimalCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MinimalCard")

DARK_STYLE = """
QMainWindow {
    background: #000000;
}
QTabWidget::pane {
    border: 1px solid #333333;
    background: #000000;
}
QTabBar::tab {
    background: #000000;
    color: #888888;
    padding: 10px 15px;
    border: 1px solid #333333;
    border-bottom: none;
    margin-right: 1px;
}
QTabBar::tab:selected {
    background: #111111;
    color: #ffffff;
    border-top: 2px solid #ffffff;
}
QToolBar {
    background: #000000;
    border: none;
    border-bottom: 1px solid #333333;
    padding: 5px;
    spacing: 5px;
}
QLineEdit {
    background: #111111;
    color: #ffffff;
    border: 1px solid #333333;
    padding: 5px 10px;
    border-radius: 0px;
}
QToolButton {
    background: transparent;
    color: #ffffff;
    border: none;
    padding: 4px;
}
QToolButton:hover {
    background: #333333;
}
QToolButton:pressed {
    background: #555555;
}
QStatusBar {
    background: #000000;
    color: #666666;
    border-top: 1px solid #333333;
}
QMenu {
    background: #000000;
    color: #ffffff;
    border: 1px solid #333333;
}
QMenu::item:selected {
    background: #333333;
}
#MinimalCard {
    background: #000000;
    border: 1px solid #333333;
    border-radius: 0px;
}
#InternalList {
    background: #000000;
    border: 1px solid #333333;
    color: #ffffff;
}
#PrimaryButton, #SecondaryButton, #DangerButton {
    background: #000000;
    color: #ffffff;
    border: 1px solid #ffffff;
    padding: 8px 15px;
    border-radius: 0px;
}
#PrimaryButton:hover, #SecondaryButton:hover, #DangerButton:hover {
    background: #ffffff;
    color: #000000;
}
QLabel {
    color: #ffffff;
}
"""

LIGHT_STYLE = """
QMainWindow {
    background: #ffffff;
}
QTabWidget::pane {
    border: 1px solid #dddddd;
    background: #ffffff;
}
QTabBar::tab {
    background: #ffffff;
    color: #888888;
    padding: 10px 15px;
    border: 1px solid #dddddd;
    border-bottom: none;
    margin-right: 1px;
}
QTabBar::tab:selected {
    background: #f8f8f8;
    color: #000000;
    border-top: 2px solid #000000;
}
QToolBar {
    background: #ffffff;
    border: none;
    border-bottom: 1px solid #dddddd;
    padding: 5px;
    spacing: 5px;
}
QLineEdit {
    background: #ffffff;
    color: #000000;
    border: 1px solid #cccccc;
    padding: 5px 10px;
    border-radius: 0px;
}
QToolButton {
    background: transparent;
    color: #000000;
    border: none;
    padding: 4px;
}
QToolButton:hover {
    background: #eeeeee;
}
QToolButton:pressed {
    background: #dddddd;
}
QStatusBar {
    background: #ffffff;
    color: #999999;
    border-top: 1px solid #dddddd;
}
QMenu {
    background: #ffffff;
    color: #000000;
    border: 1px solid #dddddd;
}
QMenu::item:selected {
    background: #eeeeee;
}
#MinimalCard {
    background: #ffffff;
    border: 1px solid #dddddd;
    border-radius: 0px;
}
#InternalList {
    background: #ffffff;
    border: 1px solid #dddddd;
    color: #000000;
}
#PrimaryButton, #SecondaryButton, #DangerButton {
    background: #ffffff;
    color: #000000;
    border: 1px solid #000000;
    padding: 8px 15px;
    border-radius: 0px;
}
#PrimaryButton:hover, #SecondaryButton:hover, #DangerButton:hover {
    background: #000000;
    color: #ffffff;
}
QLabel {
    color: #000000;
}
"""
