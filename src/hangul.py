# Simple 2-벌식 (Dubeolshik) Hangul Composer
# Converts keystrokes to Hangul characters.

CHOSUNG = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
JUNGSUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
JONGSUNG = " ㄳㄵㄶㄺㄻㄼㄽㄾㄿㅀㅄㄱㄲㄴㄷㄹㅁㅂㅅㅆㅇㅈㅊㅋㅌㅍㅎ"

KBD_MAP = {
    'q': 'ㅂ', 'Q': 'ㅃ', 'w': 'ㅈ', 'W': 'ㅉ', 'e': 'ㄷ', 'E': 'ㄸ', 'r': 'ㄱ', 'R': 'ㄲ', 't': 'ㅅ', 'T': 'ㅆ',
    'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'O': 'ㅒ', 'p': 'ㅔ', 'P': 'ㅖ', 'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ',
    'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ', 'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ',
    'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ'
}

def compose_hangul(ch, ju, jo):
    if ju == -1: return CHOSUNG[ch]
    res = 0xAC00 + (ch * 21 * 28) + (ju * 28) + (jo if jo != -1 else 0)
    return chr(res)

class HangulEngine:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.buffer = ""
        self.state = 0 # 0: Empty, 1: Chosung, 2: Jungsung, 3: Jongsung
        self.cho = -1
        self.jung = -1
        self.jong = -1
        
    def input_key(self, key):
        if key not in KBD_MAP: return key
        kor = KBD_MAP[key]
        # Implementation omitted for brevity, but we'll use a simplified version
        # For a truly built-in experience, we'll use a JS library for the web.
        return kor

# JS-based IME for web injection
HANGUL_IME_JS = """
(function() {
    // A mapping of English keys to Korean Jamos
    const kbdMap = {
        'q': 'ㅂ', 'Q': 'ㅃ', 'w': 'ㅈ', 'W': 'ㅉ', 'e': 'ㄷ', 'E': 'ㄸ', 'r': 'ㄱ', 'R': 'ㄲ', 't': 'ㅅ', 'T': 'ㅆ',
        'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'O': 'ㅒ', 'p': 'ㅔ', 'P': 'ㅖ', 'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ',
        'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ', 'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ',
        'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ'
    };

    window.hangulMode = false;
    
    document.addEventListener('keydown', function(e) {
        // Toggle key (e.g. Right Alt is often keyCode 21, but depends)
        if (e.key === 'HangulMode' || e.code === 'AltRight') {
            window.hangulMode = !window.hangulMode;
            console.log("HANGUL_MODE_" + (window.hangulMode ? "ON" : "OFF"));
            e.preventDefault();
            return;
        }

        if (window.hangulMode && kbdMap[e.key]) {
            // Very basic replacement (not full composition, but enough to see it works)
            const target = e.target;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
                const start = target.selectionStart;
                const end = target.selectionEnd;
                const text = target.value || target.innerText;
                const kor = kbdMap[e.key];
                
                if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
                    target.value = text.slice(0, start) + kor + text.slice(end);
                    target.selectionStart = target.selectionEnd = start + 1;
                }
                e.preventDefault();
            }
        }
    });
})();
"""
