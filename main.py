import sys
import os

# IME(한글 입력기) 설정을 최상단으로 이동 (어플리케이션 시작 전 적용 필수)
os.environ["QT_IM_MODULE"] = "fcitx"
os.environ["GTK_IM_MODULE"] = "fcitx"
os.environ["XMODIFIERS"] = "@im=fcitx"
os.environ["QT_QPA_PLATFORM"] = "xcb"

# PySide6 내부 런타임에 시스템 Qt 플러그인을 직접 주입
# 가상환경(.venv)은 시스템 설치된 입력기 플러그인을 못 찾는 경우가 많음
venv_plugin_path = os.path.join(os.path.dirname(__file__), ".venv/lib/python3.12/site-packages/PySide6/Qt/plugins/platforminputcontexts")
system_plugin = "/usr/lib/x86_64-linux-gnu/qt6/plugins/platforminputcontexts/libfcitxplatforminputcontextplugin-qt6.so"

if os.path.exists(system_plugin) and os.path.exists(venv_plugin_path):
    import shutil
    dest = os.path.join(venv_plugin_path, "libfcitxplatforminputcontextplugin-qt6.so")
    if not os.path.exists(dest):
        try:
            shutil.copy(system_plugin, dest)
            print("INFO: Fcitx IME plugin successfully integrated into venv.")
        except Exception as e:
            print(f"WARN: Failed to copy IME plugin: {e}")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from src.browser import PrimityBrowser

def main():
    # 리눅스 X11 한글 입력 호환성 속성
    QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, False)
    QApplication.setAttribute(Qt.AA_NativeWindows, True)
    
    # Chromium 엔진용 한글 입력 및 최신 기술(HTTP/3) 활성화 플래그
    sys.argv.append("--no-sandbox")
    sys.argv.append("--disable-setuid-sandbox")
    sys.argv.append("--ozone-platform=x11")
    sys.argv.append("--enable-wayland-ime") 
    sys.argv.append("--gtk-version=3")
    
    # HTTP/3 (QUIC) Support
    sys.argv.append("--enable-quic")
    sys.argv.append("--origin-to-force-quic-on=*")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Primity")
    
    window = PrimityBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
