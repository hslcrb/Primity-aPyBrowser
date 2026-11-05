"""일반 탐색 페이지에는 네이티브 브리지를 노출하지 않는다. / No native web bridge."""

from PySide6.QtCore import Signal
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

from src.core.navigation import is_web_url
from src.ui.dialogs import confirm


class BrowserPage(QWebEnginePage):
    blocked_navigation = Signal(str)

    def __init__(self, profile, window, parent=None):
        super().__init__(profile, parent)
        self.window = window
        self.newWindowRequested.connect(self._new_window)
        self.permissionRequested.connect(self._permission)
        self.certificateError.connect(self._certificate_error)
        self.windowCloseRequested.connect(lambda: window.close_page(self))

    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        if url.toString() == "about:blank" or is_web_url(url.toString()):
            return True
        if is_main_frame:
            self.blocked_navigation.emit(url.scheme())
        return False

    def _certificate_error(self, error):
        error.rejectCertificate()
        self.blocked_navigation.emit("TLS")

    def _new_window(self, request):
        url = request.requestedUrl().toString()
        if url and url != "about:blank" and not is_web_url(url):
            self.blocked_navigation.emit(request.requestedUrl().scheme())
            return
        if not request.isUserInitiated() and not confirm(
                self.window, self.window.t("새 창 요청", "Popup request"),
                self.window.t("이 사이트에서 새 탭을 열까요?", "Allow this site to open a new tab?")
                + "\n\n" + self.url().toDisplayString()):
            return
        # openIn은 opener와 팝업 탐색을 보존한다. / Preserve OAuth opener relationships.
        request.openIn(self.window.new_popup_page())

    def _permission(self, permission):
        if not permission.isValid():
            return
        origin = permission.origin().toDisplayString()
        kind = permission.permissionType().name
        allowed = confirm(self.window, self.window.t("사이트 권한", "Site permission"),
                          f"{origin}\n\n{kind}\n\n" + self.window.t(
                              "이 작업공간에서 허용할까요?", "Allow in this workspace?"))
        if permission.isValid():
            permission.grant() if allowed else permission.deny()


class BrowserView(QWebEngineView):
    def __init__(self, profile, window, parent=None):
        super().__init__(parent)
        self.setPage(BrowserPage(profile, window, self))

