from PySide6.QtWidgets import (QFrame, QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox)
from PySide6.QtCore import Qt

class MinimalCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MinimalCard")

class BookmarkDialog(QDialog):
    def __init__(self, parent=None, title="", url="", collections=[], current_collection="Default"):
        super().__init__(parent)
        self.setWindowTitle("Edit Bookmark")
        self.setFixedWidth(350)
        self.result_data = None
        self.action_code = None # 'save' or 'delete'
        
        layout = QVBoxLayout(self)
        
        # Name Input
        layout.addWidget(QLabel("Name"))
        self.name_input = QLineEdit(title)
        layout.addWidget(self.name_input)
        
        # Folder Selection (Editable for new collections)
        layout.addWidget(QLabel("Folder"))
        self.folder_combo = QComboBox()
        self.folder_combo.setEditable(True)
        self.folder_combo.addItems(collections)
        
        # Select current collection if exists, otherwise set text
        index = self.folder_combo.findText(current_collection)
        if index >= 0:
            self.folder_combo.setCurrentIndex(index)
        else:
            self.folder_combo.setCurrentText(current_collection)
            
        layout.addWidget(self.folder_combo)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_delete = QPushButton("Remove")
        self.btn_delete.setObjectName("DangerButton")
        self.btn_delete.clicked.connect(self.on_delete)
        
        self.btn_save = QPushButton("Done")
        self.btn_save.setObjectName("PrimaryButton")
        self.btn_save.setDefault(True)
        self.btn_save.clicked.connect(self.on_save)
        
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        
    def on_save(self):
        self.result_data = {
            'name': self.name_input.text(),
            'collection': self.folder_combo.currentText()
        }
        self.action_code = 'save'
        self.accept()
        
    def on_delete(self):
        self.action_code = 'delete'
        self.accept()
