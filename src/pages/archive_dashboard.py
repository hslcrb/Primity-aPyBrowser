from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt, QTimer, QUrl, QDateTime
from PySide6.QtGui import QIcon
import sqlite3
import os
import datetime
import subprocess

class ArchiveDashboard(QWidget):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.db_path = os.path.join(os.getcwd(), 'data', 'index.sqlite3')
        self.init_ui()
        self.load_data()

        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data)
        self.timer.start(5000)  # Refresh every 5 seconds

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("ArchiveBox Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: var(--fg);")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_data)
        self.refresh_btn.setProperty("class", "SecondaryButton")
        header_layout.addWidget(self.refresh_btn)
        
        self.open_web_btn = QPushButton("Open Original Web UI")
        self.open_web_btn.clicked.connect(lambda: self.browser.open_url("http://127.0.0.1:8000"))
        self.open_web_btn.setProperty("class", "PrimaryButton")
        header_layout.addWidget(self.open_web_btn)
        
        layout.addLayout(header_layout)

        # Status Bar
        self.status_label = QLabel("Status: Connecting...")
        layout.addWidget(self.status_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Added", "Title", "URL", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: var(--bg);
                color: var(--fg);
                gridline-color: var(--border);
                border: 1px solid var(--border);
            }
            QHeaderView::section {
                background-color: var(--tab-bg);
                color: var(--fg);
                padding: 4px;
                border: 1px solid var(--border);
            }
        """)
        layout.addWidget(self.table)

    def load_data(self):
        if not os.path.exists(self.db_path):
            self.status_label.setText("Error: Database not found. Is ArchiveBox initialized?")
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Query recent snapshots
            cursor.execute("SELECT id, added, title, url, timestamp FROM core_snapshot ORDER BY added DESC LIMIT 50")
            rows = cursor.fetchall()
            
            self.table.setRowCount(0)
            
            for row in rows:
                snap_id, added, title, url, timestamp = row
                
                # Format time
                try:
                    dt = datetime.datetime.fromisoformat(added.replace('Z', '+00:00'))
                    added_str = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    added_str = str(added)

                row_idx = self.table.rowCount()
                self.table.insertRow(row_idx)
                
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(snap_id)[:8]))
                self.table.setItem(row_idx, 1, QTableWidgetItem(added_str))
                self.table.setItem(row_idx, 2, QTableWidgetItem(title or "No Title"))
                self.table.setItem(row_idx, 3, QTableWidgetItem(url))
                
                # Actions
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                view_btn = QPushButton("View")
                view_btn.setProperty("class", "SecondaryButton")
                # Construct local URL: http://127.0.0.1:8000/archive/<timestamp>/
                local_url = f"http://127.0.0.1:8000/archive/{timestamp}/"
                view_btn.clicked.connect(lambda _, u=local_url: self.browser.open_url(u))
                
                del_btn = QPushButton("Del")
                del_btn.setProperty("class", "DangerButton")
                del_btn.clicked.connect(lambda _, s=snap_id: self.delete_snapshot(s))
                
                btn_layout.addWidget(view_btn)
                btn_layout.addWidget(del_btn)
                
                self.table.setCellWidget(row_idx, 4, btn_widget)
                
            conn.close()
            
            # Get count
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM core_snapshot")
            count = cursor.fetchone()[0]
            conn.close()
            
            self.status_label.setText(f"Status: Connected (Total {count} Snaps)")
            
        except Exception as e:
            self.status_label.setText(f"Error: {e}")

    def delete_snapshot(self, snap_id):
        # We must use the CLI to delete properly as it handles files too, not just DB
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete snapshot {snap_id}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # docker exec primity_archivebox archivebox remove <id> --yes
            try:
                subprocess.run(["docker", "exec", "primity_archivebox", "archivebox", "remove", snap_id, "--yes"], check=True)
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
