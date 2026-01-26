import sys
import os

# Set environment variables for Korean IME (fcitx) support on Linux
# We try to ensure Qt and Chromium both see the same input method
os.environ["QT_IM_MODULE"] = "fcitx"
os.environ["GTK_IM_MODULE"] = "fcitx"
os.environ["XMODIFIERS"] = "@im=fcitx"
os.environ["QT4_IM_MODULE"] = "fcitx"
os.environ["CLUTTER_IM_MODULE"] = "fcitx"

# Force X11 backend for reliability on Linux
os.environ["QT_QPA_PLATFORM"] = "xcb"

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from src.browser import PrimityBrowser

def main():
    # Attempt to fix IME issues on Linux (Native windows often help with IME composition)
    QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, True)
    QApplication.setAttribute(Qt.AA_NativeWindows, True)

    # Some Chromium flags that help with IME/Input on Linux
    sys.argv.append("--disable-features=UseOzonePlatform")
    sys.argv.append("--ignore-gpu-blocklist")
    sys.argv.append("--enable-threaded-compositing")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Primity")
    
    # Point to system Qt6 plugins to enable fcitx input context in virtual environment
    system_plugin_path = "/usr/lib/x86_64-linux-gnu/qt6/plugins"
    if os.path.exists(system_plugin_path):
        app.addLibraryPath(system_plugin_path)
    
    window = PrimityBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
