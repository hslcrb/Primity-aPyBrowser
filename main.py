import sys
import json
import os
from PySide6.QtCore import QUrl, Qt, QSettings, QSize
from PySide6.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit,
                             QTabWidget, QStatusBar, QWidget, QVBoxLayout, 
                             QPushButton, QHBoxLayout, QLabel, QMenu, QDialog, 
                             QFormLayout, QMessageBox, QInputDialog, QListWidget,
                             QScrollArea, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtGui import QIcon, QAction, QColor, QPalette, QLinearGradient, QBrush
from PySide6.QtWebEngineWidgets import QWebEngineView

# Translation Dictionary
TRANSLATIONS = {
    'ko': {
        'Back': '뒤로',
        'Forward': '앞으로',
        'Reload': '새로고침',
        'Home': '홈',
        'New Tab': '새 탭',
        'Settings': '설정',
        'Bookmarks': '즐겨찾기',
        'Add Bookmark': '즐겨찾기 추가',
        'Password Manager': '비밀번호 관리자',
        'Passwords': '비밀번호',
        'Site': '사이트',
        'Username': '사용자명',
        'Password': '비밀번호',
        'Add': '추가',
        'Delete': '삭제',
        'Close': '닫기',
        'Language': '언어',
        'Saved Passwords': '저장된 비밀번호',
        'Confirm Delete': '정말로 삭제하시겠습니까?',
        'App Settings': '앱 설정',
        'Appearance': '디자인'
    },
    'en': {
        'Back': 'Back',
        'Forward': 'Forward',
        'Reload': 'Reload',
        'Home': 'Home',
        'New Tab': 'New Tab',
        'Settings': 'Settings',
        'Bookmarks': 'Bookmarks',
        'Add Bookmark': 'Add Bookmark',
        'Password Manager': 'Password Manager',
        'Passwords': 'Passwords',
        'Site': 'Site',
        'Username': 'Username',
        'Password': 'Password',
        'Add': 'Add',
        'Delete': 'Delete',
        'Close': 'Close',
        'Language': 'Language',
        'Saved Passwords': 'Saved Passwords',
        'Confirm Delete': 'Are you sure you want to delete?',
        'App Settings': 'App Settings',
        'Appearance': 'Appearance'
    }
}

def get_shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setXOffset(0)
    shadow.setYOffset(10)
    shadow.setColor(QColor(0, 0, 0, 150))
    return shadow

class GlassCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GlassCard")
        self.setGraphicsEffect(get_shadow())

class PasswordPage(QWidget):
    def __init__(self, main_window, lang='ko'):
        super().__init__()
        self.main_window = main_window
        self.lang = lang
        self.init_ui()

    def tr(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS['ko']).get(key, key)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        
        card = GlassCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel(self.tr('Password Manager'))
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 20px;")
        card_layout.addWidget(title)
        
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("InternalList")
        card_layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton(self.tr('Add'))
        add_btn.setObjectName("PrimaryButton")
        add_btn.clicked.connect(self.add_password)
        
        del_btn = QPushButton(self.tr('Delete'))
        del_btn.setObjectName("DangerButton")
        del_btn.clicked.connect(self.delete_password)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        card_layout.addLayout(btn_layout)
        
        layout.addWidget(card)
        self.refresh_list()

    def load_passwords(self):
        try:
            if os.path.exists('passwords.json'):
                with open('passwords.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_passwords(self, passwords):
        with open('passwords.json', 'w') as f:
            json.dump(passwords, f)

    def refresh_list(self):
        self.list_widget.clear()
        passwords = self.load_passwords()
        for site, creds in passwords.items():
            self.list_widget.addItem(f"{site} | {creds['username']}")

    def add_password(self):
        site, ok1 = QInputDialog.getText(self, self.tr('Site'), "URL:")
        if ok1 and site:
            user, ok2 = QInputDialog.getText(self, self.tr('Username'), "ID:")
            if ok2 and user:
                pwd, ok3 = QInputDialog.getText(self, self.tr('Password'), "PW:", QLineEdit.Password)
                if ok3 and pwd:
                    passwords = self.load_passwords()
                    passwords[site] = {'username': user, 'password': pwd}
                    self.save_passwords(passwords)
                    self.refresh_list()

    def delete_password(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            site = current_item.text().split(' | ')[0]
            if QMessageBox.question(self, self.tr('Delete'), self.tr('Confirm Delete')) == QMessageBox.Yes:
                passwords = self.load_passwords()
                if site in passwords:
                    del passwords[site]
                    self.save_passwords(passwords)
                    self.refresh_list()

class SettingsPage(QWidget):
    def __init__(self, main_window, lang='ko'):
        super().__init__()
        self.main_window = main_window
        self.lang = lang
        self.init_ui()

    def tr(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS['ko']).get(key, key)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        
        card = GlassCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel(self.tr('App Settings'))
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 20px;")
        card_layout.addWidget(title)
        
        lang_label = QLabel(self.tr('Language'))
        lang_label.setStyleSheet("color: #ccc; font-size: 14px;")
        card_layout.addWidget(lang_label)
        
        lang_btn = QPushButton(f"Language: {self.lang.upper()}")
        lang_btn.setObjectName("SecondaryButton")
        lang_btn.clicked.connect(self.main_window.toggle_language)
        card_layout.addWidget(lang_btn)
        
        card_layout.addStretch()
        layout.addWidget(card)

class PrimityBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Primity", "Browser")
        self.current_lang = self.settings.value("language", "ko")
        
        self.setWindowTitle("Primity Browser")
        self.setGeometry(100, 100, 1280, 800)
        
        self.bookmarks = self.load_bookmarks()
        
        # Apply modern Liquid Glass theme
        self.apply_styles()

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

        # Style for Actions
        nav_style = "QToolButton { padding: 5px; border-radius: 5px; color: white; margin: 2px; } QToolButton:hover { background: rgba(255,255,255,0.1); }"

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
                # Simple refresh: replace with new one
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

    def apply_styles(self):
        style_sheet = """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a2e, stop:1 #16213e);
        }
        QTabWidget::pane {
            border: none;
            background: transparent;
        }
        QTabBar::tab {
            background: rgba(255, 255, 255, 0.05);
            color: #b0b0b0;
            padding: 10px 20px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            margin-right: 2px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-bottom: none;
        }
        QTabBar::tab:selected {
            background: rgba(255, 255, 255, 0.15);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-bottom: none;
        }
        QToolBar {
            background: rgba(255, 255, 255, 0.05);
            border: none;
            padding: 8px;
            spacing: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        QLineEdit {
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 18px;
            padding: 5px 15px;
            font-size: 13px;
        }
        QLineEdit:focus {
            border: 1px solid rgba(255, 255, 255, 0.5);
            background: rgba(0, 0, 0, 0.5);
        }
        QStatusBar {
            background: rgba(0, 0, 0, 0.2);
            color: rgba(255, 255, 255, 0.5);
        }
        QMenu {
            background: rgba(26, 26, 46, 0.95);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        QMenu::item {
            padding: 8px 25px;
        }
        QMenu::item:selected {
            background: rgba(255, 255, 255, 0.1);
        }
        
        #GlassCard {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 20px;
        }
        
        #InternalList {
            background: transparent;
            border: none;
            color: white;
            font-size: 14px;
        }
        
        #PrimaryButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4facfe, stop:1 #00f2fe);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
        }
        #SecondaryButton {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 10px;
        }
        #DangerButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff0844, stop:1 #ffb199);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            font-weight: bold;
        }
        """
        self.setStyleSheet(style_sheet)

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
        if i == -1: # double click on empty space
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Primity Browser")
    window = PrimityBrowser()
    window.show()
    sys.exit(app.exec())
