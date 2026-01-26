# Theme color variables
DARK_VARS = {
    "--bg": "#000000",
    "--fg": "#ffffff",
    "--gray": "#888888",
    "--dark-gray": "#333333",
    "--border": "#222222",
    "--hover": "#222222",
    "--input-bg": "#111111",
    "--tab-bar-bg": "#1a1a1a", # Dark Gray for tab bar in Dark Mode
    "--tab-bg": "#111111",
    "--tab-selected-bg": "#2a2a2a",
    "--close-bg": "#ffffff",
    "--close-hover": "#ff5f56",
    "--danger": "#e81123"
}

LIGHT_VARS = {
    "--bg": "#ffffff",
    "--fg": "#000000",
    "--gray": "#888888",
    "--dark-gray": "#cccccc",
    "--border": "#eeeeee",
    "--hover": "#eeeeee",
    "--input-bg": "#ffffff",
    "--tab-bar-bg": "#f0f0f0", # Light Gray for tab bar in Light Mode
    "--tab-bg": "#e0e0e0",
    "--tab-selected-bg": "#ffffff",
    "--close-bg": "#000000",
    "--close-hover": "#e81123",
    "--danger": "#e81123"
}

BASE_STYLE = """
QMainWindow {
    background: var(--bg);
}
#TitleBar {
    background: var(--bg);
    border-bottom: 1px solid var(--border);
}
#WindowTitle {
    color: var(--gray);
    font-size: 12px;
    padding-left: 10px;
}
QPushButton[class="WindowButton"] {
    background: transparent;
    border: none;
    width: 45px;
    height: 30px;
}
QPushButton[class="WindowButton"]:hover {
    background: var(--hover);
}
QPushButton#CloseButton {
    background: var(--close-bg);
}
QPushButton#CloseButton:hover {
    background: var(--danger);
}
QTabWidget::pane {
    border: none;
    border-top: 1px solid var(--border);
    background: var(--bg);
}
QTabBar {
    background: var(--tab-bar-bg);
    border: none;
}
QTabBar::tab {
    background: var(--tab-bg);
    color: var(--gray);
    padding: 6px 15px;
    border: 1px solid var(--dark-gray);
    border-bottom: none;
    margin-right: 1px;
    font-size: 11px;
    min-width: 80px;
}
QTabBar::tab:selected {
    background: var(--tab-selected-bg);
    color: var(--fg);
    border-top: 2px solid var(--fg);
    border-left: 1px solid var(--border);
    border-right: 1px solid var(--border);
}
QTabBar::tab:hover:!selected {
    background: var(--hover);
}
QTabBar::close-button {
    image: url(assets/icons/close.svg);
    background: transparent;
    border-radius: 0px;
}
QTabBar::close-button:hover {
    background: var(--danger);
}
QToolBar {
    background: var(--bg);
    border: none;
    border-bottom: 1px solid var(--dark-gray);
    padding: 5px;
    spacing: 5px;
}
QLineEdit {
    background: var(--input-bg);
    color: var(--fg);
    border: 1px solid var(--dark-gray);
    padding: 5px 10px;
    border-radius: 0px;
}
QToolButton {
    background: transparent;
    border: none;
    padding: 6px;
    margin: 1px;
}
QToolButton:hover {
    background: var(--hover);
}
QToolButton:pressed {
    background: var(--dark-gray);
}
QStatusBar {
    background: var(--bg);
    color: var(--gray);
    border-top: 1px solid var(--dark-gray);
}
QMenu {
    background: var(--bg);
    color: var(--fg);
    border: 1px solid var(--dark-gray);
}
QMenu::item:selected {
    background: var(--dark-gray);
}
#MinimalCard {
    background: var(--bg);
    border: 1px solid var(--dark-gray);
    border-radius: 0px;
}
#InternalList {
    background: var(--bg);
    border: 1px solid var(--dark-gray);
    color: var(--fg);
}
#PrimaryButton, #SecondaryButton, #DangerButton {
    background: var(--bg);
    color: var(--fg);
    border: 1px solid var(--dark-gray);
    padding: 8px 15px;
    border-radius: 0px;
}
#PrimaryButton:hover, #SecondaryButton:hover, #DangerButton:hover {
    background: var(--hover);
    border: 1px solid var(--gray);
}
QLabel {
    color: var(--fg);
}
"""

def get_stylesheet(theme="dark"):
    vars_dict = DARK_VARS if theme == "dark" else LIGHT_VARS
    style = BASE_STYLE
    for key, value in vars_dict.items():
        style = style.replace(f"var({key})", value)
    return style
