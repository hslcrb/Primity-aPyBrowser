import sys
import json
import os
from PySide6.QtCore import QUrl, Qt, QSettings
from PySide6.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit,
                             QTabWidget, QStatusBar, QWidget, QVBoxLayout, 
                             QPushButton, QHBoxLayout, QLabel, QMenu, QDialog, 
                             QFormLayout, QMessageBox, QInputDialog, QListWidget)
from PySide6.QtGui import QIcon, QAction
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
        'Confirm Delete': '정말로 삭제하시겠습니까?'
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
        'Confirm Delete': 'Are you sure you want to delete?'
    }
}

class PasswordManagerDialog(QDialog):
    def __init__(self, parent=None, lang='ko'):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(self.tr('Password Manager'))
        self.resize(500, 400)
        self.layout = QVBoxLayout(self)

        self.passwords = self.load_passwords()

        self.list_widget = QListWidget()
        self.refresh_list()
        self.layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton(self.tr('Add'))
        add_btn.clicked.connect(self.add_password)
        del_btn = QPushButton(self.tr('Delete'))
        del_btn.clicked.connect(self.delete_password)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        self.layout.addLayout(btn_layout)

    def tr(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS['ko']).get(key, key)

    def load_passwords(self):
        try:
            if os.path.exists('passwords.json'):
                with open('passwords.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_passwords(self):
        with open('passwords.json', 'w') as f:
            json.dump(self.passwords, f)

    def refresh_list(self):
        self.list_widget.clear()
        for site, creds in self.passwords.items():
            self.list_widget.addItem(f"{site} | {creds['username']}")

    def add_password(self):
        site, ok1 = QInputDialog.getText(self, self.tr('Site'), "URL:")
        if ok1 and site:
            user, ok2 = QInputDialog.getText(self, self.tr('Username'), "ID:")
            if ok2 and user:
                pwd, ok3 = QInputDialog.getText(self, self.tr('Password'), "PW:", QLineEdit.Password)
                if ok3 and pwd:
                    self.passwords[site] = {'username': user, 'password': pwd}
                    self.save_passwords()
                    self.refresh_list()

    def delete_password(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            site = current_item.text().split(' | ')[0]
            if QMessageBox.question(self, self.tr('Delete'), self.tr('Confirm Delete')) == QMessageBox.Yes:
                del self.passwords[site]
                self.save_passwords()
                self.refresh_list()

class PrimityBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("Primity", "Browser")
        self.current_lang = self.settings.value("language", "ko")
        
        self.setWindowTitle("Primity Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        self.bookmarks = self.load_bookmarks()
        
        # Apply modern dark theme
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

        # Back Button
        back_btn = QAction("←", self)
        back_btn.setStatusTip(self.tr_text("Back"))
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.navbar.addAction(back_btn)

        # Forward Button
        forward_btn = QAction("→", self)
        forward_btn.setStatusTip(self.tr_text("Forward"))
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.navbar.addAction(forward_btn)

        # Reload Button
        reload_btn = QAction("↻", self)
        reload_btn.setStatusTip(self.tr_text("Reload"))
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.navbar.addAction(reload_btn)

        # Home Button
        home_btn = QAction("🏠", self)
        home_btn.setStatusTip(self.tr_text("Home"))
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        # Bookmark Button
        self.bookmark_btn = QAction("★", self)
        self.bookmark_btn.setStatusTip(self.tr_text("Add Bookmark"))
        self.bookmark_btn.triggered.connect(self.add_bookmark)
        self.navbar.addAction(self.bookmark_btn)

        # Menu Button - Simplified to a direct menu action for better toolbar integration
        # In QToolBar, we can use a helper QToolButton or just an action.
        # Here we use an action that triggers a menu popup logic if needed, 
        # but QAction.setMenu is for QToolButton mainly.
        # Let's use a simple button widget in the toolbar.
        self.menu_btn_widget = QPushButton("☰")
        self.menu_btn_widget.setFixedSize(30, 30)
        self.menu_btn_widget.setStyleSheet("border: none; color: #b0b0b0; font-size: 16px; background: transparent;")
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

        # Password Manager
        pwd_action = QAction(self.tr_text("Password Manager"), self)
        pwd_action.triggered.connect(self.open_password_manager)
        menu.addAction(pwd_action)

        # Language Toggle
        lang_action = QAction(f"Language: {self.current_lang.upper()}", self)
        lang_action.triggered.connect(self.toggle_language)
        menu.addAction(lang_action)
        
        return menu

    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'ko' else 'ko'
        self.settings.setValue("language", self.current_lang)
        self.init_ui() # Rebuild UI
        # Re-set menu for the button
        self.menu_btn_widget.setMenu(self.create_menu())
        QMessageBox.information(self, "Language", f"Language changed to {self.current_lang.upper()}")

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
        url = self.tabs.currentWidget().url().toString()
        title = self.tabs.currentWidget().title()
        self.bookmarks[title] = url
        self.save_bookmarks()
        # Refresh menu
        self.menu_btn_widget.setMenu(self.create_menu())
        self.status.showMessage(f"Bookmarked: {title}", 2000)

    def open_password_manager(self):
        dlg = PasswordManagerDialog(self, self.current_lang)
        dlg.exec()

    def open_url(self, url):
        self.add_new_tab(QUrl(url))

    def apply_styles(self):
        style_sheet = """
        QMainWindow {
            background-color: #2b2b2b;
        }
        QTabWidget::pane {
            border: 1px solid #444;
            background: #2b2b2b;
        }
        QTabBar::tab {
            background: #3c3f41;
            color: #b0b0b0;
            padding: 8px 12px;
            border: 1px solid #444;
            border-bottom-color: #444; 
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 80px;
        }
        QTabBar::tab:selected {
            background: #4e5254;
            color: #ffffff;
            border-bottom-color: #4e5254;
        }
        QToolBar {
            background: #3c3f41;
            border: none;
            padding: 5px;
            spacing: 5px;
        }
        QLineEdit {
            background-color: #2b2b2b;
            color: #dcdcdc;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 4px;
        }
        QStatusBar {
            background-color: #2b2b2b;
            color: #888;
        }
        QMenu {
            background-color: #2b2b2b;
            color: #dcdcdc;
            border: 1px solid #555;
        }
        QMenu::item:selected {
            background-color: #4e5254;
        }
        """
        self.setStyleSheet(style_sheet)

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl('https://www.google.com')

        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # Connect signals
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url_bar(qurl, browser))
        browser.loadFinished.connect(lambda _, browser=browser: 
                                     self.tabs.setTabText(self.tabs.indexOf(browser), browser.title()))
        browser.titleChanged.connect(lambda title, browser=browser:
                                     self.tabs.setTabText(self.tabs.indexOf(browser), title))

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def tab_open_doubleclick(self, i):
        if i == -1: # double click on empty space
            self.add_new_tab()

    def current_tab_changed(self, i):
        if self.tabs.count() > 0:
            qurl = self.tabs.currentWidget().url()
            self.update_url_bar(qurl, self.tabs.currentWidget())
            self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        title = self.tabs.currentWidget().title()
        self.setWindowTitle(f"{title} - Primity Browser")

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

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
