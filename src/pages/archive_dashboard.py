"""
Primity Archive Dashboard - Native ArchiveBox Manager
=====================================================
Full-featured dashboard for managing archived pages directly within the browser.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QPushButton, QLabel, 
                             QLineEdit, QMessageBox, QScrollArea, QFrame, QSplitter)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QIcon
import datetime


class ArchiveDashboard(QWidget):
    """Native ArchiveBox dashboard integrated into Primity Browser."""
    
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.archiver = browser.archiver
        self.init_ui()
        self.load_data()

        # Auto-refresh timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_data)
        self.timer.start(10000)  # Refresh every 10 seconds

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ===== HEADER =====
        header = QHBoxLayout()
        
        title = QLabel("📦 Archive Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")
        header.addWidget(title)
        
        header.addStretch()
        
        # Stats
        self.stats_label = QLabel("Loading...")
        self.stats_label.setStyleSheet("font-size: 14px; color: #888;")
        header.addWidget(self.stats_label)
        
        layout.addLayout(header)
        
        # ===== TOOLBAR =====
        toolbar = QHBoxLayout()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search archives...")
        self.search_input.setMinimumWidth(300)
        self.search_input.returnPressed.connect(self.search_archives)
        toolbar.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search_archives)
        toolbar.addWidget(search_btn)
        
        toolbar.addStretch()
        
        # Refresh
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_data)
        toolbar.addWidget(refresh_btn)
        
        # Open Data folder
        data_dir_btn = QPushButton("📂 Open Storage")
        data_dir_btn.clicked.connect(self.open_storage_folder)
        toolbar.addWidget(data_dir_btn)
        
        layout.addLayout(toolbar)
        
        # ===== TABLE =====
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Title", "URL", "Status", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #333;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #444;
            }
        """)
        layout.addWidget(self.table)
        
        # ===== QUICK ACTIONS =====
        actions = QHBoxLayout()
        
        archive_current_btn = QPushButton("📸 Archive Current Page")
        archive_current_btn.setStyleSheet("padding: 12px 24px; font-size: 14px;")
        archive_current_btn.clicked.connect(self.archive_current_page)
        actions.addWidget(archive_current_btn)
        
        actions.addStretch()
        
        layout.addLayout(actions)

    def load_data(self):
        """Load snapshots from ArchiveBox SQLite database."""
        snapshots = self.archiver.get_snapshots(limit=100)
        total = self.archiver.get_snapshot_count()
        
        self.stats_label.setText(f"Total: {total} snapshots")
        
        self.table.setRowCount(0)
        
        for snap in snapshots:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            
            # ID (shortened)
            snap_id = str(snap.get('id', ''))[:8]
            self.table.setItem(row_idx, 0, QTableWidgetItem(snap_id))
            
            # Date
            added = snap.get('added', '')
            try:
                if added:
                    dt = datetime.datetime.fromisoformat(str(added).replace('Z', '+00:00'))
                    added_str = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    added_str = "-"
            except:
                added_str = str(added)[:16]
            self.table.setItem(row_idx, 1, QTableWidgetItem(added_str))
            
            # Title
            title = snap.get('title') or "No Title"
            self.table.setItem(row_idx, 2, QTableWidgetItem(title))
            
            # URL
            url = snap.get('url', '')
            url_item = QTableWidgetItem(url)
            url_item.setToolTip(url)
            self.table.setItem(row_idx, 3, url_item)
            
            # Status
            status = snap.get('status', 'unknown')
            status_item = QTableWidgetItem(status)
            if status == 'indexed':
                status_item.setForeground(Qt.green)
            elif status == 'pending':
                status_item.setForeground(Qt.yellow)
            else:
                status_item.setForeground(Qt.gray)
            self.table.setItem(row_idx, 4, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)
            actions_layout.setSpacing(4)
            
            # View button
            view_btn = QPushButton("👁️")
            view_btn.setToolTip("View Archive")
            view_btn.setFixedSize(32, 28)
            
            snap_id = snap.get('id')
            # Try to find the best file to open (Prioritize wget for script stability, then MHTML)
            local_path = self.archiver.get_snapshot_path(snap_id)
            import os
            
            # Wget usually gives the cleanest standard HTML
            wget_index = os.path.join(local_path, "wget", "index.html")
            mhtml_file = os.path.join(local_path, "output.mhtml")
            dom_file = os.path.join(local_path, "dom.html")
            
            if os.path.exists(wget_index):
                target_file_path = wget_index
            elif os.path.exists(mhtml_file):
                target_file_path = mhtml_file
            elif os.path.exists(dom_file):
                target_file_path = dom_file
            else:
                target_file_path = os.path.join(local_path, "index.html")
                
            local_url = QUrl.fromLocalFile(target_file_path).toString()
            view_btn.clicked.connect(lambda _, u=local_url: self.browser.open_url(u))
            actions_layout.addWidget(view_btn)
            
            # Open original
            orig_btn = QPushButton("🔗")
            orig_btn.setToolTip("Open Original URL")
            orig_btn.setFixedSize(32, 28)
            orig_btn.clicked.connect(lambda _, u=url: self.browser.open_url(u))
            actions_layout.addWidget(orig_btn)
            
            # Delete button
            del_btn = QPushButton("🗑️")
            del_btn.setToolTip("Delete Snapshot")
            del_btn.setFixedSize(32, 28)
            full_id = str(snap.get('id', ''))
            del_btn.clicked.connect(lambda _, s=full_id: self.delete_snapshot(s))
            actions_layout.addWidget(del_btn)
            
            self.table.setCellWidget(row_idx, 5, actions_widget)
        
        # Resize rows
        self.table.resizeRowsToContents()

    def search_archives(self):
        """Search snapshots by query."""
        query = self.search_input.text().strip()
        if not query:
            self.load_data()
            return
        
        snapshots = self.archiver.search_snapshots(query)
        
        self.table.setRowCount(0)
        self.stats_label.setText(f"Search results: {len(snapshots)}")
        
        for snap in snapshots:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(snap.get('id', ''))[:8]))
            
            added = snap.get('added', '')
            try:
                dt = datetime.datetime.fromisoformat(str(added).replace('Z', '+00:00'))
                added_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                added_str = str(added)[:16]
            self.table.setItem(row_idx, 1, QTableWidgetItem(added_str))
            self.table.setItem(row_idx, 2, QTableWidgetItem(snap.get('title') or "No Title"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(snap.get('url', '')))
            self.table.setItem(row_idx, 4, QTableWidgetItem(snap.get('status', '')))

    def delete_snapshot(self, snapshot_id):
        """Delete a snapshot after confirmation."""
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete snapshot {snapshot_id[:8]}...?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.archiver.delete_snapshot(snapshot_id)
            if success:
                self.browser.status.showMessage("Snapshot deleted", 2000)
                self.load_data()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete snapshot")

    def archive_current_page(self):
        """Archive the currently active page."""
        from PySide6.QtWebEngineWidgets import QWebEngineView
        
        current = self.browser.tabs.currentWidget()
        if isinstance(current, QWebEngineView):
            url = current.url().toString()
            self.archiver.start_recording(url)
            self.browser.status.showMessage(f"Archiving: {url}", 3000)
        else:
            QMessageBox.warning(self, "Error", "No web page is currently active")

    def open_storage_folder(self):
        """Open the data/archive folder in system file explorer."""
        import os
        import subprocess
        path = self.archiver.engine.archive_dir
        if os.path.exists(path):
            if os.name == 'nt': # Windows
                os.startfile(path)
            elif os.name == 'posix': # Linux/Mac
                subprocess.Popen(['xdg-open', str(path)])
