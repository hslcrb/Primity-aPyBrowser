"""흑백 작업공간 UI. / Monochrome workspace widgets."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QFrame)


def workspace_stylesheet(theme):
    dark = theme == "dark"
    background, surface, foreground, muted, border, hover = (
        ("#141414", "#202020", "#f4f4f4", "#b8b8b8", "#454545", "#303030") if dark
        else ("#f5f5f5", "#ffffff", "#171717", "#585858", "#c8c8c8", "#e8e8e8"))
    return f"""
        QWidget {{ background: {background}; color: {foreground}; font-size: 13px; }}
        QToolBar {{ border: 0; spacing: 5px; padding: 8px; background: {surface}; }}
        QLineEdit {{ background: {background}; border: 1px solid {border};
                    border-radius: 16px; padding: 8px 14px; selection-background-color: {muted}; }}
        QLineEdit:focus {{ border: 2px solid {foreground}; padding: 7px 13px; }}
        QPushButton, QToolButton {{ border: 1px solid transparent; border-radius: 7px; padding: 7px 10px; }}
        QPushButton:hover, QToolButton:hover {{ background: {hover}; border-color: {border}; }}
        QPushButton:focus, QToolButton:focus {{ border-color: {foreground}; }}
        QPushButton:disabled, QToolButton:disabled {{ color: {muted}; }}
        #WorkspaceButton {{ border: 1px solid {border}; font-weight: 600; padding: 8px 14px; }}
        #QuickLink {{ background: {surface}; border: 1px solid {border}; padding: 17px 24px; }}
        #QuickLink:hover {{ background: {hover}; }}
        #Eyebrow, #Muted {{ color: {muted}; }}
        #Brand {{ font-size: 48px; font-weight: 700; letter-spacing: -1px; }}
        #WorkspaceName {{ font-size: 22px; font-weight: 600; }}
        #Divider {{ background: {border}; max-height: 1px; }}
        QTabWidget::pane {{ border: 0; }}
        QTabBar::tab {{ background: {background}; color: {muted}; padding: 10px 16px;
                       min-width: 100px; max-width: 220px; border-top-left-radius: 8px;
                       border-top-right-radius: 8px; }}
        QTabBar::tab:selected {{ background: {surface}; color: {foreground}; }}
        QTabBar::tab:hover {{ background: {hover}; }}
        QStatusBar {{ color: {muted}; border-top: 1px solid {border}; }}
        QProgressBar {{ border: 0; background: {background}; max-height: 3px; }}
        QProgressBar::chunk {{ background: {foreground}; }}
        QMenu {{ background: {surface}; border: 1px solid {border}; padding: 5px; }}
        QMenu::item {{ padding: 7px 22px; }}
        QMenu::item:selected {{ background: {hover}; }}
        QMenu::separator {{ height: 1px; background: {border}; margin: 5px; }}
        QScrollArea {{ border: 0; }}
    """


class NewTabPage(QWidget):
    navigate = Signal(str)
    create_workspace = Signal()
    chrome_requested = Signal()

    def __init__(self, workspace, language="ko", private=False, parent=None):
        super().__init__(parent)
        self.workspace = workspace
        self.language = language
        self.private = private
        t = lambda ko, en: ko if language == "ko" else en
        outer = QVBoxLayout(self)
        outer.setContentsMargins(32, 30, 32, 30)
        outer.addStretch(2)
        content = QWidget()
        content.setMaximumWidth(780)
        layout = QVBoxLayout(content)
        layout.setSpacing(16)
        for text, object_name in (
            ("PRIVATE WORKSPACE" if private else "YOUR OWN WORKSPACE", "Eyebrow"),
            ("Primity", "Brand"), (workspace.name, "WorkspaceName"),
            (t("분리된 계정으로, 익숙한 흐름 그대로.", "Separate accounts. A familiar flow."), "Muted"),
        ):
            label = QLabel(text)
            label.setTextFormat(Qt.PlainText)
            label.setObjectName(object_name)
            label.setAlignment(Qt.AlignCenter)
            label.setWordWrap(True)
            layout.addWidget(label)
        self.search = QLineEdit()
        self.search.setMinimumHeight(48)
        self.search.setPlaceholderText(t("Google 검색 또는 웹 주소 입력", "Search Google or enter a web address"))
        self.search.setAccessibleName(t("검색 또는 주소", "Search or address"))
        self.search.returnPressed.connect(lambda: self.navigate.emit(self.search.text()))
        layout.addWidget(self.search)
        links = QHBoxLayout()
        for title, url in (("Figma", "https://www.figma.com/"),
                           ("Drive", "https://drive.google.com/"),
                           ("GitHub", "https://github.com/"),
                           ("Gmail", "https://mail.google.com/")):
            button = QPushButton(title)
            button.setObjectName("QuickLink")
            button.setToolTip(url)
            button.clicked.connect(lambda checked=False, address=url: self.navigate.emit(address))
            links.addWidget(button)
        layout.addLayout(links)
        divider = QFrame()
        divider.setObjectName("Divider")
        layout.addWidget(divider)
        description = (t("이 창의 사이트 데이터는 창을 닫으면 유지하지 않습니다. 다운로드한 파일은 남습니다.",
                         "This window's site data is temporary. Downloaded files remain.") if private else
                       t("이 작업공간의 로그인과 사이트 데이터는 다른 작업공간과 분리됩니다.",
                         "This workspace keeps its sign-ins and site data separate."))
        hint = QLabel(description)
        hint.setObjectName("Muted")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
        actions = QHBoxLayout()
        actions.addStretch()
        create = QPushButton(t("+ 새 작업공간", "+ New workspace"))
        create.clicked.connect(self.create_workspace.emit)
        actions.addWidget(create)
        chrome = QPushButton(t("Chrome 연결 안내", "About Chrome connection"))
        chrome.clicked.connect(self.chrome_requested.emit)
        chrome.setEnabled(not private)
        actions.addWidget(chrome)
        actions.addStretch()
        layout.addLayout(actions)
        outer.addWidget(content, alignment=Qt.AlignHCenter)
        outer.addStretch(3)

