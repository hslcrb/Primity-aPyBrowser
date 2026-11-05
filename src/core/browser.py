"""작업공간 중심 브라우저. / A familiar browser with isolated workspaces."""

from collections import deque
import json
from pathlib import Path

from PySide6.QtCore import QObject, QCoreApplication, QEvent, QStandardPaths, Qt, QUrl, QTimer
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (QMainWindow, QToolBar, QLineEdit, QTabWidget, QStatusBar,
                               QPushButton, QMenu, QVBoxLayout, QWidget, QHBoxLayout,
                               QLabel, QFileDialog, QInputDialog, QProgressBar, QProgressDialog)
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineDownloadRequest
from PySide6.QtWebEngineWidgets import QWebEngineView
from shiboken6 import isValid

from src.core.chrome_launcher import launch_chrome
from src.core.navigation import NEW_TAB, address_to_url, is_web_url
from src.core.profiles import ProfileRegistry
from src.core.webpage import BrowserView
from src.core.workspaces import MAX_JSON_BYTES, WorkspaceError
from src.ui.dialogs import confirm, inform
from src.ui.workspace_widgets import NewTabPage, workspace_stylesheet

ASSETS = Path(__file__).resolve().parents[2] / "assets"


class BrowserController(QObject):
    """페이지를 먼저 정리하고 프로필을 해제한다. / Profiles outlive all their pages."""

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.registry = ProfileRegistry(store, self)
        self.registry.download_requested.connect(self._download)
        self.windows = []
        self._shutting_down = False

    def open_workspace(self, workspace_id=None, url=None, *, new_window=False):
        ident = workspace_id or self.store.active_id
        workspace = self.store.get(ident)
        window = None if new_window else next(
            (w for w in self.windows if isValid(w) and not w._closing
             and not w.private and w.workspace.id == ident), None)
        if window is None:
            window = self._new_window(workspace, self.registry.get(ident), False)
        self.store.set_active(ident)
        if url is not None:
            window.add_new_tab(url)
        window.showNormal() if window.isMinimized() else window.show()
        window.raise_()
        window.activateWindow()
        return window

    def open_private(self, workspace_id):
        window = self._new_window(self.store.get(workspace_id), self.registry.private(), True)
        window.show()
        return window

    def _new_window(self, workspace, profile, private):
        window = PrimityBrowser(self, workspace, profile, private=private)
        self.windows.append(window)
        window.destroyed.connect(lambda: self._forget_window(window, profile, private))
        return window

    def _forget_window(self, window, profile, private):
        if window in self.windows:
            self.windows.remove(window)
        if private and not self._shutting_down and isValid(self.registry):
            # 자식 페이지 삭제가 끝난 다음 해제한다. / Defer until child pages are gone.
            QTimer.singleShot(0, lambda: self.registry.release_private(profile)
                              if isValid(self.registry) else None)

    def refresh_workspace(self, ident):
        for window in list(self.windows):
            if isValid(window) and not window._closing and window.workspace.id == ident:
                window.refresh_workspace()

    def _download(self, download):
        page = download.page()
        window = getattr(page, "window", None) if page is not None else None
        if window is None or not isValid(window) or window._closing:
            download.cancel()
        else:
            window.accept_download(download)

    def shutdown(self):
        if self._shutting_down:
            return
        self._shutting_down = True
        for window in list(self.windows):
            if isValid(window):
                window._closing = True
                window.dispose_tabs()
                window.deleteLater()
        self.windows.clear()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        if isValid(self.registry):
            self.registry.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


class PrimityBrowser(QMainWindow):
    def __init__(self, controller, workspace, profile, *, private=False):
        super().__init__()
        self.controller, self.workspace, self.profile = controller, workspace, profile
        self.store, self.private = controller.store, private
        self._closing = False
        self._closed_tabs = deque(maxlen=20)
        self._downloads = []
        self._translated_actions = []
        preferences = self.store.preferences(workspace.id)
        self.language, self.theme = preferences["language"], preferences["theme"]
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(QIcon(str(ASSETS / "icons/globe.svg")))
        self.resize(1280, 840)
        self.setMinimumSize(780, 520)
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setCentralWidget(central)
        self.navbar = QToolBar()
        self.navbar.setMovable(False)
        layout.addWidget(self.navbar)
        self.back_action = self._nav("←", ("뒤로", "Back"), lambda: self.with_view("back"), "Alt+Left")
        self.forward_action = self._nav("→", ("앞으로", "Forward"), lambda: self.with_view("forward"), "Alt+Right")
        self.reload_action = self._nav("↻", ("새로고침 / 중지", "Reload / Stop"), self.reload_or_stop, "Ctrl+R")
        self._nav("⌂", ("새 탭 페이지", "New tab page"), lambda: self.add_new_tab())
        self.url_bar = QLineEdit()
        self.url_bar.setMinimumWidth(220)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)
        self.bookmark_action = self._nav("☆", ("북마크 저장 / 해제", "Bookmark / Remove bookmark"),
                                         self.toggle_bookmark, "Ctrl+D")
        self.workspace_button = QPushButton()
        self.workspace_button.setObjectName("WorkspaceButton")
        self.workspace_button.clicked.connect(self.show_workspace_menu)
        self.navbar.addWidget(self.workspace_button)
        self.menu_button = QPushButton("⋮")
        self.menu_button.clicked.connect(self.show_menu)
        self.navbar.addWidget(self.menu_button)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(3)
        self.progress.hide()
        layout.addWidget(self.progress)
        self.find_bar = QWidget()
        find_layout = QHBoxLayout(self.find_bar)
        find_layout.addStretch()
        self.find_edit = QLineEdit()
        self.find_edit.setMaximumWidth(340)
        self.find_edit.returnPressed.connect(self.find_next)
        find_layout.addWidget(self.find_edit)
        for text, handler in (("↑", lambda: self.find_next(backward=True)),
                              ("↓", self.find_next), ("×", self.close_find)):
            button = QPushButton(text)
            button.clicked.connect(handler)
            find_layout.addWidget(button)
        self.find_bar.hide()
        layout.addWidget(self.find_bar)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabBar().setExpanding(False)
        self.tabs.tabBar().setElideMode(Qt.ElideRight)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_navigation)
        self.tabs.tabBarDoubleClicked.connect(lambda i: self.add_new_tab() if i == -1 else None)
        plus = QPushButton("+")
        plus.setFixedSize(36, 32)
        plus.setAccessibleName("New tab")
        plus.clicked.connect(lambda: self.add_new_tab())
        self.tabs.setCornerWidget(plus, Qt.TopRightCorner)
        layout.addWidget(self.tabs, 1)
        self.setStatusBar(QStatusBar())
        self.connection_label = QLabel()
        self.connection_label.setTextFormat(Qt.PlainText)
        self.statusBar().addPermanentWidget(self.connection_label)
        self._install_shortcuts()
        self.refresh_workspace(rebuild=False)
        self.add_new_tab()

    def t(self, korean, english):
        return korean if self.language == "ko" else english

    def _nav(self, text, labels, callback, shortcut=None):
        action = QAction(text, self)
        action.triggered.connect(callback)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        self._translated_actions.append((action, labels))
        self.addAction(action)
        self.navbar.addAction(action)
        return action

    def _shortcut(self, sequence, callback):
        action = QAction(self)
        action.setShortcut(QKeySequence(sequence))
        action.triggered.connect(callback)
        self.addAction(action)

    def _install_shortcuts(self):
        for sequence, callback in (
            ("Ctrl+L", self.focus_address), ("Ctrl+T", lambda: self.add_new_tab()),
            ("Ctrl+W", lambda: self.close_current_tab(self.tabs.currentIndex())),
            ("Ctrl+Shift+T", self.restore_closed_tab),
            ("Ctrl+N", self.new_window),
            ("Ctrl+Shift+N", self.new_private_window),
            ("Ctrl+Tab", lambda: self.cycle_tab(1)), ("Ctrl+Shift+Tab", lambda: self.cycle_tab(-1)),
            ("Ctrl+F", self.open_find), ("Escape", self.escape),
            ("F5", lambda: self.with_view("reload")), ("Ctrl+=", lambda: self.zoom(0.1)),
            ("Ctrl++", lambda: self.zoom(0.1)), ("Ctrl+-", lambda: self.zoom(-0.1)),
            ("Ctrl+0", lambda: self.zoom(reset=True)), ("F11", self.toggle_fullscreen),
        ):
            self._shortcut(sequence, callback)
        for number in range(1, 10):
            self._shortcut(f"Ctrl+{number}", lambda n=number: self.tabs.setCurrentIndex(
                self.tabs.count() - 1 if n == 9 else min(n - 1, self.tabs.count() - 1)))

    def active_view(self):
        widget = self.tabs.currentWidget()
        return widget if isinstance(widget, QWebEngineView) else None

    def with_view(self, method):
        view = self.active_view()
        if view:
            getattr(view, method)()

    def focus_address(self):
        self.url_bar.setFocus()
        self.url_bar.selectAll()

    def cycle_tab(self, direction):
        if self.tabs.count():
            self.tabs.setCurrentIndex((self.tabs.currentIndex() + direction) % self.tabs.count())

    def add_new_tab(self, url=None, *, focus=True):
        url = url.toString(QUrl.FullyEncoded) if isinstance(url, QUrl) else url
        widget = self._new_tab_widget() if url is None or url == NEW_TAB else self._make_view()
        index = self.tabs.addTab(widget, self.t("새 탭", "New tab"))
        if focus:
            self.tabs.setCurrentIndex(index)
        if isinstance(widget, QWebEngineView):
            widget.setUrl(QUrl(url))
        elif focus:
            widget.search.setFocus()
        return widget

    def _new_tab_widget(self):
        page = NewTabPage(self.workspace, self.language, self.private)
        page.navigate.connect(self.navigate_to_url)
        page.create_workspace.connect(self.create_workspace)
        page.chrome_requested.connect(self.open_chrome)
        return page

    def _make_view(self):
        view = BrowserView(self.profile, self)
        view._loading = False
        view.loadStarted.connect(lambda: self._loading(view, True))
        view.loadProgress.connect(lambda value: self.progress.setValue(value) if self.active_view() is view else None)
        view.loadFinished.connect(lambda ok: self._loaded(view, ok))
        view.urlChanged.connect(lambda url: self.update_navigation() if self.active_view() is view else None)
        view.titleChanged.connect(lambda title: self._title_changed(view, title))
        view.iconChanged.connect(lambda icon: self.tabs.setTabIcon(self.tabs.indexOf(view), icon)
                                 if self.tabs.indexOf(view) >= 0 else None)
        view.page().blocked_navigation.connect(lambda kind: self.statusBar().showMessage(
            self.t("주소 또는 인증서가 차단되었습니다: ", "Address or certificate was blocked: ") + kind, 6000))
        view.page().linkHovered.connect(lambda url: self.statusBar().showMessage(url))
        # 기록 상태는 URL 신호 뒤에 바뀔 수 있다. / Follow Chromium navigation actions.
        for action_type in (QWebEnginePage.Back, QWebEnginePage.Forward):
            view.page().action(action_type).changed.connect(self.update_navigation)
        view.renderProcessTerminated.connect(lambda *args: self.statusBar().showMessage(
            self.t("페이지 엔진이 종료되었습니다. 새로고침해 주세요.", "Page renderer stopped. Reload to retry."), 10000))
        return view

    def new_popup_page(self):
        return self.add_new_tab("about:blank").page()

    def close_page(self, page):
        for index in range(self.tabs.count()):
            view = self.tabs.widget(index)
            if isinstance(view, QWebEngineView) and view.page() is page:
                self.close_current_tab(index)
                return

    def _loading(self, view, active):
        view._loading = active
        if view is self.active_view():
            self.progress.setVisible(active)
            self.reload_action.setText("×" if active else "↻")

    def _loaded(self, view, ok):
        self._loading(view, False)
        if view is self.active_view():
            self.update_navigation()
            if not ok:
                self.statusBar().showMessage(self.t("페이지를 불러오지 못했거나 탐색이 중지되었습니다.",
                                                     "Page load failed or navigation was stopped."), 5000)

    def _title_changed(self, view, title):
        index = self.tabs.indexOf(view)
        if index >= 0:
            self.tabs.setTabText(index, title[:60] or self.t("새 탭", "New tab"))
            self.tabs.setTabToolTip(index, title)
        if view is self.active_view():
            self._update_title()

    def _update_title(self):
        view = self.active_view()
        title = view.title()[:100] if view else "Primity"
        private = self.t(" · 시크릿", " · Private") if self.private else ""
        self.setWindowTitle(f"{title} — {self.workspace.name}{private} — Primity")

    def update_navigation(self, *_):
        if self._closing or not hasattr(self, "connection_label"):
            return
        view = self.active_view()
        url = view.url().toString(QUrl.FullyEncoded) if view else NEW_TAB
        if not self.url_bar.hasFocus():
            self.url_bar.setText("" if url in {NEW_TAB, "about:blank"} else url)
        self.back_action.setEnabled(bool(view and view.history().canGoBack()))
        self.forward_action.setEnabled(bool(view and view.history().canGoForward()))
        self.reload_action.setEnabled(view is not None)
        self.bookmark_action.setEnabled(not self.private and is_web_url(url))
        self.progress.setVisible(bool(view and view._loading))
        self.reload_action.setText("×" if view and view._loading else "↻")
        self.connection_label.setText((view.url().scheme().upper() if view else "Primity")
                                     + " · " + self.workspace.name
                                     + (self.t(" · 시크릿", " · Private") if self.private else ""))
        self._update_title()
        try:
            starred = any(item["url"] == url for item in self.store.bookmarks(self.workspace.id))
            self.bookmark_action.setText("★" if starred else "☆")
        except WorkspaceError as error:
            self.statusBar().showMessage(str(error), 5000)

    def navigate_to_url(self, text=None):
        try:
            url = address_to_url(text if isinstance(text, str) else self.url_bar.text())
        except ValueError as error:
            self.statusBar().showMessage(str(error), 6000)
            return
        if url == NEW_TAB:
            self.add_new_tab()
            return
        view = self.active_view()
        if view is None:
            index = self.tabs.currentIndex()
            old = self.tabs.widget(index)
            self.tabs.removeTab(index)
            if old:
                old.deleteLater()
            view = self._make_view()
            self.tabs.insertTab(max(index, 0), view, self.t("불러오는 중…", "Loading…"))
            self.tabs.setCurrentWidget(view)
        view.setFocus()
        view.setUrl(QUrl(url))

    def reload_or_stop(self):
        view = self.active_view()
        if view:
            view.stop() if view._loading else view.reload()

    def close_current_tab(self, index):
        if index < 0 or index >= self.tabs.count():
            return
        if self.tabs.count() == 1:
            self.close()
            return
        widget = self.tabs.widget(index)
        if isinstance(widget, QWebEngineView):
            if is_web_url(widget.url().toString(QUrl.FullyEncoded)):
                self._closed_tabs.append(widget.url().toString(QUrl.FullyEncoded))
            widget.stop()
        self.tabs.removeTab(index)
        widget.deleteLater()

    def restore_closed_tab(self):
        return self.add_new_tab(self._closed_tabs.pop()) if self._closed_tabs else None

    def open_find(self):
        if self.active_view():
            self.find_edit.setPlaceholderText(self.t("페이지에서 찾기", "Find in page"))
            self.find_bar.show()
            self.find_edit.setFocus()
            self.find_edit.selectAll()

    def find_next(self, *_, backward=False):
        view = self.active_view()
        if view:
            view.findText(self.find_edit.text(), QWebEnginePage.FindBackward if backward
                          else QWebEnginePage.FindFlags())

    def close_find(self):
        if self.active_view():
            self.active_view().findText("")
        self.find_bar.hide()

    def escape(self):
        if self.isFullScreen():
            self.showNormal()
        elif self.find_bar.isVisible():
            self.close_find()
        else:
            self.with_view("stop")

    def zoom(self, delta=0, *, reset=False):
        if self.active_view():
            view = self.active_view()
            view.setZoomFactor(1.0 if reset else max(0.25, min(3.0, view.zoomFactor() + delta)))
            self.statusBar().showMessage(f"{round(view.zoomFactor() * 100)}%", 1500)

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def request_workspace(self, ident, *, new_window=False):
        try:
            return self.controller.open_workspace(ident, new_window=new_window)
        except (WorkspaceError, OSError) as error:
            inform(self, "Primity", str(error), error=True)
            return None

    def new_private_window(self):
        try:
            return self.controller.open_private(self.workspace.id)
        except (WorkspaceError, OSError) as error:
            inform(self, "Primity", str(error), error=True)
            return None

    def new_window(self):
        return self.new_private_window() if self.private else self.request_workspace(
            self.workspace.id, new_window=True)

    def show_workspace_menu(self):
        menu = QMenu(self)
        for workspace in self.store.list():
            action = menu.addAction(workspace.name)
            action.setCheckable(True)
            action.setChecked(workspace.id == self.workspace.id and not self.private)
            action.triggered.connect(lambda checked=False, ident=workspace.id: self.request_workspace(ident))
        menu.addSeparator()
        menu.addAction(self.t("+ 새 작업공간", "+ New workspace"), self.create_workspace)
        menu.addAction(self.t("이 작업공간 이름 변경", "Rename this workspace"), self.rename_workspace)
        menu.addAction(self.t("새 시크릿 창", "New private window"), self.new_private_window)
        menu.exec(self.workspace_button.mapToGlobal(self.workspace_button.rect().bottomLeft()))
        menu.deleteLater()

    def create_workspace(self):
        name, ok = QInputDialog.getText(self, self.t("새 작업공간", "New workspace"),
                                       self.t("이름 (예: 디자인 B)", "Name (e.g. Design B)"))
        if ok:
            try:
                self.controller.open_workspace(self.store.create(name).id)
            except WorkspaceError as error:
                inform(self, "Primity", str(error), error=True)

    def rename_workspace(self):
        name, ok = QInputDialog.getText(self, self.t("이름 변경", "Rename workspace"),
                                       self.t("작업공간 이름", "Workspace name"), text=self.workspace.name)
        if ok:
            try:
                self.store.rename(self.workspace.id, name)
                self.controller.refresh_workspace(self.workspace.id)
            except WorkspaceError as error:
                inform(self, "Primity", str(error), error=True)

    def refresh_workspace(self, *, rebuild=True):
        self.workspace = self.store.get(self.workspace.id)
        if not self.private:
            preferences = self.store.preferences(self.workspace.id)
            self.language, self.theme = preferences["language"], preferences["theme"]
        self.setStyleSheet(workspace_stylesheet(self.theme))
        label = self.workspace.name[:18] + ("…" if len(self.workspace.name) > 18 else "")
        self.workspace_button.setText(("◌ " if self.private else "◯ ") + label
                                      + (self.t(" · 시크릿", " · Private") if self.private else ""))
        self.workspace_button.setToolTip(self.t("작업공간 선택 · ", "Choose workspace · ") + self.workspace.name)
        self.workspace_button.setAccessibleName(self.workspace.name)
        self.url_bar.setPlaceholderText(self.t("검색 또는 주소 입력 · Ctrl+L", "Search or enter address · Ctrl+L"))
        self.url_bar.setAccessibleName(self.t("주소 또는 검색", "Address or search"))
        self.menu_button.setAccessibleName(self.t("메뉴", "Menu"))
        for action, labels in self._translated_actions:
            action.setToolTip(self.t(*labels))
        if rebuild:
            current = self.tabs.currentIndex()
            for index in range(self.tabs.count()):
                old = self.tabs.widget(index)
                if isinstance(old, NewTabPage):
                    self.tabs.removeTab(index)
                    old.deleteLater()
                    self.tabs.insertTab(index, self._new_tab_widget(), self.t("새 탭", "New tab"))
            self.tabs.setCurrentIndex(current)
        self.update_navigation()

    def change_appearance(self, *, theme=None, language=None):
        self.theme, self.language = theme or self.theme, language or self.language
        if self.private:
            self.refresh_workspace()
        else:
            try:
                self.store.save_preferences(self.workspace.id, theme=self.theme, language=self.language)
                self.controller.refresh_workspace(self.workspace.id)
            except WorkspaceError as error:
                inform(self, "Primity", str(error), error=True)

    def show_menu(self):
        menu = QMenu(self)
        menu.addAction(self.t("새 탭", "New tab"), lambda: self.add_new_tab())
        menu.addAction(self.t("닫은 탭 다시 열기", "Reopen closed tab"), self.restore_closed_tab)
        menu.addAction(self.t("새 창", "New window"), self.new_window)
        menu.addAction(self.t("새 시크릿 창", "New private window"), self.new_private_window)
        menu.addSeparator()
        bookmarks = menu.addMenu(self.t("이 작업공간의 북마크", "Workspace bookmarks"))
        try:
            for item in self.store.bookmarks(self.workspace.id):
                action = bookmarks.addAction(item["title"])
                action.triggered.connect(lambda checked=False, url=item["url"]: self.add_new_tab(url))
            if bookmarks.isEmpty():
                bookmarks.addAction(self.t("저장된 북마크 없음", "No saved bookmarks")).setEnabled(False)
        except WorkspaceError as error:
            bookmarks.addAction(str(error)).setEnabled(False)
        bookmarks.addSeparator()
        bookmarks.addAction(self.t("JSON 가져오기…", "Import JSON…"), self.import_bookmarks).setEnabled(not self.private)
        bookmarks.addAction(self.t("JSON 내보내기…", "Export JSON…"), self.export_bookmarks).setEnabled(not self.private)
        menu.addAction(self.t("페이지에서 찾기", "Find in page"), self.open_find)
        menu.addAction(self.t("라이트 / 다크 테마", "Light / dark theme"),
                       lambda: self.change_appearance(theme="light" if self.theme == "dark" else "dark"))
        menu.addAction("한국어 / English",
                       lambda: self.change_appearance(language="en" if self.language == "ko" else "ko"))
        menu.addSeparator()
        menu.addAction(self.t("Chrome으로 연결 · 독립 프로필", "Open in Chrome · isolated profile"),
                       self.open_chrome).setEnabled(not self.private)
        menu.addAction(self.t("계정 분리 안내", "About account isolation"), self.show_about)
        menu.exec(self.menu_button.mapToGlobal(self.menu_button.rect().bottomLeft()))
        menu.deleteLater()

    def toggle_bookmark(self):
        view = self.active_view()
        if self.private or view is None or not is_web_url(view.url().toString(QUrl.FullyEncoded)):
            return
        url = view.url().toString(QUrl.FullyEncoded)
        try:
            items = self.store.bookmarks(self.workspace.id)
            if any(item["url"] == url for item in items):
                items = [item for item in items if item["url"] != url]
            else:
                items.append({"title": (view.title() or url)[:256], "url": url})
            self.store.save_bookmarks(self.workspace.id, items)
            self.controller.refresh_workspace(self.workspace.id)
        except WorkspaceError as error:
            inform(self, "Primity", str(error), error=True)

    def import_bookmarks(self):
        if self.private:
            return
        filename, _ = QFileDialog.getOpenFileName(self, self.t("북마크 가져오기", "Import bookmarks"), "", "JSON (*.json)")
        if not filename:
            return
        try:
            path = Path(filename)
            if path.stat().st_size > MAX_JSON_BYTES:
                raise WorkspaceError(self.t("2 MB 이하 파일만 가져올 수 있습니다.", "Import files up to 2 MB."))
            count = self.store.import_bookmarks(self.workspace.id, json.loads(path.read_text(encoding="utf-8")))
            self.controller.refresh_workspace(self.workspace.id)
            self.statusBar().showMessage(self.t(f"북마크 {count}개 저장됨", f"{count} bookmarks saved"), 5000)
        except (OSError, ValueError, UnicodeError, RecursionError) as error:
            inform(self, "Primity", str(error), error=True)

    def export_bookmarks(self):
        if self.private:
            return
        filename, _ = QFileDialog.getSaveFileName(self, self.t("북마크 내보내기", "Export bookmarks"),
                                                 "primity-bookmarks.json", "JSON (*.json)")
        if filename:
            try:
                Path(filename).write_text(json.dumps(self.store.export_bookmarks(self.workspace.id),
                                                     ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            except (OSError, ValueError) as error:
                inform(self, "Primity", str(error), error=True)

    def open_chrome(self):
        if self.private:
            return
        message = self.t(
            "Google Chrome을 작업공간 전용 프로필로 엽니다.\n\n일반 Chrome과 분리되며 Primity의 로그인도 복사하지 않습니다. 여기에서 별도로 로그인하세요. Chrome 자체 동기화는 열린 Chrome의 프로필 메뉴에서 설정할 수 있습니다.\n\n계속할까요?",
            "Open installed Google Chrome with a profile dedicated to this workspace.\n\nNormal Chrome stays separate. Primity sign-ins are not copied; sign in again. Chrome Sync is configured in Chrome's own profile menu.\n\nContinue?")
        if confirm(self, self.t("Chrome 연결", "Chrome connection"), message):
            view = self.active_view()
            url = view.url().toString(QUrl.FullyEncoded) if view and is_web_url(view.url().toString(QUrl.FullyEncoded)) else "https://www.google.com/"
            try:
                launch_chrome(self.store.path(self.workspace.id, "chrome"), url)
                self.statusBar().showMessage(self.t("Chrome 실행을 요청했습니다.", "Chrome launch requested."), 5000)
            except (OSError, ValueError) as error:
                inform(self, "Primity", str(error), error=True)

    def show_about(self):
        inform(self, "Primity 0.3.0", self.t(
            "쿠키, 웹 저장소, 캐시와 북마크를 작업공간마다 분리합니다. 사이트의 로그인 만료 정책은 유지됩니다. 권한 선택은 앱 종료 후 초기화됩니다.\n\nGoogle 웹 로그인과 Chrome 동기화는 별개입니다. 임베디드 로그인을 지원하지 않는 사이트는 Chrome 연결을 이용하세요. Qt와 Chrome의 로그인은 서로 공유되지 않습니다.\n\n브라우저 데이터 분리이며 같은 OS 사용자의 다른 프로그램에 대한 보안 격리는 아닙니다.",
            "Workspaces separate cookies, web storage, cache and bookmarks. Site session expiration still applies. Permission choices reset after exit.\n\nGoogle sign-in and Chrome Sync differ. Use Chrome connection for sites that reject embedded sign-in. Qt and Chrome sessions are not shared.\n\nThis is browser-data isolation, not an OS security boundary."))

    def accept_download(self, download):
        destination = Path(QStandardPaths.writableLocation(QStandardPaths.DownloadLocation) or str(Path.home()))
        suggested = Path(download.downloadFileName()).name or "download"
        filename, _ = QFileDialog.getSaveFileName(self, self.t("다운로드 저장", "Save download"),
                                                 str(destination / suggested))
        if not filename:
            download.cancel()
            return
        path = Path(filename)
        download.setDownloadDirectory(str(path.parent))
        download.setDownloadFileName(path.name)
        progress = QProgressDialog(path.name, self.t("취소", "Cancel"), 0, 100, self)
        progress.setWindowTitle(self.workspace.name + " · " + self.t("다운로드", "Download"))
        progress.setWindowModality(Qt.NonModal)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.canceled.connect(download.cancel)
        self._downloads.append(download)

        def update():
            if not isValid(progress):
                return
            total, received = download.totalBytes(), download.receivedBytes()
            progress.setRange(0, 100 if total > 0 else 0)
            if total > 0:
                progress.setValue(min(100, int(received * 100 / total)))
            progress.setLabelText(f"{path.name}\n{received:,} / {total:,} bytes" if total > 0
                                  else f"{path.name}\n{received:,} bytes")
            if download.isFinished():
                progress.close()
                progress.deleteLater()
                if download in self._downloads:
                    self._downloads.remove(download)
                if not self._closing:
                    complete = download.state() == QWebEngineDownloadRequest.DownloadCompleted
                    self.statusBar().showMessage((self.t("다운로드 완료: ", "Download complete: ") if complete else
                                                  self.t("다운로드 중단: ", "Download stopped: ")) + path.name, 7000)

        download.receivedBytesChanged.connect(update)
        download.totalBytesChanged.connect(update)
        download.stateChanged.connect(update)
        download.isFinishedChanged.connect(update)
        download.accept()
        progress.show()

    def dispose_tabs(self):
        for download in list(self._downloads):
            if isValid(download) and not download.isFinished():
                download.cancel()
        self._downloads.clear()
        while self.tabs.count():
            widget = self.tabs.widget(0)
            self.tabs.removeTab(0)
            if isinstance(widget, QWebEngineView):
                widget.stop()
            widget.deleteLater()

    def closeEvent(self, event):
        active = any(isValid(item) and not item.isFinished() for item in self._downloads)
        if active and not confirm(self, "Primity", self.t("다운로드를 취소하고 닫을까요?",
                                                        "Cancel active downloads and close?")):
            event.ignore()
            return
        self._closing = True
        self.dispose_tabs()
        event.accept()

