"""
Primity Native Archive Manager
==============================
Manages web archiving using the embedded Python engine (No Docker).
High-fidelity capture using Qt WebEngine native capabilities.
"""

import os
import json
from PySide6.QtCore import QObject, Signal, Slot, QThread, QTimer, QByteArray
from PySide6.QtWebEngineCore import QWebEngineDownloadRequest, QWebEngineUrlRequestInterceptor
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from src.core.archivebox_core.engine import ArchiveEngine
from pathlib import Path

class PrimityRecorder(QObject):
    """Bridge for vacuuming real response data from JS to Python."""
    data_received = Signal(str, str, str) # snapshot_id, url, payload_b64

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    @Slot(str, str)
    def record(self, url, payload_b64):
        if self.manager.is_recording and self.manager.current_snapshot_id:
            self.data_received.emit(self.manager.current_snapshot_id, url, payload_b64)

class ArchiveInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts and logs network requests for perfect archiving."""
    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def interceptRequest(self, info):
        if self.manager.is_recording and self.manager.current_snapshot_id:
            url = info.requestUrl().toString()
            method = info.requestMethod().data().decode()
            resource_type = info.resourceType()
            try:
                self.manager.engine.log_network_request(
                    self.manager.current_snapshot_id, url, method, resource_type
                )
            except:
                pass

class ArchiveWorker(QThread):
    finished = Signal(bool, str)
    progress = Signal(str)

    def __init__(self, manager, url, title, options, snapshot_id, snap_path):
        super().__init__()
        self.manager = manager
        self.engine = manager.engine
        self.url = url
        self.title = title
        self.options = options or {}
        self.snapshot_id = snapshot_id
        self.snap_path = snap_path

    def run(self):
        try:
            self.progress.emit(f"Background capture starting: {self.url}")
            
            # 1. Run Wget (Slow)
            if self.options.get('extractors', {}).get('wget', True):
                self.progress.emit("Running Wget...")
                self.engine._run_wget(self.url, self.snap_path, depth=self.options.get('depth', 0))
                
            # 2. Build WARC & Export Logs (Medium)
            self.progress.emit("Building WARC & Network Logs...")
            self.engine.build_warc(self.snapshot_id, self.url)
            self.engine.export_network_logs(self.snapshot_id, self.snap_path / "network_logs.json")
            self.engine.build_wacz(self.snapshot_id)
            
            # 3. Media Extraction (Slow)
            if self.options.get('extractors', {}).get('media'):
                self.progress.emit("Extracting Media...")
                self.manager._run_ytdlp(self.url, self.snap_path, self.snapshot_id)
                
            self.finished.emit(True, f"Archive Complete [ID: {self.snapshot_id[:8]}]")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.finished.emit(False, str(e))

class ArchiveManager(QObject):
    status_msg = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.current_snapshot_id = None
        
        # Default data path: projects/Primity/data
        primary_data = Path(os.getcwd()) / 'data'
        try:
            if not primary_data.exists():
                primary_data.mkdir(parents=True, exist_ok=True)
            # Test writability
            test_file = primary_data / '.write_test'
            test_file.touch()
            test_file.unlink()
            self.data_dir = primary_data
        except:
            self.data_dir = Path(os.getcwd()) / 'data_native'
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
        self.engine = ArchiveEngine(self.data_dir)
        
        # Setup Interceptor & Recorder (The Vacuum)
        self.interceptor = ArchiveInterceptor(self)
        self.recorder = PrimityRecorder(self)
        self.recorder.data_received.connect(self.engine.log_payload)

    def _on_finished(self, success, msg):
        """Handle background worker completion."""
        self.is_recording = False
        if success:
            self.status_msg.emit(f"✅ {msg}")
        else:
            self.status_msg.emit(f"❌ Error: {msg}")

    def update_storage_path(self, new_path):
        """Update storage path dynamically."""
        self.data_dir = Path(new_path)
        self.engine = ArchiveEngine(self.data_dir)
        self.status_msg.emit(f"Storage path updated: {new_path}")

    @Slot()
    def start_recording(self, url, title="", options=None, browser_view=None):
        """High-level entry point for archiving. (Async)"""
        self.is_recording = True
        
        # Set default options if none provided
        if not options:
            options = {
                "depth": 0,
                "extractors": {
                    "wget": True, 
                    "singlefile": True, 
                    "screenshot": True, 
                    "dom": True,
                    "media": True,
                    "pdf": True
                }
            }
            
        self.status_msg.emit(f"Initializing Archive: {url}...")
        
        # 1. Create entry in DB and dir
        self.current_snapshot_id = self.engine.add(
            url, title, 
            depth=options.get("depth", 0),
            extractors=options.get('extractors')
        )
        snapshot_id = self.current_snapshot_id
        snap_path = Path(self.engine.get_snapshot_path(snapshot_id))
        
        # 2. Native High-Fidelity Capture (Instant parts on UI Thread)
        if browser_view:
            try:
                self._do_native_capture(snapshot_id, snap_path, browser_view, options)
            except Exception as e:
                print(f"Native Capture Error: {e}")
            
        # 3. Heavy Background Extraction (ASYNC THREAD)
        self.worker = ArchiveWorker(self, url, title, options, snapshot_id, snap_path)
        self.worker.progress.connect(lambda msg: self.status_msg.emit(msg))
        self.worker.finished.connect(self._on_finished)
        self.worker.start()
        
        self.status_msg.emit(f"✅ Archive Started [ID: {snapshot_id[:8]}]")
        return snapshot_id

    def _run_ytdlp(self, url, snap_path, snapshot_id):
        """Run yt-dlp only for recognized video platforms."""
        import subprocess
        video_platforms = ["youtube.com", "youtu.be", "vimeo.com", "dailymotion.com", "twitch.tv", "tiktok.com"]
        if not any(p in url.lower() for p in video_platforms):
            return # Skip non-video sites
            
        try:
            media_path = snap_path / "media"
            media_path.mkdir(exist_ok=True)
            cmd = [
                "yt-dlp", "--no-playlist", "--quiet", "--max-filesize", "100M",
                "-o", f"{media_path}/%(title)s.%(ext)s",
                url
            ]
            # Run in background to not block
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.engine._log_result(snapshot_id, "media", "success", "media/")
        except Exception as e:
            self.engine._log_result(snapshot_id, "media", "failed", str(e))

    def _do_native_capture(self, snapshot_id, snap_path, view, options):
        """Perform screenshot and MHTML capture using Qt WebEngine."""
        extractors = options.get('extractors', {}) if options else {"screenshot": True, "singlefile": True}
        
        # A. Screenshot
        if extractors.get('screenshot'):
            try:
                img_path = snap_path / "screenshot.png"
                view.grab().save(str(img_path))
                self.engine._log_result(snapshot_id, "screenshot", "success", "screenshot.png")
            except Exception as e:
                self.engine._log_result(snapshot_id, "screenshot", "failed", str(e))

        # B. MHTML
        if extractors.get('singlefile'):
            try:
                mhtml_path = snap_path / "output.mhtml"
                view.page().save(str(mhtml_path), QWebEngineDownloadRequest.MimeHtmlSaveFormat)
                self.engine._log_result(snapshot_id, "singlefile", "success", "output.mhtml")
            except Exception as e:
                self.engine._log_result(snapshot_id, "singlefile", "failed", str(e))
                
        # C. DOM Dump
        if extractors.get('dom'):
            view.page().toHtml(lambda html, sid=snapshot_id, sp=snap_path: self._save_dom(sid, sp, html))
            
        # D. PDF
        if extractors.get('pdf', True):
            pdf_path = snap_path / "output.pdf"
            view.page().printToPdf(str(pdf_path))
            self.engine._log_result(snapshot_id, "pdf", "success", "output.pdf")

    def _save_dom(self, sid, snap_path, html):
        try:
            with open(snap_path / "dom.html", "w", encoding='utf-8') as f:
                f.write(html)
            self.engine._log_result(sid, "dom", "success", "dom.html")
        except:
            pass

    @Slot()
    def stop_recording(self):
        self.is_recording = False
        self.current_snapshot_id = None
        self.status_msg.emit("Archiving Mode Disabled")

    # ========== Data Access Proxy ==========
    
    def get_snapshots(self, limit=50):
        return self.engine.list_snapshots(limit)

    def delete_snapshot(self, snap_id):
        return self.engine.delete(snap_id)

    def search_snapshots(self, query, limit=50):
        snaps = self.engine.list_snapshots(1000)
        return [s for s in snaps if query.lower() in (s['url'] + (s.get('title') or "")).lower()][:limit]

    def get_snapshot_count(self):
        return len(self.engine.list_snapshots(10000))

    def get_snapshot_path(self, snapshot_id):
        return self.engine.get_snapshot_path(snapshot_id)

    def get_snapshot_url(self, snapshot_id):
        return self.engine.get_snapshot_url(snapshot_id)

    def get_injection_script(self):
        return ""
