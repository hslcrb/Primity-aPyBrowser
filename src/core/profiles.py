"""계정 데이터의 Chromium 경계. / Chromium boundaries for account data."""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings


class ProfileRegistry(QObject):
    download_requested = Signal(object)

    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self._profiles = {}
        self._private = []

    def _configure(self, profile):
        settings = profile.settings()
        for attribute in (QWebEngineSettings.AllowRunningInsecureContent,
                          QWebEngineSettings.LocalContentCanAccessFileUrls,
                          QWebEngineSettings.LocalContentCanAccessRemoteUrls,
                          QWebEngineSettings.JavascriptCanAccessClipboard):
            settings.setAttribute(attribute, False)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.FocusOnNavigationEnabled, True)
        profile.setPersistentPermissionsPolicy(QWebEngineProfile.PersistentPermissionsPolicy.StoreInMemory)
        profile.downloadRequested.connect(self.download_requested.emit)
        return profile

    def get(self, workspace_id):
        if workspace_id not in self._profiles:
            # 페이지 생성 전에 모든 경로를 확정한다. / Set paths before creating pages.
            storage = self.store.path(workspace_id, "qt")
            cache = self.store.path(workspace_id, "cache")
            profile = QWebEngineProfile("primity-" + workspace_id, self)
            profile.setPersistentStoragePath(str(storage))
            profile.setCachePath(str(cache))
            profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
            profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
            self._profiles[workspace_id] = self._configure(profile)
        return self._profiles[workspace_id]

    def private(self):
        # 저장 이름 없는 프로필은 디스크를 사용하지 않는다. / Off-the-record profile.
        profile = QWebEngineProfile(self)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self._private.append(self._configure(profile))
        return profile

    def release_private(self, profile):
        if profile in self._private:
            self._private.remove(profile)
            profile.deleteLater()

