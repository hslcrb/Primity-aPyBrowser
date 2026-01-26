import sys
from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit,
                             QTabWidget, QStatusBar, QVBoxLayout, 
                             QPushButton, QHBoxLayout, QLabel)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWebEngineWidgets import QWebEngineView

class PrimityBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Primity Browser")
        self.setGeometry(100, 100, 1200, 800)
        
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

        # Back Button
        back_btn = QAction("←", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.navbar.addAction(back_btn)

        # Forward Button
        forward_btn = QAction("→", self)
        forward_btn.setStatusTip("Forward to next page")
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.navbar.addAction(forward_btn)

        # Reload Button
        reload_btn = QAction("↻", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.navbar.addAction(reload_btn)

        # Home Button
        home_btn = QAction("🏠", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        # Add initial tab
        self.add_new_tab(QUrl('https://www.google.com'), 'Home')

        # Status Bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

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
