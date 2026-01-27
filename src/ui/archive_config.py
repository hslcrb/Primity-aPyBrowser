from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QCheckBox, 
                             QSpinBox, QDialogButtonBox, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt

class ArchiveConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("고급 캡처 옵션")
        self.resize(420, 320)
        self.cwd_options = {} 
        
        layout = QVBoxLayout(self)
        
        # 크롤링 깊이
        depth_group = QGroupBox("크롤링 깊이")
        depth_layout = QGridLayout()
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(0, 3)
        self.depth_spin.setValue(0)
        self.depth_spin.setToolTip("0=현재 페이지만, 1=직접 링크, 2=2단계 링크...")
        depth_layout.addWidget(QLabel("깊이:"), 0, 0)
        depth_layout.addWidget(self.depth_spin, 0, 1)
        depth_group.setLayout(depth_layout)
        layout.addWidget(depth_group)
        
        # 추출기
        ext_group = QGroupBox("추출기")
        ext_layout = QGridLayout()
        
        self.extractors = {
            "wget": QCheckBox("Wget (HTML)"),
            "singlefile": QCheckBox("SingleFile (HTML+리소스)"),
            "screenshot": QCheckBox("스크린샷"),
            "pdf": QCheckBox("PDF"),
            "dom": QCheckBox("DOM 덤프"),
            "git": QCheckBox("Git (저장소)"),
            "media": QCheckBox("미디어 (유튜브 등)"),
            "archive_org": QCheckBox("Archive.org에 제출")
        }
        
        # 기본값
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
        
        # 버튼
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("확인")
        buttons.button(QDialogButtonBox.Cancel).setText("취소")
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
