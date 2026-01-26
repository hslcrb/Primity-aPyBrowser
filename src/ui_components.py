from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

def get_shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setXOffset(0)
    shadow.setYOffset(10)
    shadow.setColor(QColor(0, 0, 0, 150))
    return shadow

class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GlassCard")
        self.setGraphicsEffect(get_shadow())

STYLE_SHEET = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a2e, stop:1 #16213e);
}
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: rgba(255, 255, 255, 0.05);
    color: #b0b0b0;
    padding: 10px 20px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 2px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-bottom: none;
}
QTabBar::tab:selected {
    background: rgba(255, 255, 255, 0.15);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-bottom: none;
}
QToolBar {
    background: rgba(255, 255, 255, 0.05);
    border: none;
    padding: 8px;
    spacing: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
QLineEdit {
    background: rgba(0, 0, 0, 0.3);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 18px;
    padding: 5px 15px;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid rgba(255, 255, 255, 0.5);
    background: rgba(0, 0, 0, 0.5);
}
QStatusBar {
    background: rgba(0, 0, 0, 0.2);
    color: rgba(255, 255, 255, 0.5);
}
QMenu {
    background: rgba(26, 26, 46, 0.95);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}
QMenu::item {
    padding: 8px 25px;
}
QMenu::item:selected {
    background: rgba(255, 255, 255, 0.1);
}

#GlassCard {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 20px;
}

#InternalList {
    background: transparent;
    border: none;
    color: white;
    font-size: 14px;
}

#PrimaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4facfe, stop:1 #00f2fe);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 10px;
    font-weight: bold;
}
#SecondaryButton {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 10px 20px;
    border-radius: 10px;
}
#DangerButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff0844, stop:1 #ffb199);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 10px;
    font-weight: bold;
}
"""
