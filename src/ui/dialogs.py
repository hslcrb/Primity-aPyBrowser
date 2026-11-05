"""사이트가 제공한 문자열도 평문으로 표시. / Render untrusted UI text as plain text."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox


def confirm(parent, title, text):
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setTextFormat(Qt.PlainText)
    box.setText(text)
    box.setIcon(QMessageBox.Question)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    box.setDefaultButton(QMessageBox.No)
    return box.exec() == QMessageBox.Yes


def inform(parent, title, text, *, error=False):
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setTextFormat(Qt.PlainText)
    box.setText(text)
    box.setIcon(QMessageBox.Warning if error else QMessageBox.Information)
    box.exec()

