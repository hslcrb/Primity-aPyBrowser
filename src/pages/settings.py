from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from src.config import TRANSLATIONS
from src.ui_components import MinimalCard

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
        
        card = MinimalCard()
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
