import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from src.browser import PrimityBrowser

# Set environment variables for Korean IME (fcitx) support on Linux
os.environ["QT_IM_MODULE"] = "fcitx"
os.environ["XMODIFIERS"] = "@im=fcitx"

def main():
    # Attempt to fix IME issues on Linux
    QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Primity")
    
    window = PrimityBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
