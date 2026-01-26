import sys
from PySide6.QtWidgets import QApplication
from src.browser import PrimityBrowser

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Primity")
    window = PrimityBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
