/**
 * Primity Multi-Standard Hangul Automata Engine
 * Supports Dubeolshik, Sebeolshik 390, Sebeolshik Final, and English.
 */
(function () {
    const BASE = 0xAC00;
    const CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];
    const JUN = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"];
    const JON = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];

    const COMP_JUN = { 'ㅗㅏ': 9, 'ㅗㅐ': 10, 'ㅗㅣ': 11, 'ㅜㅓ': 14, 'ㅜㅔ': 15, 'ㅜㅣ': 16, 'ㅡㅣ': 19 };
    const COMP_JON = { 'ㄱㅅ': 3, 'ㄴㅈ': 5, 'ㄴㅎ': 6, 'ㄹㄱ': 9, 'ㄹㅁ': 10, 'ㄹㅂ': 11, 'ㄹㅅ': 12, 'ㄹㅌ': 13, 'ㄹㅍ': 14, 'ㄹㅎ': 15, 'ㅂㅅ': 18 };

    const LAYOUTS = {
        'dubeol': {
            'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
            'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
            'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
            'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'O': 'ㅒ', 'P': 'ㅖ'
        },
        'sebeol390': {
            '8': 'ㅛ', '9': 'ㅕ', '0': 'ㅑ', '-': 'ㅐ', '=': 'ㅒ',
            'i': 'ㅓ', 'o': 'ㅏ', 'p': 'ㅣ', '[': 'ㅔ', ']': 'ㅖ',
            'k': 'ㄴ', 'l': 'ㅇ', ';': 'ㄹ', "'": 'ㅎ',
            'm': 'ㅁ', ',': 'ㅊ', '.': 'ㅌ', '/': 'ㅍ',
            'h': 'ㅗ', 'j': 'ㅓ', 'n': 'ㅜ' // Simplified for 390
        },
        'english': {} // Empty map means pass-through
    };

    let hangulActive = false;
    let currentLayout = 'dubeol';

    class Buffer {
        constructor() { this.reset(); }
        reset() { this.cho = -1; this.jun = -1; this.jon = -1; this.jon2 = -1; }
        get char() {
            if (this.cho === -1) return "";
            if (this.jun === -1) return CHO[this.cho];
            let fJon = this.jon;
            if (this.jon2 !== -1) {
                const combined = COMP_JON[JON[this.jon] + JON[this.jon2]];
                if (combined) fJon = combined;
            }
            return String.fromCharCode(BASE + (this.cho * 588) + (this.jun * 28) + (fJon > 0 ? fJon : 0));
        }
        decompose() {
            if (this.jon2 !== -1) { this.jon2 = -1; return true; }
            if (this.jon !== -1) { this.jon = -1; return true; }
            if (this.jun !== -1) {
                for (let key in COMP_JUN) { if (COMP_JUN[key] === this.jun) { this.jun = JUN.indexOf(key[0]); return true; } }
                this.jun = -1; return true;
            }
            if (this.cho !== -1) { this.cho = -1; return true; }
            return false;
        }
    }

    const B = new Buffer();
    let isComposing = false;

    window.addEventListener('PRIMITY_TOGGLE_IME', (e) => {
        hangulActive = e.detail.active;
        if (e.detail.layout) currentLayout = e.detail.layout;
        B.reset(); isComposing = false;
    });

    document.addEventListener('keydown', function (e) {
        if (e.code === 'AltRight' || e.key === 'HangulMode') {
            hangulActive = !hangulActive;
            B.reset(); isComposing = false;
            e.preventDefault(); return;
        }

        if (!hangulActive || currentLayout === 'english' || e.ctrlKey || e.altKey || e.metaKey) return;

        const k = (LAYOUTS[currentLayout] || LAYOUTS['dubeol'])[e.key];
        if (!k) {
            if (e.key === 'Backspace' && isComposing) {
                if (B.decompose()) {
                    if (B.cho === -1) { undo(e.target); isComposing = false; }
                    else { update(e.target, B.char); }
                    e.preventDefault();
                }
            } else { B.reset(); isComposing = false; }
            return;
        }

        e.preventDefault();
        const target = e.target;
        const isC = CHO.includes(k);

        if (isC) handleC(target, k);
        else handleV(target, k);
    }, true);

    function handleC(target, k) {
        const cIdx = CHO.indexOf(k), jIdx = JON.indexOf(k);
        if (!isComposing) { B.cho = cIdx; isComposing = true; insert(target, B.char); }
        else {
            if (B.jun === -1) { B.reset(); B.cho = cIdx; insert(target, B.char); }
            else if (B.jon === -1) { if (jIdx > 0) { B.jon = jIdx; update(target, B.char); } else { B.reset(); B.cho = cIdx; insert(target, B.char); } }
            else if (B.jon2 === -1) { const comb = COMP_JON[JON[B.jon] + k]; if (comb) { B.jon2 = JON.indexOf(k); update(target, B.char); } else { B.reset(); B.cho = cIdx; insert(target, B.char); } }
            else { B.reset(); B.cho = cIdx; insert(target, B.char); }
        }
    }

    function handleV(target, k) {
        const vIdx = JUN.indexOf(k);
        if (!isComposing) insert(target, k);
        else {
            if (B.jun === -1) { B.jun = vIdx; update(target, B.char); }
            else if (B.jon === -1) { const comb = COMP_JUN[JUN[B.jun] + k]; if (comb) { B.jun = comb; update(target, B.char); } else { B.reset(); insert(target, k); isComposing = false; } }
            else {
                let moveC = -1, leftJon = -1;
                if (B.jon2 !== -1) { moveC = CHO.indexOf(JON[B.jon2]); leftJon = B.jon; }
                else moveC = CHO.indexOf(JON[B.jon]);
                if (moveC !== -1) {
                    const prevCho = B.cho, prevJun = B.jun;
                    update(target, String.fromCharCode(BASE + (prevCho * 588) + (prevJun * 28) + (leftJon > 0 ? leftJon : 0)));
                    B.reset(); B.cho = moveC; B.jun = vIdx; insert(target, B.char);
                } else { B.reset(); insert(target, k); isComposing = false; }
            }
        }
    }

    function insert(el, t) {
        if (el.isContentEditable) document.execCommand('insertText', false, t);
        else {
            const s = el.selectionStart, e = el.selectionEnd, v = el.value;
            el.value = v.slice(0, s) + t + v.slice(e);
            el.selectionStart = el.selectionEnd = s + t.length;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    function update(el, t) {
        if (el.isContentEditable) { document.execCommand('undo'); document.execCommand('insertText', false, t); }
        else {
            const s = el.selectionStart - 1, v = el.value;
            el.value = v.slice(0, s) + t + v.slice(s + 1);
            el.selectionStart = el.selectionEnd = s + 1;
        }
    }
})();
