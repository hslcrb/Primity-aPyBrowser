import requests
import subprocess
import os
import time
from PySide6.QtCore import QObject, Signal, Slot, QThread

class ArchiveBoxWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, url, options=None):
        super().__init__()
        self.url = url
        self.options = options or {}

    def run(self):
        try:
            # Construct CLI command with options
            # docker exec [ENV_VARS] primity_archivebox archivebox add "URL" --depth=X
            
            base_cmd = ["docker", "exec"]
            
            # Apply Extractor options via Environment Variables
            # e.g. SAVE_WGET=False
            if self.options.get("extractors"):
                for ext, enabled in self.options["extractors"].items():
                    val = "True" if enabled else "False"
                    base_cmd.extend(["-e", f"SAVE_{ext.upper()}={val}"])

            base_cmd.extend(["primity_archivebox", "archivebox", "add", self.url])
            
            if self.options.get("depth"):
                base_cmd.append(f"--depth={self.options['depth']}")
                
            result = subprocess.run(base_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.finished.emit(True, "Snapshot Created Successfully")
            else:
                self.finished.emit(False, f"ArchiveBox Error: {result.stderr}")
                
        except Exception as e:
            self.finished.emit(False, str(e))

class ArchiveManager(QObject):
    """
    Real ArchiveBox Integration Manager.
    Controls the Docker container and triggers snapshots via CLI.
    """
    status_msg = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.check_docker_status()

    def check_docker_status(self):
        # Check if container is running
        try:
            res = subprocess.run(["docker", "ps", "-q", "-f", "name=primity_archivebox"], capture_output=True, text=True)
            if not res.stdout.strip():
                print("[ArchiveManager] Starting ArchiveBox Container...")
                subprocess.Popen(["docker-compose", "up", "-d"], cwd=os.getcwd())
        except Exception as e:
            print(f"[ArchiveManager] Docker Error: {e}")

    @Slot()
    def start_recording(self, url, title="", options=None):
        self.is_recording = True
        self.status_msg.emit(f"Archiving via ArchiveBox: {url}...")
        
        # Start Worker with options
        self.worker = ArchiveBoxWorker(url, options)
        self.worker.finished.connect(self.on_archive_finished)
        self.worker.start()

    @Slot()
    def stop_recording(self):
        # ArchiveBox 'add' is atomic, so 'stop' just means we are done waiting or cancelling (logic-wise).
        self.is_recording = False
        self.status_msg.emit("Archiving Request Sent")

    def on_archive_finished(self, success, msg):
        self.is_recording = False
        if success:
            self.status_msg.emit("✅ ArchiveBox: Snapshot Complete!")
        else:
            self.status_msg.emit(f"❌ ArchiveBox Failed: {msg}")

    def get_injection_script(self):
        # No longer needed for server-side archiving, but kept for interface compatibility
        return ""
