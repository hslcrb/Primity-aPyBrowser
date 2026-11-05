"""A fresh-process persistence probe using only the parent's loopback fixture."""

from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from PySide6.QtCore import QCoreApplication, QEvent, QTimer, QUrl
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

from src.core.profiles import ProfileRegistry
from src.core.workspaces import WorkspaceStore

app = QApplication(["profile-session-probe"])
store = WorkspaceStore(Path(sys.argv[1]))
registry = ProfileRegistry(store)
view = QWebEngineView()
view.setPage(QWebEnginePage(registry.get(store.active_id), view))
completed = False


def finish(value):
    global completed
    completed = True
    print("RESULT=" + value, flush=True)
    view.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    registry.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    app.quit()


def loaded(ok):
    if not ok:
        app.exit(2)
        return
    source = ""
    if sys.argv[3] == "write":
        source = "document.cookie='account=persistent-A; path=/; max-age=86400';localStorage.setItem('account','persistent-A');"
    source += "JSON.stringify({cookie:document.cookie,storage:localStorage.getItem('account')})"
    view.page().runJavaScript(source, 0, finish)


view.loadFinished.connect(loaded)
view.setUrl(QUrl(sys.argv[2]))
QTimer.singleShot(20000, lambda: app.exit(3) if not completed else None)
raise SystemExit(app.exec())
