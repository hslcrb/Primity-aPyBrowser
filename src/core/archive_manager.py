"""
Primity ArchiveBox Hybrid Integration Module
=============================================
Since ArchiveBox 0.9.3+ requires Python 3.13+, we use a hybrid approach:
- Docker CLI for archiving operations (add, remove)
- Direct SQLite access for data reading (snapshots, stats)

This provides "real integration" while remaining compatible with Python 3.12.
"""

import subprocess
import sqlite3
import os
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QThread


class ArchiveBoxWorker(QThread):
    """Worker thread for archiving URLs without blocking the UI."""
    finished = Signal(bool, str)
    progress = Signal(str)

    def __init__(self, url, options=None):
        super().__init__()
        self.url = url
        self.options = options or {}

    def run(self):
        """Execute archiving via Docker CLI."""
        try:
            self.progress.emit("Starting ArchiveBox Capture...")
            
            base_cmd = ["docker", "exec"]
            
            # Apply Extractor options via Environment Variables
            if self.options.get("extractors"):
                for ext, enabled in self.options["extractors"].items():
                    val = "True" if enabled else "False"
                    base_cmd.extend(["-e", f"SAVE_{ext.upper()}={val}"])

            base_cmd.extend(["primity_archivebox", "archivebox", "add", self.url])
            
            if self.options.get("depth"):
                base_cmd.append(f"--depth={self.options['depth']}")
                
            result = subprocess.run(base_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.finished.emit(True, "Snapshot Created Successfully")
            else:
                self.finished.emit(False, f"ArchiveBox Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.finished.emit(False, "Archiving timed out (5 min)")
        except Exception as e:
            self.finished.emit(False, str(e))


class ArchiveManager(QObject):
    """
    Primity ArchiveBox Hybrid Integration Manager.
    
    Features:
    - Docker CLI for archiving (add/remove)
    - Direct SQLite database access for data queries
    - Real-time status signals for UI updates
    """
    status_msg = Signal(str)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.worker = None
        self.worker = None
        
        # Load custom path from .env or settings (managed via .env for docker)
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self._load_data_dir()
        self.db_path = self.data_dir / 'index.sqlite3'
        
        self._ensure_docker_container()

    def _load_data_dir(self):
        """Load data directory from .env or default."""
        env_path = self.project_root / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('ARCHIVE_DATA_DIR='):
                        path_str = line.split('=', 1)[1].strip()
                        return Path(path_str)
        return self.project_root / 'data'

    def update_storage_path(self, new_path):
        """Update storage path and restart container."""
        new_dir = Path(new_path)
        if not new_dir.exists():
            return
            
        # Write to .env
        env_path = self.project_root / '.env'
        with open(env_path, 'w') as f:
            f.write(f"ARCHIVE_DATA_DIR={new_dir.absolute()}\n")
            
        self.data_dir = new_dir
        self.db_path = self.data_dir / 'index.sqlite3'
        
        self.status_msg.emit("Restarting ArchiveBox with new storage...")
        
        # Restart Docker
        try:
            subprocess.run(["docker-compose", "down"], cwd=str(self.project_root), check=True)
            subprocess.Popen(["docker-compose", "up", "-d"], cwd=str(self.project_root))
        except Exception as e:
            print(f"[ArchiveManager] Restart Error: {e}")

    def _ensure_docker_container(self):
        """Ensure Docker container is running."""
        try:
            res = subprocess.run(
                ["docker", "ps", "-q", "-f", "name=primity_archivebox"],
                capture_output=True, text=True
            )
            if not res.stdout.strip():
                print("[ArchiveManager] Starting ArchiveBox Container...")
                subprocess.Popen(["docker-compose", "up", "-d"], cwd=str(Path(__file__).parent.parent.parent))
        except Exception as e:
            print(f"[ArchiveManager] Docker Error: {e}")

    # ========== ARCHIVING OPERATIONS (Docker CLI) ==========

    @Slot()
    def start_recording(self, url, title="", options=None):
        """Start archiving a URL."""
        self.is_recording = True
        self.status_msg.emit(f"Archiving: {url}...")
        
        self.worker = ArchiveBoxWorker(url, options)
        self.worker.progress.connect(lambda msg: self.status_msg.emit(msg))
        self.worker.finished.connect(self._on_archive_finished)
        self.worker.start()

    @Slot()
    def stop_recording(self):
        """Stop/cancel archiving."""
        self.is_recording = False
        self.status_msg.emit("Archiving Stopped")

    def _on_archive_finished(self, success, msg):
        """Handle archive completion."""
        self.is_recording = False
        if success:
            self.status_msg.emit(f"✅ {msg}")
        else:
            self.status_msg.emit(f"❌ {msg}")

    def delete_snapshot(self, snapshot_id):
        """Delete a snapshot via Docker CLI."""
        try:
            result = subprocess.run(
                ["docker", "exec", "primity_archivebox", "archivebox", "remove", snapshot_id, "--yes"],
                capture_output=True, text=True, timeout=60
            )
            return result.returncode == 0
        except Exception as e:
            print(f"[ArchiveManager] Delete Error: {e}")
            return False

    # ========== DATA ACCESS (Direct SQLite) ==========

    def get_snapshots(self, limit=50):
        """Get recent snapshots directly from SQLite database."""
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, added, title, url, timestamp, status 
                FROM core_snapshot 
                ORDER BY added DESC 
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ArchiveManager] SQLite Error: {e}")
            return []

    def get_snapshot_count(self):
        """Get total number of snapshots."""
        if not self.db_path.exists():
            return 0
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM core_snapshot")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception:
            return 0

    def get_tags(self):
        """Get all tags from the database."""
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT name FROM taggit_tag")
            tags = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tags
        except Exception:
            return []

    def search_snapshots(self, query, limit=50):
        """Search snapshots by title or URL."""
        if not self.db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, added, title, url, timestamp, status 
                FROM core_snapshot 
                WHERE title LIKE ? OR url LIKE ?
                ORDER BY added DESC 
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ArchiveManager] Search Error: {e}")
            return []

    def get_snapshot_detail(self, snapshot_id):
        """Get detailed info for a single snapshot including archive results."""
        if not self.db_path.exists():
            return None
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get snapshot
            cursor.execute("SELECT * FROM core_snapshot WHERE id = ?", (snapshot_id,))
            snapshot = cursor.fetchone()
            
            if not snapshot:
                return None
            
            result = dict(snapshot)
            
            # Get archive results
            cursor.execute("""
                SELECT extractor, status, start_ts, output 
                FROM core_archiveresult 
                WHERE snapshot_id = ?
            """, (snapshot_id,))
            results = cursor.fetchall()
            result['archive_results'] = [dict(r) for r in results]
            
            conn.close()
            return result
        except Exception as e:
            print(f"[ArchiveManager] Detail Error: {e}")
            return None

    def get_injection_script(self):
        """No JS injection needed for Docker-based archiving."""
        return ""
