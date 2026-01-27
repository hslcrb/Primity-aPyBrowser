"""
Primity Native Hangul IME for Qt Widgets
=========================================
한글 입력기 - Qt 네이티브 위젯(QLineEdit 등)용
"""

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QKeyEvent

# 한글 조합 테이블
BASE_CODE = 0xAC00
CHO_TABLE = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
JUN_TABLE = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
JON_TABLE = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

# 복합 모음 조합
MIX_VOWEL_MAP = {
    8: {0: 9, 1: 10, 20: 11},   # ㅗ + ㅏ=ㅘ, ㅐ=ㅙ, ㅣ=ㅚ
    13: {4: 14, 5: 15, 20: 16}, # ㅜ + ㅓ=ㅝ, ㅔ=ㅞ, ㅣ=ㅟ
    18: {20: 19}                # ㅡ + ㅣ=ㅢ
}

# 복합 종성 조합
MIX_JONG_MAP = {
    1: {19: 3},   # ㄱ+ㅅ=ㄳ
    4: {22: 5, 27: 6},  # ㄴ+ㅈ=ㄵ, ㄴ+ㅎ=ㄶ
    8: {1: 9, 16: 10, 17: 11, 19: 12, 25: 13, 26: 14, 27: 15},  # ㄹ+...
    17: {19: 18}  # ㅂ+ㅅ=ㅄ
}

# 복합 종성 분해
REVERSE_JONG_MAP = {}
for first, seconds in MIX_JONG_MAP.items():
    for second, combined in seconds.items():
        REVERSE_JONG_MAP[combined] = (first, second)

# 두벌식 자판 매핑
LAYOUT_DUBEOL = {
    'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
    'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
    'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
    'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'O': 'ㅒ', 'P': 'ㅖ'
}


class HangulLineEdit(QLineEdit):
    """한글 입력이 가능한 QLineEdit"""
    
    # 한영 전환 요청 시그널 (부모 창에서 처리)
    hangul_toggle_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hangul_active = False
        self.state = 0  # 0=empty, 1=cho, 2=jun, 3=jon
        self.idx_cho = -1
        self.idx_jun = -1
        self.idx_jon = 0
        
    def set_hangul_active(self, active):
        """한글 모드 활성화/비활성화"""
        self.hangul_active = active
        if not active:
            self.reset()
    
    def reset(self):
        """상태 초기화"""
        self.state = 0
        self.idx_cho = -1
        self.idx_jun = -1
        self.idx_jon = 0
    
    def get_cho_index(self, char):
        return CHO_TABLE.index(char) if char in CHO_TABLE else -1
    
    def get_jun_index(self, char):
        return JUN_TABLE.index(char) if char in JUN_TABLE else -1
    
    def get_jon_index(self, char):
        return JON_TABLE.index(char) if char in JON_TABLE else 0
    
    def make_syllable(self, c, v, t):
        return chr(BASE_CODE + (c * 588) + (v * 28) + t)
    
    def keyPressEvent(self, event: QKeyEvent):
        # 오른쪽 Alt 키 (한영 전환) 처리
        if event.key() == Qt.Key_AltGr or (event.key() == Qt.Key_Alt and event.nativeScanCode() == 108):
            self.hangul_toggle_requested.emit()
            return
        
        # 한글 모드가 아니면 기본 처리
        if not self.hangul_active:
            super().keyPressEvent(event)
            return
        
        # 특수 키 처리
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Escape, Qt.Key_Tab):
            self.reset()
            super().keyPressEvent(event)
            return
        
        # 방향키, Home, End 등
        if event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, 
                          Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown):
            self.reset()
            super().keyPressEvent(event)
            return
        
        # 백스페이스
        if event.key() == Qt.Key_Backspace:
            if self.state != 0:
                self.process_backspace()
                return
            else:
                super().keyPressEvent(event)
                return
        
        # Delete 키
        if event.key() == Qt.Key_Delete:
            self.reset()
            super().keyPressEvent(event)
            return
        
        # Ctrl, Alt 조합은 패스 (Ctrl+C, Ctrl+V 등)
        if event.modifiers() & (Qt.ControlModifier | Qt.MetaModifier):
            super().keyPressEvent(event)
            return
        
        # 입력된 문자 가져오기
        key_text = event.text()
        if not key_text or len(key_text) != 1:
            super().keyPressEvent(event)
            return
        
        # 한글 매핑
        mapped = LAYOUT_DUBEOL.get(key_text)
        if not mapped:
            # 한글이 아닌 문자 (숫자, 특수문자 등)는 그냥 입력
            self.reset()
            super().keyPressEvent(event)
            return
        
        # 한글 조합 처리
        self.process_input(mapped)
    
    def process_input(self, char):
        is_consonant = char in CHO_TABLE
        is_vowel = char in JUN_TABLE
        
        in_cho = self.get_cho_index(char) if is_consonant else -1
        in_jun = self.get_jun_index(char) if is_vowel else -1
        in_jon = self.get_jon_index(char) if is_consonant else 0
        
        # State 0: Empty
        if self.state == 0:
            if is_consonant:
                self.state = 1
                self.idx_cho = in_cho
                self.commit(CHO_TABLE[self.idx_cho])
            else:
                self.commit(char)
                self.reset()
            return
        
        # State 1: Cho (초성만)
        if self.state == 1:
            if is_vowel:
                self.state = 2
                self.idx_jun = in_jun
                self.update_char(self.make_syllable(self.idx_cho, self.idx_jun, 0))
            else:
                self.reset()
                self.state = 1
                self.idx_cho = in_cho
                self.commit(CHO_TABLE[self.idx_cho])
            return
        
        # State 2: Cho + Jun (초성+중성)
        if self.state == 2:
            if is_vowel:
                # 복합 모음 시도
                if self.idx_jun in MIX_VOWEL_MAP and in_jun in MIX_VOWEL_MAP[self.idx_jun]:
                    self.idx_jun = MIX_VOWEL_MAP[self.idx_jun][in_jun]
                    self.update_char(self.make_syllable(self.idx_cho, self.idx_jun, 0))
                else:
                    self.reset()
                    self.commit(char)
            else:
                if in_jon > 0:
                    self.state = 3
                    self.idx_jon = in_jon
                    self.update_char(self.make_syllable(self.idx_cho, self.idx_jun, self.idx_jon))
                else:
                    self.reset()
                    self.state = 1
                    self.idx_cho = in_cho
                    self.commit(CHO_TABLE[self.idx_cho])
            return
        
        # State 3: Cho + Jun + Jon (초성+중성+종성)
        if self.state == 3:
            if is_vowel:
                # 연음 처리 - 종성을 다음 글자의 초성으로
                prev_jon = self.idx_jon
                left_jon = 0
                moved_cho = -1
                
                if prev_jon in REVERSE_JONG_MAP:
                    left_jon = REVERSE_JONG_MAP[prev_jon][0]
                    jong_char = JON_TABLE[REVERSE_JONG_MAP[prev_jon][1]]
                    moved_cho = self.get_cho_index(jong_char)
                else:
                    left_jon = 0
                    moved_cho = self.get_cho_index(JON_TABLE[prev_jon])
                
                self.update_char(self.make_syllable(self.idx_cho, self.idx_jun, left_jon))
                self.reset()
                self.state = 2
                self.idx_cho = moved_cho
                self.idx_jun = in_jun
                self.commit(self.make_syllable(self.idx_cho, self.idx_jun, 0))
            else:
                # 복합 종성 시도
                if self.idx_jon in MIX_JONG_MAP and in_jon in MIX_JONG_MAP[self.idx_jon]:
                    self.idx_jon = MIX_JONG_MAP[self.idx_jon][in_jon]
                    self.update_char(self.make_syllable(self.idx_cho, self.idx_jun, self.idx_jon))
                else:
                    self.reset()
                    self.state = 1
                    self.idx_cho = in_cho
                    self.commit(CHO_TABLE[self.idx_cho])
            return
    
    def process_backspace(self):
        if self.state == 1:
            # 초성만 있으면 삭제
            text = self.text()
            cursor = self.cursorPosition()
            if cursor > 0:
                self.setText(text[:cursor-1] + text[cursor:])
                self.setCursorPosition(cursor - 1)
            self.reset()
        elif self.state == 2:
            # 중성 제거 -> 초성만
            self.state = 1
            self.idx_jun = -1
            self.update_char(CHO_TABLE[self.idx_cho])
        elif self.state == 3:
            # 종성 제거
            if self.idx_jon in REVERSE_JONG_MAP:
                self.idx_jon = REVERSE_JONG_MAP[self.idx_jon][0]
                self.update_char(self.make_syllable(self.idx_cho, self.idx_jun, self.idx_jon))
            else:
                self.state = 2
                self.idx_jon = 0
                self.update_char(self.make_syllable(self.idx_cho, self.idx_jun, 0))
    
    def commit(self, text):
        """새 글자 추가"""
        cursor = self.cursorPosition()
        current = self.text()
        self.setText(current[:cursor] + text + current[cursor:])
        self.setCursorPosition(cursor + len(text))
    
    def update_char(self, text):
        """현재 조합 중인 글자 교체"""
        cursor = self.cursorPosition()
        current = self.text()
        if cursor > 0:
            self.setText(current[:cursor-1] + text + current[cursor:])
            self.setCursorPosition(cursor)
        else:
            self.commit(text)
