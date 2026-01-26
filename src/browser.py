import json
import os
from PySide6.QtCore import QUrl, QSettings, Qt, Signal, QObject, Slot, QPoint
from PySide6.QtWidgets import (QMainWindow, QToolBar, QLineEdit, QTabWidget, 
                             QStatusBar, QPushButton, QMenu, QMessageBox, QVBoxLayout, 
                             QWidget, QHBoxLayout, QLabel)
from PySide6.QtGui import QAction, QIcon, QPixmap, QMouseEvent
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel

from src.config import TRANSLATIONS
from src.ui_components import get_stylesheet
from src.pages.passwords import PasswordPage
from src.pages.settings import SettingsPage
from src.utils import generate_strong_password

# Bridge class for JS to Python communication
class PasswordBridge(QObject):
    passwordFocused = Signal()

    @Slot()
    def onPasswordFocused(self):
        self.passwordFocused.emit()

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
        
        # Dragging support
        self._old_pos = None

        # Bridge for password detection
        self.bridge = PasswordBridge()
        self.bridge.passwordFocused.connect(self.suggest_password)

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
        self.main_layout.addWidget(self.navbar)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
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

    def get_icon(self, name):
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icons', f"{name}.svg")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        return QIcon()

    def tr_text(self, key):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS['ko']).get(key, key)

    def init_ui(self):
        self.navbar.clear()

        # Back Button
        back_btn = QAction(self.get_icon("back"), "", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back() if isinstance(self.tabs.currentWidget(), QWebEngineView) else None)
        self.navbar.addAction(back_btn)

        # Forward Button
        forward_btn = QAction(self.get_icon("forward"), "", self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward() if isinstance(self.tabs.currentWidget(), QWebEngineView) else None)
        self.navbar.addAction(forward_btn)

        # Reload Button
        reload_btn = QAction(self.get_icon("reload"), "", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload() if isinstance(self.tabs.currentWidget(), QWebEngineView) else None)
        self.navbar.addAction(reload_btn)

        # Home Button
        home_btn = QAction(self.get_icon("home"), "", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        # Bookmark Button
        self.bookmark_btn = QAction(self.get_icon("star"), "", self)
        self.bookmark_btn.triggered.connect(self.add_bookmark)
        self.navbar.addAction(self.bookmark_btn)

        # Menu Button
        self.menu_btn_widget = QPushButton()
        self.menu_btn_widget.setIcon(self.get_icon("menu"))
        self.menu_btn_widget.setFixedSize(36, 36)
        self.menu_btn_widget.setObjectName("SecondaryButton")
        self.menu_btn_widget.setMenu(self.create_menu())
        self.navbar.addWidget(self.menu_btn_widget)

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

    def create_menu(self):
        menu = QMenu(self)
        
        # Bookmarks Submenu
        bookmarks_menu = menu.addMenu(self.tr_text("Bookmarks"))
        for title, url in self.bookmarks.items():
            action = QAction(title, self)
            action.triggered.connect(lambda checked, u=url: self.open_url(u))
            bookmarks_menu.addAction(action)
            
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
        
        return menu

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.settings.setValue("theme", self.current_theme)
        self.apply_theme()
        # Refresh menu to update text
        self.menu_btn_widget.setMenu(self.create_menu())

    def open_password_tab(self):
        self.add_new_tab(internal="passwords", label=self.tr_text("Password Manager"))

    def open_settings_tab(self):
        self.add_new_tab(internal="settings", label=self.tr_text("Settings"))

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

    def add_bookmark(self):
        widget = self.tabs.currentWidget()
        if isinstance(widget, QWebEngineView):
            url = widget.url().toString()
            title = widget.title()
            self.bookmarks[title] = url
            self.save_bookmarks()
            self.menu_btn_widget.setMenu(self.create_menu())
            self.status.showMessage(f"Bookmarked: {title}", 2000)

    def suggest_password(self):
        new_pwd = generate_strong_password()
        QApplication.clipboard().setText(new_pwd)
        QMessageBox.information(self, "Password Suggestion", 
                                f"Detected password field.\nSuggested strong password has been copied to clipboard:\n\n{new_pwd}")

    def open_url(self, url):
        self.add_new_tab(QUrl(url))

    def add_new_tab(self, qurl=None, label="New Tab", internal=None):
        if internal == "passwords":
            widget = PasswordPage(self, self.current_lang)
        elif internal == "settings":
            widget = SettingsPage(self, self.current_lang)
        else:
            if qurl is None:
                qurl = QUrl('https://www.google.com')
            widget = QWebEngineView()
            widget.setAttribute(Qt.WA_InputMethodEnabled, True)
            
            # Setup bridge for password detection injection
            channel = QWebChannel(widget.page())
            widget.page().setWebChannel(channel)
            channel.registerObject("bridge", self.bridge)
            
            injection_script = """
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.bridge = channel.objects.bridge;
                document.addEventListener('focusin', function(e) {
                    if (e.target.type === 'password') {
                        window.bridge.onPasswordFocused();
                    }
                });
            });
            """
            widget.loadFinished.connect(lambda _, b=widget: b.page().runJavaScript(injection_script))

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
        curr = self.tabs.currentWidget()
        if isinstance(curr, QWebEngineView):
            curr.setUrl(QUrl("https://www.google.com"))
        else:
            self.add_new_tab(QUrl("https://www.google.com"), "Home")

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
        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)
