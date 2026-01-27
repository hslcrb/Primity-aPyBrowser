from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QCheckBox, 
                             QSpinBox, QDialogButtonBox, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt

# 번역 데이터
ARCHIVE_TRANSLATIONS = {
    'ko': {
        'title': '고급 캡처 옵션',
        'depth_group': '크롤링 깊이',
        'depth_label': '깊이:',
        'depth_tooltip': '0=현재 페이지만, 1=직접 링크, 2=2단계 링크...',
        'extractors_group': '추출기',
        'wget': 'Wget (HTML)',
        'singlefile': 'SingleFile (HTML+리소스)',
        'screenshot': '스크린샷',
        'pdf': 'PDF',
        'dom': 'DOM 덤프',
        'git': 'Git (저장소)',
        'media': '미디어 (유튜브 등)',
        'archive_org': 'Archive.org에 제출',
        'ok': '확인',
        'cancel': '취소'
    },
    'en': {
        'title': 'Advanced Capture Options',
        'depth_group': 'Crawling Depth',
        'depth_label': 'Depth:',
        'depth_tooltip': '0=Current page only, 1=Direct links, 2=2-level links...',
        'extractors_group': 'Extractors',
        'wget': 'Wget (HTML)',
        'singlefile': 'SingleFile (HTML+Assets)',
        'screenshot': 'Screenshot',
        'pdf': 'PDF',
        'dom': 'DOM Dump',
        'git': 'Git (Repository)',
        'media': 'Media (Youtube-DL)',
        'archive_org': 'Submit to Archive.org',
        'ok': 'OK',
        'cancel': 'Cancel'
    }
}

class ArchiveConfigDialog(QDialog):
    def __init__(self, parent=None, lang='ko'):
        super().__init__(parent)
        self.lang = lang
        self.tr = ARCHIVE_TRANSLATIONS.get(lang, ARCHIVE_TRANSLATIONS['ko'])
        self.cwd_options = {} 
        
        self.setWindowTitle(self.tr['title'])
        self.resize(420, 320)
        
        layout = QVBoxLayout(self)
        
        # 크롤링 깊이
        depth_group = QGroupBox(self.tr['depth_group'])
        depth_layout = QGridLayout()
        self.depth_spin = QSpinBox()
        self.depth_spin.setRange(0, 3)
        self.depth_spin.setValue(0)
        self.depth_spin.setToolTip(self.tr['depth_tooltip'])
        depth_layout.addWidget(QLabel(self.tr['depth_label']), 0, 0)
        depth_layout.addWidget(self.depth_spin, 0, 1)
        depth_group.setLayout(depth_layout)
        layout.addWidget(depth_group)
        
        # 추출기
        ext_group = QGroupBox(self.tr['extractors_group'])
        ext_layout = QGridLayout()
        
        self.extractors = {
            "wget": QCheckBox(self.tr['wget']),
            "singlefile": QCheckBox(self.tr['singlefile']),
            "screenshot": QCheckBox(self.tr['screenshot']),
            "pdf": QCheckBox(self.tr['pdf']),
            "dom": QCheckBox(self.tr['dom']),
            "git": QCheckBox(self.tr['git']),
            "media": QCheckBox(self.tr['media']),
            "archive_org": QCheckBox(self.tr['archive_org'])
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
        buttons.button(QDialogButtonBox.Ok).setText(self.tr['ok'])
        buttons.button(QDialogButtonBox.Cancel).setText(self.tr['cancel'])
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
