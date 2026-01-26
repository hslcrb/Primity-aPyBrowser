import sys
import os

# 1. 포괄적인 IME 환경 변수 설정 (fcitx 최우선)
env_vars = {
    "QT_IM_MODULE": "fcitx",
    "GTK_IM_MODULE": "fcitx",
    "XMODIFIERS": "@im=fcitx",
    "QT4_IM_MODULE": "fcitx",
    "CLUTTER_IM_MODULE": "fcitx",
    "QT_QPA_PLATFORM": "xcb",      # X11 환경 강제
    "SDL_IM_MODULE": "fcitx",
    "GLFW_IM_MODULE": "ibus"       # ibus 호환성 필요한 경우 대비
}
for key, value in env_vars.items():
    os.environ[key] = value

# 2. 시스템 Qt 플러그인 경로 탐색 및 추가 (가상환경 IME 미작동 방지)
plugin_paths = [
    "/usr/lib/x86_64-linux-gnu/qt6/plugins",
    "/usr/lib/qt6/plugins",
    "/usr/lib64/qt6/plugins"
]
for path in plugin_paths:
    if os.path.exists(path):
        current = os.environ.get("QT_PLUGIN_PATH", "")
        os.environ["QT_PLUGIN_PATH"] = f"{path}:{current}" if current else path
        break

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from src.browser import PrimityBrowser

def main():
    # 3. 네이티브 이벤트 핸들링 최적화
    # DontCreateNativeWidgetSiblings를 False로 하여 네이티브 윈도우와의 통신 복구
    QApplication.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, False)
    QApplication.setAttribute(Qt.AA_NativeWindows, True)
    
    # 4. Chromium 입력 관련 플래그 최적화
    sys.argv.append("--ozone-platform=x11")
    sys.argv.append("--enable-wayland-ime") # 혹시 모를 내부 레이어 대비
    sys.argv.append("--gtk-version=3")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Primity")
    
    # Library Path에도 시스템 경로 추가
    for path in plugin_paths:
        if os.path.exists(path):
            app.addLibraryPath(path)
    
    window = PrimityBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
