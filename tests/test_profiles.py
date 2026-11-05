"""실제 Qt 프로필 설정 검사. / Real Qt profile configuration tests."""

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
import pytest

from src.core.profiles import ProfileRegistry
from src.core.workspaces import WorkspaceStore


pytestmark = pytest.mark.gui


def test_profiles_are_named_persistent_and_disjoint(qapp, tmp_path):
    store = WorkspaceStore(tmp_path)
    a, b = store.create("A"), store.create("B")
    registry = ProfileRegistry(store)
    pa, pb = registry.get(a.id), registry.get(b.id)
    assert registry.get(a.id) is pa
    assert pa is not pb
    assert not pa.isOffTheRecord() and not pb.isOffTheRecord()
    assert pa.persistentStoragePath() != pb.persistentStoragePath()
    assert pa.cachePath() != pb.cachePath()
    assert pa.persistentStoragePath() == str(store.path(a.id, "qt"))
    assert pa.persistentCookiesPolicy() == QWebEngineProfile.AllowPersistentCookies
    assert pa.persistentPermissionsPolicy() == QWebEngineProfile.PersistentPermissionsPolicy.StoreInMemory
    registry.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_private_profiles_are_fresh_and_never_persist(qapp, tmp_path):
    registry = ProfileRegistry(WorkspaceStore(tmp_path))
    first, second = registry.private(), registry.private()
    assert first is not second
    assert first.isOffTheRecord() and second.isOffTheRecord()
    assert first.persistentCookiesPolicy() == QWebEngineProfile.NoPersistentCookies
    assert first.httpCacheType() == QWebEngineProfile.MemoryHttpCache
    registry.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_web_security_defaults_are_kept(qapp, tmp_path):
    store = WorkspaceStore(tmp_path)
    registry = ProfileRegistry(store)
    settings = registry.get(store.active_id).settings()
    for attribute in (QWebEngineSettings.AllowRunningInsecureContent,
                      QWebEngineSettings.LocalContentCanAccessFileUrls,
                      QWebEngineSettings.LocalContentCanAccessRemoteUrls,
                      QWebEngineSettings.JavascriptCanAccessClipboard):
        assert not settings.testAttribute(attribute)
    assert settings.testAttribute(QWebEngineSettings.JavascriptEnabled)
    registry.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)

