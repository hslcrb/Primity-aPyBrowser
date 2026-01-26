import json
import os
from PySide6.QtCore import QUrl, QSettings
from PySide6.QtWidgets import (QMainWindow, QToolBar, QLineEdit, QTabWidget, 
                             QStatusBar, QPushButton, QMenu, QMessageBox)
from PySide6.QtGui import QAction
from PySide6.QtWebEngineWidgets import QWebEngineView

from src.config import TRANSLATIONS
from src.ui_components import STYLE_SHEET
from src.pages.passwords import PasswordPage
from src.pages.settings import SettingsPage

class PrimityBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Primity", "Browser")
        self.current_lang = self.settings.value("language", "ko")
        
        self.setWindowTitle("Primity Browser")
        self.setGeometry(100, 100, 1280, 800)
        
        self.bookmarks = self.load_bookmarks()
        
        # Apply modern Liquid Glass theme
        self.setStyleSheet(STYLE_SHEET)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        # Navigation Bar
        self.navbar = QToolBar("Navigation")
        self.navbar.setMovable(False)
        self.addToolBar(self.navbar)
        
        self.init_ui()

    def tr_text(self, key):
        return TRANSLATIONS.get(self.current_lang, TRANSLATIONS['ko']).get(key, key)

    def init_ui(self):
        self.navbar.clear()

        # Back Button
        back_btn = QAction("←", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back() if hasattr(self.tabs.currentWidget(), 'back') else None)
        self.navbar.addAction(back_btn)

        # Forward Button
        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward() if hasattr(self.tabs.currentWidget(), 'forward') else None)
        self.navbar.addAction(forward_btn)

        # Reload Button
        reload_btn = QAction("↻", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload() if hasattr(self.tabs.currentWidget(), 'reload') else None)
        self.navbar.addAction(reload_btn)

        # Home Button
        home_btn = QAction("🏠", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        # Bookmark Button
        self.bookmark_btn = QAction("★", self)
        self.bookmark_btn.triggered.connect(self.add_bookmark)
        self.navbar.addAction(self.bookmark_btn)

        # Menu Button
        self.menu_btn_widget = QPushButton("☰")
        self.menu_btn_widget.setFixedSize(36, 36)
        self.menu_btn_widget.setStyleSheet("border: none; color: white; font-size: 18px; background: transparent;")
        self.menu_btn_widget.setMenu(self.create_menu())
        self.navbar.addWidget(self.menu_btn_widget)

        # Add initial tab if none
        if self.tabs.count() == 0:
            self.add_new_tab(QUrl('https://www.google.com'), self.tr_text('Home'))

        # Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def create_menu(self):
        menu = QMenu(self)
        
        # Bookmarks Submenu
        bookmarks_menu = menu.addMenu(self.tr_text("Bookmarks"))
        for title, url in self.bookmarks.items():
            action = QAction(title, self)
            action.triggered.connect(lambda checked, u=url: self.open_url(u))
            bookmarks_menu.addAction(action)
            
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

    def open_password_tab(self):
        self.add_new_tab(internal="passwords", label=self.tr_text("Password Manager"))

    def open_settings_tab(self):
        self.add_new_tab(internal="settings", label=self.tr_text("Settings"))

    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'ko' else 'ko'
        self.settings.setValue("language", self.current_lang)
        self.init_ui() 
        self.menu_btn_widget.setMenu(self.create_menu())
        # If settings tab is open, update it
        for i in range(self.tabs.count()):
            widget = self.tabs.widget(i)
            if isinstance(widget, SettingsPage):
                new_settings = SettingsPage(self, self.current_lang)
                self.tabs.removeTab(i)
                self.tabs.insertTab(i, new_settings, self.tr_text("Settings"))
                self.tabs.setCurrentIndex(i)
                break

    def load_bookmarks(self):
        try:
            if os.path.exists('bookmarks.json'):
                with open('bookmarks.json', 'r') as f:
                    return json.load(f)
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
            widget.setUrl(qurl)
            widget.urlChanged.connect(lambda qurl, browser=widget: self.update_url_bar(qurl, browser))
            widget.loadFinished.connect(lambda _, browser=widget: 
                                         self.tabs.setTabText(self.tabs.indexOf(browser), browser.title()))
            widget.titleChanged.connect(lambda title, browser=widget:
                                         self.tabs.setTabText(self.tabs.indexOf(browser), title))

        i = self.tabs.addTab(widget, label)
        self.tabs.setCurrentIndex(i)

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
                self.setWindowTitle(f"{self.tabs.tabText(i)} - Primity Browser")

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        title = browser.title()
        self.setWindowTitle(f"{title} - Primity Browser")

    def navigate_home(self):
        curr = self.tabs.currentWidget()
        if isinstance(curr, QWebEngineView):
            curr.setUrl(QUrl("https://www.google.com"))
        else:
            self.add_new_tab(QUrl("https://www.google.com"), "Home")

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        if q.scheme() == "":
            q.setScheme("http")
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
