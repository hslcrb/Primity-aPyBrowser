"""일반 탐색 페이지에는 네이티브 브리지를 노출하지 않는다. / No native web bridge."""

from PySide6.QtCore import QUrl, Signal
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

from src.core.navigation import is_web_url
from src.ui.dialogs import confirm


def supports_document_url(url, *, main_frame=True):
    """웹 문서의 내장 프레임은 Chromium의 출처 정책을 따른다.
    Let Chromium enforce origin rules for browser-owned document frames.
    """
    encoded = url.toString(QUrl.FullyEncoded)
    if is_web_url(encoded):
        return True
    if url.scheme() == "about":
        return url.path() == "blank" or (not main_frame and url.path() == "srcdoc")
    if url.scheme() == "blob":
        return url.isValid()
    return not main_frame and url.scheme() == "data" and url.isValid()


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
        if supports_document_url(url, main_frame=is_main_frame):
            return True
        if is_main_frame:
            self.blocked_navigation.emit(url.scheme())
        return False

    def _certificate_error(self, error):
        error.rejectCertificate()
        self.blocked_navigation.emit("TLS")

    def _new_window(self, request):
        url = request.requestedUrl()
        if not url.isEmpty() and not supports_document_url(url):
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
        labels = {
            "MediaAudioCapture": ("마이크 사용", "Microphone"),
            "MediaVideoCapture": ("카메라 사용", "Camera"),
            "MediaAudioVideoCapture": ("카메라 및 마이크 사용", "Camera and microphone"),
            "DesktopVideoCapture": ("화면 공유", "Screen sharing"),
            "DesktopAudioVideoCapture": ("화면 및 오디오 공유", "Screen and audio sharing"),
            "MouseLock": ("마우스 포인터 잠금", "Pointer lock"),
            "Notifications": ("알림 표시", "Notifications"),
            "Geolocation": ("위치 정보", "Location"),
            "ClipboardReadWrite": ("클립보드 읽기 및 쓰기", "Read and write clipboard"),
            "LocalFontsAccess": ("설치된 글꼴 목록 확인", "Access installed fonts"),
        }
        if kind not in labels:
            permission.deny()
            return
        allowed = confirm(self.window, self.window.t("사이트 권한", "Site permission"),
                          f"{origin}\n\n{self.window.t(*labels[kind])}\n\n" + self.window.t(
                              "이 작업공간에서 허용할까요?", "Allow in this workspace?"))
        if permission.isValid():
            permission.grant() if allowed else permission.deny()


class BrowserView(QWebEngineView):
    def __init__(self, profile, window, parent=None):
        super().__init__(parent)
        self.setPage(BrowserPage(profile, window, self))

