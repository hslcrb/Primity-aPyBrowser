from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QCheckBox, 
                             QSpinBox, QDialogButtonBox, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt

class ArchiveConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Capture Options")
        self.resize(400, 300)
        self.cwd_options = {} 
        
        layout = QVBoxLayout(self)
        
        # Depth
        depth_group = QGroupBox("Crawling Depth")
        depth_layout = QGridLayout()
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(0, 3)
        self.depth_spin.setValue(0)
        self.depth_spin.setToolTip("0=Single Page, 1=Direct Links, etc.")
        depth_layout.addWidget(QLabel("Depth:"), 0, 0)
        depth_layout.addWidget(self.depth_spin, 0, 1)
        depth_group.setLayout(depth_layout)
        layout.addWidget(depth_group)
        
        # Extractors
        ext_group = QGroupBox("Extractors")
        ext_layout = QGridLayout()
        
        self.extractors = {
            "wget": QCheckBox("Wget (HTML)"),
            "singlefile": QCheckBox("SingleFile (HTML+Assets)"),
            "screenshot": QCheckBox("Screenshot"),
            "pdf": QCheckBox("PDF"),
            "dom": QCheckBox("DOM Dump"),
            "git": QCheckBox("Git (Repo)"),
            "media": QCheckBox("Media (Youtube-DL)"),
            "archive_org": QCheckBox("Submit to Archive.org")
        }
        
        # Defaults
        defaults = ["wget", "singlefile", "screenshot", "dom"]
        
        row = 0
        col = 0
        for key, cb in self.extractors.items():
            cb.setChecked(key in defaults)
            ext_layout.addWidget(cb, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        ext_group.setLayout(ext_layout)
        layout.addWidget(ext_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def get_options(self):
        opts = {
            "depth": self.depth_spin.value(),
            "extractors": {}
        }
        for key, cb in self.extractors.items():
            opts["extractors"][key] = cb.isChecked()
        return opts
