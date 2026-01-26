from PySide6.QtWidgets import QFrame

class MinimalCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MinimalCard")
