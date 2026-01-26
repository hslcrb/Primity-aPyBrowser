import json
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QInputDialog, 
                             QMessageBox, QLineEdit)
from src.config import TRANSLATIONS
from src.ui_components import MinimalCard

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
        
        card = MinimalCard()
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
