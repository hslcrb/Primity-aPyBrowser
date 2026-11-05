"""외부 계정 없이 실제 Chromium으로 검사. / Real Chromium, synthetic local pages."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import time

from PySide6.QtCore import QCoreApplication, QEvent, QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
import pytest

from src.core.browser import BrowserController
from src.core.workspaces import WorkspaceStore

pytestmark = pytest.mark.gui


def wait_until(app, predicate, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        app.processEvents()
        if predicate():
            return
        time.sleep(0.01)
    raise AssertionError("Timed out waiting for a Chromium event")


def js(app, view, source):
    values = []
    view.page().runJavaScript(source, 0, values.append)
    wait_until(app, lambda: bool(values))
    return values[0]


def load(app, view, url):
    finished = []
    view.loadFinished.connect(finished.append)
    view.setUrl(QUrl(url))
    wait_until(app, lambda: bool(finished))
    view.loadFinished.disconnect(finished.append)
    assert finished[-1], url


@pytest.fixture(scope="module")
def site():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/sw.js"):
                body = b"self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',e=>e.waitUntil(clients.claim()));"
                content_type = "text/javascript"
            else:
                body = b"<!doctype html><title>Primity local fixture</title><h1>Local fixture</h1><a id='popup' target='_blank' href='/popup'>Popup</a><p>Find this text</p>"
                content_type = "text/html; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)


@pytest.fixture
def controller(qapp, tmp_path):
    app = BrowserController(WorkspaceStore(tmp_path))
    yield app
    app.shutdown()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)


def test_cookie_localstorage_indexeddb_and_service_workers_are_isolated(qapp, controller, site):
    first = controller.open_workspace(controller.store.active_id)
    second_id = controller.store.create("B").id
    second = controller.open_workspace(second_id)
    a, b = first.add_new_tab(site), second.add_new_tab(site)
    load(qapp, a, site + "/a")
    load(qapp, b, site + "/b")
    js(qapp, a, "document.cookie='account=A; path=/; max-age=3600'; localStorage.setItem('account','A'); sessionStorage.setItem('account','A'); 'done'")
    js(qapp, b, "document.cookie='account=B; path=/; max-age=3600'; localStorage.setItem('account','B'); 'done'")
    assert js(qapp, a, "document.cookie") == "account=A"
    assert js(qapp, b, "document.cookie") == "account=B"
    assert js(qapp, a, "localStorage.getItem('account')") == "A"
    assert js(qapp, b, "localStorage.getItem('account')") == "B"
    script = """window.dbDone=false;let r=indexedDB.open('primity-test',1);r.onupgradeneeded=()=>r.result.createObjectStore('kv');r.onsuccess=()=>{let db=r.result;let t=db.transaction('kv','readwrite');t.objectStore('kv').put('A','account');t.oncomplete=()=>{db.close();window.dbDone=true}};"""
    js(qapp, a, script)
    wait_until(qapp, lambda: js(qapp, a, "window.dbDone") is True)
    js(qapp, b, "window.databaseNames=null;indexedDB.databases().then(x=>window.databaseNames=x.map(d=>d.name).join(','));")
    wait_until(qapp, lambda: js(qapp, b, "window.databaseNames") is not None)
    assert "primity-test" not in js(qapp, b, "window.databaseNames")
    js(qapp, a, "window.swReady=false;navigator.serviceWorker.register('/sw.js').then(()=>navigator.serviceWorker.ready).then(()=>window.swReady=true);")
    wait_until(qapp, lambda: js(qapp, a, "window.swReady") is True)
    js(qapp, b, "window.swCount=-1;navigator.serviceWorker.getRegistrations().then(x=>window.swCount=x.length);")
    wait_until(qapp, lambda: js(qapp, b, "window.swCount") != -1)
    assert js(qapp, b, "window.swCount") == 0
    assert a.page().webChannel() is None
    assert b.page().webChannel() is None


def test_navigation_close_restore_and_workspace_badge(qapp, controller, site):
    window = controller.open_workspace(controller.store.active_id)
    view = window.add_new_tab(site)
    load(qapp, view, site + "/first")
    window.url_bar.setText(site + "/second")
    window.navigate_to_url()
    wait_until(qapp, lambda: view.url().path() == "/second" and view.history().canGoBack())
    assert window.back_action.isEnabled(), (view.url().toString(),
        [(item.url().toString()) for item in view.history().items()])
    window.back_action.trigger()
    wait_until(qapp, lambda: view.url().path() == "/first")
    assert window.workspace.name in window.windowTitle()
    index = window.tabs.indexOf(view)
    window.close_current_tab(index)
    restored = window.restore_closed_tab()
    assert isinstance(restored, QWebEngineView)
    assert restored.page().profile() is window.profile
    wait_until(qapp, lambda: restored.url().path() == "/first")


def test_private_windows_have_no_shared_account(qapp, controller, site):
    normal = controller.open_workspace(controller.store.active_id)
    private = controller.open_private(normal.workspace.id)
    a, b = normal.add_new_tab(site), private.add_new_tab(site)
    load(qapp, a, site)
    load(qapp, b, site)
    js(qapp, a, "document.cookie='account=A; path=/'; localStorage.setItem('account','A')")
    assert js(qapp, b, "document.cookie") == ""
    assert js(qapp, b, "JSON.stringify(localStorage.getItem('account'))") == "null"
    assert private.profile.isOffTheRecord()
    assert not private.bookmark_action.isEnabled()


def test_popup_page_stays_in_its_workspace(qapp, controller, site):
    window = controller.open_workspace(controller.store.active_id)
    view = window.add_new_tab(site)
    load(qapp, view, site)
    js(qapp, view, "document.cookie='account=A; path=/';")
    # Same production factory used by newWindowRequested.openIn().
    popup = window.new_popup_page()
    assert popup.profile() is view.page().profile()
    assert popup.webChannel() is None
    assert popup is not view.page()

