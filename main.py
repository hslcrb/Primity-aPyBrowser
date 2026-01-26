import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from src.browser import PrimityBrowser

# Set environment variables for Korean IME (fcitx) support on Linux
os.environ["QT_IM_MODULE"] = "fcitx"
os.environ["XMODIFIERS"] = "@im=fcitx"

# CRITICAL: Point to system Qt6 plugins to enable fcitx input context in virtual environment
system_plugin_path = "/usr/lib/x86_64-linux-gnu/qt6/plugins"
if os.path.exists(system_plugin_path):
    # PREPEND to existing plugin paths
    current_paths = os.environ.get("QT_PLUGIN_PATH", "")
    if current_paths:
        os.environ["QT_PLUGIN_PATH"] = f"{system_plugin_path}:{current_paths}"
    else:
        os.environ["QT_PLUGIN_PATH"] = system_plugin_path

def main():
    # Attempt to fix IME issues on Linux (Native windows often help with IME composition)
    QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, True)
    QApplication.setAttribute(Qt.AA_NativeWindows, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Primity")
    
    # Ensure system plugin path is also in the app's library paths
    if os.path.exists(system_plugin_path):
        app.addLibraryPath(system_plugin_path)
    
    window = PrimityBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
