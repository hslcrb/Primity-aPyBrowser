from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox
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
        
        # Language Section
        lang_label = QLabel(self.tr('Language'))
        lang_label.setStyleSheet("color: #ccc; font-size: 14px; margin-top: 10px;")
        card_layout.addWidget(lang_label)
        
        lang_btn = QPushButton(f"Language: {self.lang.upper()}")
        lang_btn.setObjectName("SecondaryButton")
        lang_btn.clicked.connect(self.main_window.toggle_language)
        card_layout.addWidget(lang_btn)

        # Keyboard Layout Section
        kbd_label = QLabel(self.tr('Keyboard Layout'))
        kbd_label.setStyleSheet("color: #ccc; font-size: 14px; margin-top: 20px;")
        card_layout.addWidget(kbd_label)

        self.kbd_box = QComboBox()
        self.kbd_box.addItem(self.tr("Dubeolshik"), "dubeol")
        self.kbd_box.addItem(self.tr("Sebeolshik 390"), "sebeol390")
        self.kbd_box.addItem(self.tr("Sebeolshik Final"), "sebeolfinal")
        
        # Set current selection from settings
        current_kbd = self.main_window.settings.value("kbd_layout", "dubeol")
        index = self.kbd_box.findData(current_kbd)
        if index >= 0:
            self.kbd_box.setCurrentIndex(index)
            
        self.kbd_box.currentIndexChanged.connect(self.kbd_changed)
        card_layout.addWidget(self.kbd_box)
        
        card_layout.addStretch()
        layout.addWidget(card)

    def kbd_changed(self, index):
        layout_id = self.kbd_box.itemData(index)
        self.main_window.change_kbd_layout(layout_id)
