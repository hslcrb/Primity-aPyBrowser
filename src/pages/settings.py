from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QComboBox, QLineEdit, QHBoxLayout, QScrollArea, QTextBrowser)
from src.config.constants import TRANSLATIONS
from src.config.manual import MANUAL_KO, MANUAL_EN
from src.ui.components import MinimalCard

class SettingsPage(QWidget):
    def __init__(self, main_window, lang='ko'):
        super().__init__()
        self.main_window = main_window
        self.lang = lang
        self.init_ui()

    def tr(self, key):
        return TRANSLATIONS.get(self.lang, TRANSLATIONS['ko']).get(key, key)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 20, 50, 50)
        
        # Scroll Area for many settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # --- GENERAL SETTINGS ---
        gen_card = MinimalCard()
        gen_layout = QVBoxLayout(gen_card)
        gen_layout.setContentsMargins(30, 30, 30, 30)
        
        gen_title = QLabel(self.tr('General Settings'))
        gen_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom:  profile10px;")
        gen_layout.addWidget(gen_title)
        
        # Home Page URL
        hp_label = QLabel(self.tr('Home Page'))
        hp_label.setStyleSheet("color: #888; font-size: 13px; margin-top: 10px;")
        gen_layout.addWidget(hp_label)
        
        self.home_page_edit = QLineEdit()
        self.home_page_edit.setText(self.main_window.settings.value("home_url", "https://www.google.com"))
        self.home_page_edit.textChanged.connect(self.save_home_url)
        gen_layout.addWidget(self.home_page_edit)
        
        # Language
        lang_label = QLabel(self.tr('Language'))
        lang_label.setStyleSheet("color: #888; font-size: 13px; margin-top: 10px;")
        gen_layout.addWidget(lang_label)
        
        lang_btn = QPushButton(f"Language: {self.lang.upper()}")
        lang_btn.setObjectName("SecondaryButton")
        lang_btn.clicked.connect(self.main_window.toggle_language)
        gen_layout.addWidget(lang_btn)
        
        layout.addWidget(gen_card)
        
        # --- KEYBOARD SETTINGS ---
        kbd_card = MinimalCard()
        kbd_layout = QVBoxLayout(kbd_card)
        kbd_layout.setContentsMargins(30, 30, 30, 30)
        
        kbd_title = QLabel(self.tr('Keyboard Settings'))
        kbd_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;")
        kbd_layout.addWidget(kbd_title)
        
        # Kbd Layout
        kbd_label = QLabel(self.tr('Keyboard Layout'))
        kbd_label.setStyleSheet("color: #888; font-size: 13px; margin-top: 10px;")
        kbd_layout.addWidget(kbd_label)

        self.kbd_box = QComboBox()
        self.kbd_box.addItem(self.tr("Dubeolshik"), "dubeol")
        self.kbd_box.addItem(self.tr("Sebeolshik 390"), "sebeol390")
        self.kbd_box.addItem(self.tr("Sebeolshik Final"), "sebeolfinal")
        self.kbd_box.addItem(self.tr("English"), "english")
        
        current_kbd = self.main_window.settings.value("kbd_layout", "dubeol")
        index = self.kbd_box.findData(current_kbd)
        if index >= 0: self.kbd_box.setCurrentIndex(index)
            
        self.kbd_box.currentIndexChanged.connect(self.kbd_changed)
        kbd_layout.addWidget(self.kbd_box)
        
        layout.addWidget(kbd_card)
        
        # --- DATA MANAGEMENT ---
        data_card = MinimalCard()
        data_layout = QVBoxLayout(data_card)
        data_layout.setContentsMargins(30, 30, 30, 30)
        
        data_title = QLabel(self.tr("Data Management"))
        data_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;")
        data_layout.addWidget(data_title)
        
        btn_layout = QHBoxLayout()
        export_btn = QPushButton(self.tr('Export Browser Data'))
        export_btn.setObjectName("SecondaryButton")
        export_btn.clicked.connect(self.main_window.export_data)
        
        import_btn = QPushButton(self.tr('Import Browser Data'))
        import_btn.setObjectName("SecondaryButton")
        import_btn.clicked.connect(self.main_window.import_data)
        
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(import_btn)
        data_layout.addLayout(btn_layout)
        
        layout.addWidget(data_card)

        # --- ARCHIVE SETTINGS ---
        arc_card = MinimalCard()
        arc_layout = QVBoxLayout(arc_card)
        arc_layout.setContentsMargins(30, 30, 30, 30)
        
        arc_title = QLabel("Archive Settings")
        arc_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;")
        arc_layout.addWidget(arc_title)
        
        # Storage Path
        path_label = QLabel("Storage Path (Requires Restart)")
        path_label.setStyleSheet("color: #888; font-size: 13px; margin-top: 10px;")
        arc_layout.addWidget(path_label)
        
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.main_window.settings.value("archive_path", "data"))
        self.path_edit.setReadOnly(True)
        path_layout.addWidget(self.path_edit)
        
        path_btn = QPushButton("Change...")
        path_btn.setObjectName("SecondaryButton")
        path_btn.clicked.connect(self.change_archive_path)
        path_layout.addWidget(path_btn)
        
        arc_layout.addLayout(path_layout)
        arc_layout.addLayout(path_layout)
        layout.addWidget(arc_card)
        
        # --- USER MANUAL ---
        manual_card = MinimalCard()
        manual_layout = QVBoxLayout(manual_card)
        manual_layout.setContentsMargins(30, 30, 30, 30)
        
        manual_title = QLabel(self.tr("User Manual"))
        manual_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;")
        manual_layout.addWidget(manual_title)
        
        self.manual_browser = QTextBrowser()
        self.manual_browser.setOpenExternalLinks(True)
        self.manual_browser.setStyleSheet("background-color: transparent; border: none; color: #ccc; font-size: 14px;")
        
        # Markdown Content based on Language
        content = MANUAL_KO if self.lang == 'ko' else MANUAL_EN
        self.manual_browser.setMarkdown(content)
        self.manual_browser.setFixedHeight(400) # Fixed height for manual section
        
        manual_layout.addWidget(self.manual_browser)
        layout.addWidget(manual_card)
        
        # --- SYSTEM ---
        sys_card = MinimalCard()
        sys_layout = QVBoxLayout(sys_card)
        sys_layout.setContentsMargins(30, 30, 30, 30)
        
        reset_btn = QPushButton(self.tr('Reset to Defaults'))
        reset_btn.setObjectName("DangerButton")
        reset_btn.clicked.connect(self.main_window.reset_settings)
        sys_layout.addWidget(reset_btn)
        
        layout.addWidget(sys_card)
        
        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def save_home_url(self, text):
        self.main_window.settings.setValue("home_url", text)

    def kbd_changed(self, index):
        layout_id = self.kbd_box.itemData(index)
        self.main_window.change_kbd_layout(layout_id)

    def change_archive_path(self):
        from PySide6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "Select Archive Data Directory")
        if path:
            self.path_edit.setText(path)
            self.main_window.settings.setValue("archive_path", path)
            self.main_window.archiver.update_storage_path(path)
