"""
Primity Native Archive Engine
=============================
A lightweight, Django-free implementation of ArchiveBox core features.
Optimized for embedding within Primity Browser.
"""

import os
import sqlite3
import subprocess
import json
import time
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

class ArchiveEngine:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.archive_dir = self.data_dir / "archive"
        self.db_path = self.data_dir / "index.sqlite3"
        self.warc_dir = self.data_dir / "warcs"
        
        # Ensure directories exist
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            self.warc_dir.mkdir(parents=True, exist_ok=True)
            self._init_db()
        except Exception as e:
            print(f"[ArchiveEngine] Critical Init Error: {e}")

    def _init_db(self):
        """Initialize SQLite database with a compatible schema."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Core Snapshot Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS core_snapshot (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                title TEXT,
                tags TEXT,
                status TEXT,
                added TEXT
            )
        """)
        
        # Archive Result Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS core_archiveresult (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT,
                extractor TEXT,
                status TEXT,
                output TEXT,
                start_ts TEXT,
                end_ts TEXT,
                FOREIGN KEY(snapshot_id) REFERENCES core_snapshot(id)
            )
        """)

        # Network Log Table (For Replay/Mocking)
        c.execute("""
            CREATE TABLE IF NOT EXISTS core_networklog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT,
                url TEXT,
                method TEXT,
                resource_type INTEGER,
                payload BLOB,
                timestamp TEXT,
                FOREIGN KEY(snapshot_id) REFERENCES core_snapshot(id)
            )
        """)
        
        conn.commit()
        conn.close()

    def add(self, url, title=None, depth=0, extractors=None):
        """Add a new URL to the archive index."""
        timestamp = str(int(time.time()))
        snapshot_id = timestamp 
        
        # Create snapshot directory: data/archive/<timestamp>/
        snap_dir = self.archive_dir / timestamp
        snap_dir.mkdir(parents=True, exist_ok=True)
        
        # Save placeholder index.html
        with open(snap_dir / "index.html", "w", encoding='utf-8') as f:
            f.write(f'<html><head><title>{title or url}</title><meta http-equiv="refresh" content="3;url={url}"></head>'
                    f'<body><h1>Archiving in progress...</h1><p>URL: {url}</p></body></html>')
            
        # Save to DB
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO core_snapshot (id, url, timestamp, title, status, added) VALUES (?, ?, ?, ?, ?, ?)",
                  (snapshot_id, url, timestamp, title or url, "pending", datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        # Run standard CLI extractors (wget)
        if extractors and extractors.get('wget'):
            self._run_wget(url, snap_dir, depth=depth)
            
        return snapshot_id

    def update_snapshot_info(self, snapshot_id, title=None, status=None):
        """Update snapshot metadata."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if title and status:
            c.execute("UPDATE core_snapshot SET title = ?, status = ? WHERE id = ?", (title, status, snapshot_id))
        elif title:
            c.execute("UPDATE core_snapshot SET title = ? WHERE id = ?", (title, snapshot_id))
        elif status:
            c.execute("UPDATE core_snapshot SET status = ? WHERE id = ?", (status, snapshot_id))
        conn.commit()
        conn.close()

    def _run_wget(self, url, output_dir, depth=0):
        """Native Wget extraction."""
        try:
            # We save into a 'wget' subfolder
            wget_dir = output_dir / "wget"
            wget_dir.mkdir(exist_ok=True)
            
            cmd = [
                "wget", "--no-clobber", "--page-requisites", "--html-extension",
                "--convert-links", "--restrict-file-names=windows",
                "--directory-prefix", str(wget_dir)
            ]
            
            # Add recursion if depth > 0
            if depth > 0:
                cmd.extend(["--recursive", f"--level={depth}", "--no-parent"])
                
            cmd.append(url)
            
            subprocess.run(cmd, capture_output=True, timeout=300) # Increased timeout for recursion
            
            self._log_result(output_dir.name, "wget", "success", "wget/index.html")
        except Exception as e:
            self._log_result(output_dir.name, "wget", "failed", str(e))

    def _log_result(self, snapshot_id, extractor, status, output):
        """Log extractor result to DB."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO core_archiveresult (snapshot_id, extractor, status, output, start_ts) 
            VALUES (?, ?, ?, ?, ?)
        """, (snapshot_id, extractor, status, output, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def log_network_request(self, snapshot_id, url, method, resource_type):
        """Log individual network requests."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO core_networklog (snapshot_id, url, method, resource_type, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (snapshot_id, url, method, int(resource_type), datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def log_payload(self, snapshot_id, url, payload_b64):
        """Save actual response body to DB for perfect replay."""
        import base64
        try:
            payload_bytes = base64.b64decode(payload_b64)
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                UPDATE core_networklog SET payload = ? 
                WHERE snapshot_id = ? AND url = ?
            """, (payload_bytes, snapshot_id, url))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Log Payload Error: {e}")

    def build_warc(self, snapshot_id, url):
        """Build a WARC file from captured data for this snapshot."""
        warc_path = self.warc_dir / f"{snapshot_id}.warc.gz"
        try:
            from warcio.warcwriter import WARCWriter
            from warcio.statusandheaders import StatusAndHeaders
            import io
            import requests

            with open(warc_path, 'wb') as output:
                writer = WARCWriter(output, gzip=True)
                
                # Add metadata record
                data = {"url": url, "snapshot_id": snapshot_id, "app": "Primity Browser"}
                record = writer.create_warc_record(url, 'metadata', 
                                                payload=io.BytesIO(json.dumps(data).encode('utf-8')),
                                                warc_headers_dict={'Content-Type': 'application/json'})
                writer.write_record(record)
                
                # Fetch essential resources if not already local (Basic Implementation)
                # In full 'Web Time Machine', we'd use the intercepted byte-stream.
                # For now, we fetch current state for WARC packaging.
                try:
                    resp = requests.get(url, timeout=10, headers={'User-Agent': 'PrimityArchiver/1.0'})
                    http_headers = StatusAndHeaders('200 OK', resp.headers.items(), protocol='HTTP/1.1')
                    record = writer.create_warc_record(url, 'response',
                                                    payload=io.BytesIO(resp.content),
                                                    http_headers=http_headers)
                    writer.write_record(record)
                except:
                    pass

            self._log_result(snapshot_id, "warc", "success", f"warcs/{snapshot_id}.warc.gz")
            return True
        except Exception as e:
            self._log_result(snapshot_id, "warc", "failed", str(e))
            return False

    def export_network_logs(self, snapshot_id, output_path):
        """Export all network logs for this snapshot to a JSON file."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM core_networklog WHERE snapshot_id = ?", (snapshot_id,))
            rows = c.fetchall()
            logs = [dict(r) for r in rows]
            conn.close()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
            return True
        except:
            return False

    def build_wacz(self, snapshot_id):
        """Create a WACZ compatible zip file containing WARC and metadata."""
        import zipfile
        wacz_path = self.data_dir / "archives" / f"{snapshot_id}.wacz"
        wacz_path.parent.mkdir(exist_ok=True)
        
        warc_file = self.warc_dir / f"{snapshot_id}.warc.gz"
        
        try:
            with zipfile.ZipFile(wacz_path, 'w') as z:
                # 1. Add WARC
                if warc_file.exists():
                    z.write(warc_file, "archive/data.warc.gz")
                
                # 2. Add Network Logs (Metadata)
                log_temp = self.data_dir / f"tmp_{snapshot_id}.json"
                if self.export_network_logs(snapshot_id, log_temp):
                    z.write(log_temp, "metadata/network_logs.json")
                    log_temp.unlink()
            
            self._log_result(snapshot_id, "wacz", "success", f"archives/{snapshot_id}.wacz")
            return True
        except Exception as e:
            self._log_result(snapshot_id, "wacz", "failed", str(e))
            return False

    def delete(self, snapshot_id):
        """Delete snapshot files and DB entries."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM core_snapshot WHERE id = ?", (snapshot_id,))
            c.execute("DELETE FROM core_archiveresult WHERE snapshot_id = ?", (snapshot_id,))
            conn.commit()
            conn.close()
            
            snap_dir = self.archive_dir / snapshot_id
            if snap_dir.exists():
                shutil.rmtree(snap_dir)
            return True
        except Exception as e:
            print(f"Delete Error: {e}")
            return False

    def list_snapshots(self, limit=50):
        if not self.db_path.exists():
            return []
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM core_snapshot ORDER BY added DESC LIMIT ?", (limit,))
            rows = c.fetchall()
            conn.close()
            return [dict(r) for r in rows]
        except:
            return []

    def get_snapshot_path(self, snapshot_id):
        """Get the absolute path to a snapshot directory."""
        return str((self.archive_dir / snapshot_id).absolute())
