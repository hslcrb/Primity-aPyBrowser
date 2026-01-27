# IME Configuration: 使用 Internal JS-based IME engine (Primity Omni-Engine).
# System IME integration removed to prevent conflicts.

import sys
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from src.core.browser import PrimityBrowser

def main():
    # 리눅스 X11 한글 입력 호환성 속성
    # Force Software OpenGL to prevent Segfaults on some Linux drivers
    QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    
    # Chromium 엔진용 한글 입력 및 최신 기술(HTTP/3) 활성화 플래그
    sys.argv.append("--no-sandbox")
    sys.argv.append("--disable-setuid-sandbox")
    # sys.argv.append("--ozone-platform=x11") # Let Qt decide, remove rigid flag
    sys.argv.append("--disable-gpu")
    
    # Stability Flags (Prevent Segfaults on Linux)
    sys.argv.append("--disable-gpu") 
    sys.argv.append("--single-process")
    sys.argv.append("--no-zygote")
    
    # HTTP/3 (QUIC) Support
    sys.argv.append("--enable-quic")
    sys.argv.append("--origin-to-force-quic-on=*")
    
    # Archiving Excellence Flags (CORS bypass, etc.)
    sys.argv.append("--disable-web-security")
    sys.argv.append("--allow-running-insecure-content")
    sys.argv.append("--autoplay-policy=no-user-gesture-required")
    sys.argv.append("--allow-file-access-from-files")
    sys.argv.append("--test-type")
    sys.argv.append("--disable-site-isolation-trials")
    sys.argv.append("--disable-features=IsolateOrigins,site-per-process")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Primity")
    
    window = PrimityBrowser()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
