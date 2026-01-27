import json
import os
from PySide6.QtWidgets import (QMainWindow, QToolBar, QLineEdit, QTabWidget, 
                             QStatusBar, QPushButton, QMenu, QMessageBox, QVBoxLayout, 
                             QWidget, QHBoxLayout, QLabel, QFileDialog, QInputDialog, QDialog,
                             QToolButton)
from PySide6.QtCore import QUrl, QSettings, Qt, Signal, QObject, Slot, QPoint, QPropertyAnimation, QVariantAnimation
from PySide6.QtGui import QAction, QIcon, QPixmap, QMouseEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings

from src.config.constants import TRANSLATIONS, DEFAULT_SETTINGS
from src.ui.styles import get_stylesheet
from src.ui.components import MinimalCard, BookmarkDialog
from src.pages.passwords import PasswordPage
from src.pages.settings import SettingsPage
from src.pages.archive_dashboard import ArchiveDashboard
from src.ui.archive_config import ArchiveConfigDialog
from src.ui.hangul_lineedit import HangulLineEdit
from src.utils.helpers import generate_strong_password
from src.core.ime_manager import IMEManager
from src.core.archive_manager import ArchiveManager


class PrimityBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WA_InputMethodEnabled, True)

        self.settings = QSettings("Primity", "Browser")
        self.current_lang = self.settings.value("language", "ko")
        self.current_theme = self.settings.value("theme", "dark")
        
        self.setWindowTitle(self.tr_text("Browser Name"))
        self.setGeometry(100, 100, 1280, 800)
        
        self.bookmarks = self.load_bookmarks()
        
        # Managers
        self.ime = IMEManager(self)
        self.archiver = ArchiveManager()
        self.kor_input_active = False # Local state for UI sync
        
        # Dragging support
        self._old_pos = None

        # Main Central Widget and Layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # Custom Title Bar
        self.setup_title_bar()

        # Navigation Bar
        self.navbar = QToolBar("Navigation")
        self.navbar.setMovable(False)
        self.navbar.setIconSize(self.navbar.iconSize() * 0.8)
        self.main_layout.addWidget(self.navbar) # Keep this line, the snippet's addLayout was incorrect here
        
        # --- Tabs Layout (Inline flow) ---
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.tabBar().setExpanding(False) # Keep tabs to the left

        self.main_layout.addWidget(self.tabs)

        # Apply monochrome theme
        self.apply_theme()
        
        self.init_ui()

    def setup_title_bar(self):
        self.title_bar = QWidget()
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(30)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        
        # Window Title Label
        self.title_label = QLabel(self.tr_text("Browser Name"))
        self.title_label.setObjectName("WindowTitle")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Window Buttons
        min_btn = QPushButton()
        min_btn.setIcon(self.get_icon("minimize"))
        min_btn.setProperty("class", "WindowButton")
        min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(min_btn)
        
        self.max_btn = QPushButton()
        self.max_btn.setIcon(self.get_icon("maximize"))
        self.max_btn.setProperty("class", "WindowButton")
        self.max_btn.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(self.max_btn)
        
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setProperty("class", "WindowButton")
        self.close_btn.clicked.connect(self.close)
        title_layout.addWidget(self.close_btn)
        
        self.main_layout.addWidget(self.title_bar)

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.max_btn.setIcon(self.get_icon("maximize"))
        else:
            self.showMaximized()
            self.max_btn.setIcon(self.get_icon("restore"))

    # Mouse events for dragging frameless window
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.title_bar.underMouse():
            self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._old_pos is not None:
            delta = event.globalPosition().toPoint() - self._old_pos
            self.move(self.pos() + delta)
            self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._old_pos = None

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if self.title_bar.underMouse():
            self.toggle_maximize()

    def keyPressEvent(self, event):
        """전역 키 이벤트 - 오른쪽 Alt로 한영 전환"""
        from PySide6.QtCore import Qt
        if event.key() == Qt.Key_AltGr or (event.key() == Qt.Key_Alt and event.nativeScanCode() == 108):
            # 오른쪽 Alt 키 (한영 전환)
            self.toggle_internal_ime()
            return
        super().keyPressEvent(event)

    def get_icon(self, name):
        # Use simple relative path from CWD (root)
        icon_path = f"assets/icons/{name}.svg"
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def tr_text(self, key):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS['ko']).get(key, key)

    def init_ui(self):
        self.navbar.clear()

        # 1. Navigation Actions (Primary Left)
        back_btn = QAction(self.get_icon("back"), "", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back() if isinstance(self.tabs.currentWidget(), QWebEngineView) else None)
        self.navbar.addAction(back_btn)

        forward_btn = QAction(self.get_icon("forward"), "", self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward() if isinstance(self.tabs.currentWidget(), QWebEngineView) else None)
        self.navbar.addAction(forward_btn)

        home_btn = QAction(self.get_icon("home"), "", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        # Reload Button with Animation state
        self.reload_btn = QAction(self.get_icon("reload"), "", self)
        self.reload_btn.triggered.connect(self.reload_page)
        self.navbar.addAction(self.reload_btn)

        # Bookmark Button (Toolbar Only)
        self.bookmark_btn = QAction(self.get_icon("star"), "", self)
        self.bookmark_btn.triggered.connect(self.add_bookmark)
        self.navbar.addAction(self.bookmark_btn)

        # 2. URL Bar (Expanding) - 한글 입력 지원
        self.url_bar = HangulLineEdit()
        self.url_bar.setPlaceholderText("Search or enter address")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.hangul_toggle_requested.connect(self.toggle_internal_ime)
        # Only Lock Icon allowed here
        self.security_action = self.url_bar.addAction(self.get_icon("unlock"), HangulLineEdit.LeadingPosition)
        self.navbar.addWidget(self.url_bar)

        # Archive (REC) Button - Placed right after URL Bar
        self.rec_btn = QToolButton()
        self.rec_btn.setIcon(self.get_icon("circle_red"))
        self.rec_btn.setToolTip("Start Archiving (REC)")
        self.rec_btn.clicked.connect(self.toggle_recording)
        self.rec_btn.setPopupMode(QToolButton.MenuButtonPopup)
        
        # Rec Menu for Advanced Options
        rec_menu = QMenu(self)
        adv_action = QAction("Advanced Capture...", self)
        adv_action.triggered.connect(self.open_archive_config)
        rec_menu.addAction(adv_action)
        self.rec_btn.setMenu(rec_menu)
        
        self.navbar.addWidget(self.rec_btn)

        # 3. Secondary Actions (Right)
        # Internal Korean Input Button
        self.ime_btn = QPushButton(self.tr_text("Korean Input"))
        self.ime_btn.setCheckable(True)
        self.ime_btn.setObjectName("PrimaryButton")
        self.ime_btn.setFixedSize(90, 32)
        self.ime_btn.clicked.connect(self.toggle_internal_ime)
        self.navbar.addWidget(self.ime_btn)

        # Menu Button
        self.menu_btn_widget = QPushButton()
        self.menu_btn_widget.setIcon(self.get_icon("menu"))
        self.menu_btn_widget.setFixedSize(32, 32)
        self.menu_btn_widget.setObjectName("SecondaryButton")
        self.menu_btn_widget.setMenu(self.create_menu())
        self.navbar.addWidget(self.menu_btn_widget)

        # Animation Setup
        self.reload_angle = 0
        self.reload_timer = QVariantAnimation(self)
        self.reload_timer.setStartValue(0)
        self.reload_timer.setEndValue(360)
        self.reload_timer.setDuration(1000)
        self.reload_timer.setLoopCount(-1)
        self.reload_timer.valueChanged.connect(self.animate_reload)

        # Add initial tab if none
        if self.tabs.count() == 0:
            self.add_new_tab(QUrl('https://www.google.com'), self.tr_text('Home'))

        # Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def apply_theme(self):
        self.setStyleSheet(get_stylesheet(self.current_theme))
        # Update title bar icons that change based on theme contrast requirements
        if hasattr(self, 'close_btn'):
            icon_name = "close_black" if self.current_theme == "dark" else "close_white"
            self.close_btn.setIcon(self.get_icon(icon_name))

    def toggle_internal_ime(self):
        self.kor_input_active = self.ime.toggle()
        self.ime_btn.setChecked(self.kor_input_active)
        # 주소창에도 한글 모드 적용
        self.url_bar.set_hangul_active(self.kor_input_active)
        msg = "Korean Input (Internal) ON" if self.kor_input_active else "Korean Input (Internal) OFF"
        self.status.showMessage(msg, 2000)

    def apply_ime_state(self):
        self.ime.apply_to_all_tabs()

    def change_kbd_layout(self, layout_id):
        self.settings.setValue("kbd_layout", layout_id)
        self.apply_ime_state()
        self.status.showMessage(f"Keyboard Layout Changed: {layout_id}", 2000)

    def create_menu(self):
        menu = QMenu(self)
        
        # Bookmarks with Collections
        bm_menu = menu.addMenu(self.tr_text("Bookmarks"))
        for coll, items in self.bookmarks.items():
            if isinstance(items, dict):
                coll_menu = bm_menu.addMenu(coll)
                for title, url in items.items():
                    action = coll_menu.addAction(title)
                    action.triggered.connect(lambda checked=False, u=url: self.open_url(u))
            else:
                # Top level bookmarks (legacy support or single-level bookmarks)
                action = bm_menu.addAction(coll)
                action.triggered.connect(lambda checked=False, u=items: self.open_url(u))
        
        menu.addSeparator()

        # Theme Toggle
        theme_action = QAction(f"Theme: {self.current_theme.upper()}", self)
        theme_action.triggered.connect(self.toggle_theme)
        menu.addAction(theme_action)

        menu.addSeparator()
        
        # Global Password Manager (Internal Tab)
        pwd_action = QAction(self.tr_text("Password Manager"), self)
        pwd_action.triggered.connect(self.open_password_tab)
        menu.addAction(pwd_action)

        # Settings (Internal Tab)
        settings_action = QAction(self.tr_text("Settings"), self)
        settings_action.triggered.connect(self.open_settings_tab)
        menu.addAction(settings_action)

        menu.addSeparator()

        # Archive Dashboard (New Modded Feature)
        archive_action = QAction("Archive Dashboard (Pro)", self)
        archive_action.triggered.connect(self.open_archive_dashboard)
        menu.addAction(archive_action)
        
        return menu

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.settings.setValue("theme", self.current_theme)
        self.apply_theme()
        # Refresh menu to update text
        self.menu_btn_widget.setMenu(self.create_menu())

    def reset_settings(self):
        reply = QMessageBox.question(self, self.tr_text("Confirm Reset"), 
                                   self.tr_text("Are you sure you want to reset all settings to defaults?"),
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Revert to defaults
            for key, val in DEFAULT_SETTINGS.items():
                self.settings.setValue(key, val)
            
            # Re-sync current instance
            self.current_lang = DEFAULT_SETTINGS['language']
            self.current_theme = DEFAULT_SETTINGS['theme']
            self.kor_input_active = False # Reset IME toggle too
            
            # Apply Changes
            self.apply_theme()
            self.toggle_language() # This re-inits UI and internal tabs
            self.status.showMessage("Settings Reset to Defaults", 3000)

    def open_password_tab(self):
        self.add_new_tab(internal="passwords", label=self.tr_text("Password Manager"))

    def open_settings_tab(self):
        self.add_new_tab(internal="settings", label=self.tr_text("Settings"))

    def open_archive_dashboard(self):
        self.add_new_tab(internal="archive", label="Archive Dashboard")

    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'ko' else 'ko'
        self.settings.setValue("language", self.current_lang)
        
        # Re-initialize UI elements that use translations
        self.init_ui() 
        self.menu_btn_widget.setMenu(self.create_menu())
        self.title_label.setText(self.tr_text("Browser Name"))

        # Update all internal tabs and re-translate browser tab titles
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, SettingsPage):
                new_settings = SettingsPage(self, self.current_lang)
                self.tabs.removeTab(i)
                self.tabs.insertTab(i, new_settings, self.tr_text("Settings"))
                self.tabs.setCurrentIndex(i)
            elif isinstance(widget, PasswordPage):
                new_pwd = PasswordPage(self, self.current_lang)
                self.tabs.removeTab(i)
                self.tabs.insertTab(i, new_pwd, self.tr_text("Password Manager"))
                self.tabs.setCurrentIndex(i)
            elif isinstance(widget, QWebEngineView):
                # If it's the home page, we might want to update its tab text if it was 'Home'
                if self.tabs.tabText(i) in [TRANSLATIONS['ko']['Home'], TRANSLATIONS['en']['Home']]:
                    self.tabs.setTabText(i, self.tr_text('Home'))

    def load_bookmarks(self):
        try:
            if os.path.exists('bookmarks.json'):
                with open('bookmarks.json', 'r') as f:
                    return json.load(f)
            else:
                with open('bookmarks.json', 'w') as f:
                    json.dump({}, f)
        except:
            pass
        return {}

    def save_bookmarks(self):
        with open('bookmarks.json', 'w') as f:
            json.dump(self.bookmarks, f)

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, self.tr_text("Export Browser Data"), "primity_data.json", "JSON Files (*.json)")
        if path:
            data = {
                "bookmarks": self.bookmarks,
                "settings": {key: self.settings.value(key) for key in self.settings.allKeys()}
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.status.showMessage(f"Data exported to {path}", 3000)

    def import_data(self):
        path, _ = QFileDialog.getOpenFileName(self, self.tr_text("Import Browser Data"), "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Import bookmarks
                if "bookmarks" in data:
                    self.bookmarks.update(data["bookmarks"])
                    self.save_bookmarks()
                
                # Import settings
                if "settings" in data:
                    for key, val in data["settings"].items():
                        self.settings.setValue(key, val)
                
                self.status.showMessage("Data successfully imported", 3000)
                self.reset_ui_after_import()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import data: {e}")

    def reset_ui_after_import(self):
        # Refresh current state
        self.current_lang = self.settings.value("language", "ko")
        self.current_theme = self.settings.value("theme", "dark")
        self.apply_theme()
        self.toggle_language()
        self.menu_btn_widget.setMenu(self.create_menu())

    def reload_page(self):
        curr = self.tabs.currentWidget()
        if isinstance(curr, QWebEngineView):
            curr.reload()

    def animate_reload(self, value):
        # Rotate the reload icon based on value (0-360)
        pixmap = self.get_icon("reload_yellow").pixmap(24, 24)
        if pixmap.isNull(): return
        
        from PySide6.QtGui import QTransform, QPainter
        
        # Create a new pixmap for rotation
        rotated_pixmap = QPixmap(pixmap.size())
        rotated_pixmap.fill(Qt.transparent)
        
        painter = QPainter(rotated_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Center of the pixmap
        center = pixmap.rect().center()
        
        # Translate to center, rotate, translate back
        transform = QTransform()
        transform.translate(center.x(), center.y())
        transform.rotate(value)
        transform.translate(-center.x(), -center.y())
        
        painter.setTransform(transform)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        
        self.reload_btn.setIcon(QIcon(rotated_pixmap))

    def start_reload_anim(self, browser):
        if browser == self.tabs.currentWidget():
            self.reload_btn.setIcon(self.get_icon("reload_yellow"))
            self.reload_timer.start()

    def stop_reload_anim(self, browser):
        if browser == self.tabs.currentWidget():
            self.reload_timer.stop()
            self.reload_btn.setIcon(self.get_icon("reload_green"))
            # Fader effect simulation
            from PySide6.QtCore import QTimer
            QTimer.singleShot(800, lambda: self.reload_btn.setIcon(self.get_icon("reload")))

    def add_bookmark(self):
        widget = self.tabs.currentWidget()
        if not isinstance(widget, QWebEngineView): return

        url = widget.url().toString()
        title = widget.title()
        
        # 1. State Analysis: Is it already bookmarked?
        current_coll = "Bookmarks Bar"
        found_name = title
        is_existing = False
        
        # Search existing
        for coll, items in self.bookmarks.items():
            if isinstance(items, dict):
                for name, link in items.items():
                    if link == url:
                        current_coll = coll
                        found_name = name
                        is_existing = True
                        break
            if is_existing: break
            
        collections = list(self.bookmarks.keys())
        if not collections: collections = ["Bookmarks Bar"]
        
        # 2. Show Dialog
        dlg = BookmarkDialog(self, found_name, url, collections, current_coll)
        if dlg.exec():
            action = dlg.action_code
            data = dlg.result_data
            
            if action == 'delete':
                if is_existing:
                    # Remove from old collection
                    if current_coll in self.bookmarks and found_name in self.bookmarks[current_coll]:
                        del self.bookmarks[current_coll][found_name]
                        # Cleanup empty collections if needed, or keep them
                        self.save_bookmarks()
                        self.update_bookmark_indicator()
                        self.menu_btn_widget.setMenu(self.create_menu())
                        self.status.showMessage("Bookmark Removed", 2000)
            
            elif action == 'save':
                new_coll = data['collection']
                new_name = data['name']
                
                # If editing, remove old entry first
                if is_existing:
                    if current_coll in self.bookmarks and found_name in self.bookmarks[current_coll]:
                        del self.bookmarks[current_coll][found_name]
                
                # Add to new collection
                if new_coll not in self.bookmarks:
                    self.bookmarks[new_coll] = {}
                elif not isinstance(self.bookmarks[new_coll], dict):
                    # legacy support or type mismatch fix
                    self.bookmarks[new_coll] = {}
                    
                self.bookmarks[new_coll][new_name] = url
                
                self.save_bookmarks()
                self.update_bookmark_indicator()
                self.menu_btn_widget.setMenu(self.create_menu())
                self.status.showMessage(f"Saved to {new_coll}", 2000)

    def update_bookmark_indicator(self):
        widget = self.tabs.currentWidget()
        if not isinstance(widget, QWebEngineView):
            self.bookmark_btn.setIcon(self.get_icon("star"))
            return
            
        url = widget.url().toString()
        is_bookmarked = False
        
        # Search in all collections (v0.0.31 supports nested bookmarks)
        for coll_name, coll_data in self.bookmarks.items():
            if isinstance(coll_data, dict):
                if url in coll_data.values():
                    is_bookmarked = True
                    break
            elif coll_data == url: # Legacy support
                is_bookmarked = True
                break
        
        if is_bookmarked:
            self.bookmark_btn.setIcon(self.get_icon("star_yellow"))
        else:
            self.bookmark_btn.setIcon(self.get_icon("star"))

    def suggest_password(self):
        from PySide6.QtWidgets import QApplication
        new_pwd = generate_strong_password()
        QApplication.clipboard().setText(new_pwd)
        QMessageBox.information(self, "Password Suggestion", 
                                f"Detected password field.\nSuggested strong password has been copied to clipboard:\n\n{new_pwd}")

    def open_url(self, url):
        self.add_new_tab(QUrl(url))

    def toggle_recording(self, options=None):
        if self.archiver.is_recording:
            self.archiver.stop_recording()
            self.rec_btn.setIcon(self.get_icon("circle_red"))
            self.rec_btn.setToolTip("Start Archiving (REC)")
            self.status.showMessage("Archiving Stopped", 2000)
        else:
            current_url = "about:blank"
            if isinstance(self.tabs.currentWidget(), QWebEngineView):
                current_url = self.tabs.currentWidget().url().toString()
                
            self.archiver.start_recording(current_url, "User Session", options)
            self.rec_btn.setIcon(self.get_icon("circle_white"))
            self.rec_btn.setToolTip("Stop Archiving")
            self.status.showMessage("Archiving Started...", 2000)
            
            # Inject script into current page immediately
            curr = self.tabs.currentWidget()
            if isinstance(curr, QWebEngineView):
                self.inject_archiver(curr)

    def open_archive_config(self):
        dlg = ArchiveConfigDialog(self, lang=self.current_lang)
        if dlg.exec():
            options = dlg.get_options()
            self.toggle_recording(options)

    def inject_archiver(self, browser):
        script = self.archiver.get_injection_script()
        browser.page().runJavaScript(script)

    def add_new_tab(self, qurl=None, label="New Tab", internal=None):
        if internal == "passwords":
            widget = PasswordPage(self, self.current_lang)
        elif internal == "settings":
            widget = SettingsPage(self, self.current_lang)
        elif internal == "archive":
            widget = ArchiveDashboard(self)
        else:
            if qurl is None:
                qurl = QUrl('https://www.google.com')
            widget = QWebEngineView()
            widget.setAttribute(Qt.WA_InputMethodEnabled, True)
            
            # Additional settings for focus and input compatibility
            widget.settings().setAttribute(QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, True)
            widget.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            
            # Simple script to detect password focus and log to console
            detection_script = """
            document.addEventListener('focusin', function(e) {
                if (e.target.type === 'password') {
                    console.log("PRIMITY_PWD_FOCUS");
                }
            });
            """
            
            # Software IME Integration
            self.ime.inject_script(widget)
            
            # Archiver Integration
            # We inject script on load finished to ensure context is ready, 
            # OR typically we need to inject via UserScript for early capture.
            # For now, simplistic injection on load started/finished.
            if self.archiver.is_recording:
                # Note: To capture early requests, we really need QWebEngineScript/UserScripts.
                # runJavaScript is late-bound. 
                # But for our 'current view' strategy, re-injecting on load is okay for user actions.
                widget.loadFinished.connect(lambda _, b=widget: self.inject_archiver(b))

            # Connect reload state triggers
            widget.loadStarted.connect(lambda b=widget: self.start_reload_anim(b))
            widget.loadFinished.connect(lambda _, b=widget: self.stop_reload_anim(b))
            widget.urlChanged.connect(lambda _, b=widget: self.update_bookmark_indicator())

            # Handle notification via console messages
            def handle_console_message(level, message, line, source):
                if "PRIMITY_PWD_FOCUS" in message:
                    self.suggest_password()
                elif "PRIMITY_IME_TOGGLED_VIA_KBD" in message:
                    active = "true" in message.lower()
                    self.kor_input_active = active
                    self.ime.active = active # Sync manager state
                    self.ime_btn.setChecked(active)
            
            widget.page().javaScriptConsoleMessage = handle_console_message

            widget.setUrl(qurl)
            widget.urlChanged.connect(lambda qurl, browser=widget: self.update_url_bar(qurl, browser))
            widget.loadFinished.connect(lambda _, browser=widget: 
                                         self.tabs.setTabText(self.tabs.indexOf(browser), browser.title()))
            widget.titleChanged.connect(lambda title, browser=widget:
                                         self.tabs.setTabText(self.tabs.indexOf(browser), title))
            
            # Favicon Support
            widget.iconChanged.connect(lambda icon, browser=widget:
                                       self.tabs.setTabIcon(self.tabs.indexOf(browser), icon))
            
        i = self.tabs.addTab(widget, label)
        self.tabs.setCurrentIndex(i)

        # Set default icon for web pages if newly created
        if isinstance(widget, QWebEngineView):
            self.tabs.setTabIcon(i, self.get_icon("globe"))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        if self.tabs.count() > 0:
            widget = self.tabs.currentWidget()
            if isinstance(widget, QWebEngineView):
                qurl = widget.url()
                self.update_url_bar(qurl, widget)
                self.update_title(widget)
                self.update_bookmark_indicator()
            else:
                self.url_bar.setText(f"primity://{type(widget).__name__.lower().replace('page','')}")
                tab_text = self.tabs.tabText(i)
                self.title_label.setText(f"{self.tr_text('Browser Name')} | {tab_text}")

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        title = browser.title()
        if title:
            self.title_label.setText(f"{self.tr_text('Browser Name')} | {title}")
        else:
            self.title_label.setText(self.tr_text('Browser Name'))

    def navigate_home(self):
        home = self.settings.value("home_url", "https://www.google.com")
        curr = self.tabs.currentWidget()
        if isinstance(curr, QWebEngineView):
            curr.setUrl(QUrl(home))
        else:
            self.add_new_tab(QUrl(home), "Home")

    def navigate_to_url(self):
        text = self.url_bar.text().strip()
        if not text:
            return
            
        # Smart URL vs Search detection
        if "." not in text or " " in text:
            # Likely a search query
            q = QUrl(f"https://www.google.com/search?q={text}")
        else:
            q = QUrl(text)
            if not q.scheme():
                q.setScheme("https") # Default to https for direct URLs
        
        curr = self.tabs.currentWidget()
        if isinstance(curr, QWebEngineView):
            curr.setUrl(q)
        else:
            self.add_new_tab(q, "Loading...")

    def update_url_bar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        url_str = q.toString()
        self.url_bar.setText(url_str)
        self.url_bar.setCursorPosition(0)
        self.update_lock_icon(q)

    def update_lock_icon(self, qurl):
        if qurl.scheme() == "https":
            self.security_action.setIcon(self.get_icon("lock"))
        elif qurl.scheme() in ["http", "primity"]:
            self.security_action.setIcon(self.get_icon("unlock"))
        else:
            self.security_action.setIcon(QIcon())
