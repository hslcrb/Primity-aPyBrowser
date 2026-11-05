import os
import sys
import pytest


@pytest.fixture(scope="session")
def qapp():
    if (sys.platform.startswith("linux") and not os.environ.get("DISPLAY")
            and not os.environ.get("WAYLAND_DISPLAY")
            and os.environ.get("QT_QPA_PLATFORM") not in {"offscreen", "minimal"}):
        pytest.fail("Qt GUI 테스트에는 디스플레이 또는 QT_QPA_PLATFORM=offscreen이 필요합니다.")
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(["primity-tests"])
    yield app

