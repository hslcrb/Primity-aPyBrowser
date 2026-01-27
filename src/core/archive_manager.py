import sqlite3
import json
import base64
import os
import time
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QUrl

class ArchiveManager(QObject):
    """
    Core engine for 'Web Time Machine'.
    Handles SQLite storage of network resources and DOM snapshots.
    """
    status_msg = Signal(str)

    def __init__(self, db_path="primity_archive.db"):
        super().__init__()
        self.db_path = db_path
        self.init_db()
        self.is_recording = False
        self.current_session_id = None

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # 1. Archives (Sessions)
        c.execute('''CREATE TABLE IF NOT EXISTS archives (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT,
                        title TEXT,
                        timestamp TEXT,
                        user_note TEXT
                    )''')
        
        # 2. Resources (The 'Grid')
        # We store URL as unique key per archive to handle versioning if needed, 
        # or global deduplication. For 'Time Machine', we need versioning.
        # So (archive_id, url) should be unique-ish.
        c.execute('''CREATE TABLE IF NOT EXISTS resources (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        archive_id INTEGER,
                        url TEXT,
                        method TEXT,
                        mime_type TEXT,
                        data BLOB,
                        timestamp TEXT,
                        FOREIGN KEY(archive_id) REFERENCES archives(id)
                    )''')
        
        conn.commit()
        conn.close()

    @Slot()
    def start_recording(self, url, title="Untitled"):
        self.is_recording = True
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        ts = datetime.now().isoformat()
        c.execute("INSERT INTO archives (url, title, timestamp) VALUES (?, ?, ?)", (url, title, ts))
        self.current_session_id = c.lastrowid
        conn.commit()
        conn.close()
        self.status_msg.emit(f"REC Started: Session #{self.current_session_id}")

    @Slot()
    def stop_recording(self):
        self.is_recording = False
        self.current_session_id = None
        self.status_msg.emit("REC Stopped")

    def save_resource(self, url, method, mime, data_b64):
        """
        Saves a network resource.
        data_b64: Base64 encoded string of the response body.
        """
        if not self.is_recording or not self.current_session_id:
            return

        try:
            # Decode base64 to blob
            if ',' in data_b64:
                header, encoded = data_b64.split(',', 1)
                data = base64.b64decode(encoded)
            else:
                data = base64.b64decode(data_b64)
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            ts = datetime.now().isoformat()
            
            # Check duplicates in this session
            c.execute("SELECT id FROM resources WHERE archive_id=? AND url=?", (self.current_session_id, url))
            if c.fetchone():
                # Update existing (latest wins)
                c.execute("UPDATE resources SET data=?, timestamp=?, mime_type=? WHERE archive_id=? AND url=?", 
                          (data, ts, mime, self.current_session_id, url))
            else:
                c.execute("INSERT INTO resources (archive_id, url, method, mime_type, data, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                          (self.current_session_id, url, method, mime, data, ts))
            
            conn.commit()
            conn.close()
            # self.status_msg.emit(f"Captured: {url[:30]}...") # Too verbose
        except Exception as e:
            print(f"[Archiver Error] Failed to save {url}: {e}")

    def get_injection_script(self):
        """
        Returns the JS code to inject into pages to capture Fetch/XHR/Resources.
        """
        return """
        (function() {
            if (window._primity_archiver_active) return;
            window._primity_archiver_active = true;
            console.log("[Primity Archiver] Injection Active");

            // Helper to send data to Python
            function sendToPython(url, method, mime, blob) {
                var reader = new FileReader();
                reader.onload = function() {
                    // Send via WebChannel or Console fallback
                    // For now, let's use console log with a prefix if WebChannel isn't ready
                    // Ideally, we'd use a QWebChannel. For simplicity in this step:
                    // We will assume a 'primityBackend' object is exposed or we use a special console key.
                    // Let's use a specific JSON structure in console.log that Python intercepts.
                    var payload = JSON.stringify({
                        type: 'PRIMITY_ARCHIVE_DATA',
                        url: url,
                        method: method,
                        mime: mime || 'application/octet-stream',
                        data: reader.result // Data URL
                    });
                    console.log(payload); 
                };
                reader.readAsDataURL(blob);
            }

            // 1. Intercept Fetch
            const originalFetch = window.fetch;
            window.fetch = async function(...args) {
                const response = await originalFetch(...args);
                const clone = response.clone();
                const url = (args[0] instanceof Request) ? args[0].url : args[0];
                const method = (args[0] instanceof Request) ? args[0].method : (args[1]?.method || 'GET');
                
                clone.blob().then(blob => {
                    sendToPython(url, method, clone.headers.get('content-type'), blob);
                }).catch(e => console.error("Fetch capture failed", e));
                
                return response;
            };

            // 2. Intercept XHR
            const originalXHR = window.XMLHttpRequest;
            window.XMLHttpRequest = function() {
                const xhr = new originalXHR();
                const originalOpen = xhr.open;
                
                let requestUrl;
                let requestMethod;

                xhr.open = function(method, url) {
                    requestUrl = url;
                    requestMethod = method;
                    originalOpen.apply(xhr, arguments);
                };

                xhr.addEventListener('load', function() {
                    if (xhr.responseType === '' || xhr.responseType === 'text') {
                        const blob = new Blob([xhr.responseText], {type: xhr.getResponseHeader('Content-Type')});
                        sendToPython(requestUrl, requestMethod, xhr.getResponseHeader('Content-Type'), blob);
                    } else if (xhr.responseType === 'blob') {
                        sendToPython(requestUrl, requestMethod, xhr.getResponseHeader('Content-Type'), xhr.response);
                    }
                    // buffer/json types can also be handled
                });
                return xhr;
            };
            
            // 3. Capture Static Resources (Images/CSS loaded via HTML tags)
            // Use Performance Observer
            new PerformanceObserver((entryList) => {
                for (const entry of entryList.getEntries()) {
                    if (entry.initiatorType === 'img' || entry.initiatorType === 'css' || entry.initiatorType === 'script') {
                        // Re-fetch to get content blob (Browser cache should make this cheap)
                        originalFetch(entry.name).then(r => r.blob()).then(blob => {
                            sendToPython(entry.name, 'GET', blob.type, blob);
                        }).catch(e => {}); // Ignore failures
                    }
                }
            }).observe({type: 'resource', buffered: true});

        })();
        """
