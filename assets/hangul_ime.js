/**
 * Primity Full Syllable Hangul Automata (Multi-Layout)
 */
(function () {
    const CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];
    const JUNG = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"];
    const JON = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];

    const LAYOUTS = {
        'dubeol': {
            'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
            'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
            'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
            'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'O': 'ㅒ', 'P': 'ㅖ'
        },
        'sebeol390': {
            // Placeholder for Sebeolshik 390
            'k': 'ㅏ', 'l': 'ㅣ' // ...
        }
    };

    window.hangulActive = false;
    window.currentLayout = 'dubeol';

    window.addEventListener('PRIMITY_TOGGLE_IME', (e) => {
        window.hangulActive = e.detail.active;
        if (e.detail.layout) window.currentLayout = e.detail.layout;
        reset();
    });

    let state = 0; // 0:Empty, 1:Cho, 2:Jung, 3:Jon
    let c = -1, ju = -1, jo = -1;

    function reset() { state = 0; c = -1; ju = -1; jo = -1; }

    function getChar() {
        if (state === 0) return "";
        if (state === 1) return CHO[c];
        if (state === 2) return String.fromCharCode(0xAC00 + (c * 588) + (ju * 28));
        if (state === 3) return String.fromCharCode(0xAC00 + (c * 588) + (ju * 28) + jo);
        return "";
    }

    document.addEventListener('keydown', function (e) {
        if (e.code === 'AltRight' || e.key === 'HangulMode') {
            window.hangulActive = !window.hangulActive;
            console.log("PRIMITY_IME_TOGGLED_VIA_KBD:" + window.hangulActive);
            reset(); e.preventDefault(); return;
        }

        if (!window.hangulActive) return;
        if (e.ctrlKey || e.altKey || e.metaKey || e.key.length > 1) {
            reset(); return;
        }

        const map = LAYOUTS[window.currentLayout] || LAYOUTS['dubeol'];
        const kor = map[e.key];
        if (!kor) { reset(); return; }

        e.preventDefault();
        const isConsonant = CHO.includes(kor);
        const target = e.target;

        // Functional Automata logic for '국가' (ㄱ+ㅜ+ㄱ+ㄱ+ㅏ)
        if (isConsonant) {
            if (state === 0) { state = 1; c = CHO.indexOf(kor); insertText(target, CHO[c]); }
            else if (state === 2) {
                let idx = JON.indexOf(kor);
                if (idx > 0) { state = 3; jo = idx; updateText(target, getChar()); }
                else { reset(); state = 1; c = CHO.indexOf(kor); insertText(target, CHO[c]); }
            }
            else { reset(); state = 1; c = CHO.indexOf(kor); insertText(target, CHO[c]); }
        } else {
            if (state === 1) { state = 2; ju = JUNG.indexOf(kor); updateText(target, getChar()); }
            else { reset(); insertText(target, kor); }
        }
    }, true);

    function insertText(el, text) {
        if (el.isContentEditable) { document.execCommand('insertText', false, text); }
        else {
            const start = el.selectionStart;
            const end = el.selectionEnd;
            el.value = el.value.slice(0, start) + text + el.value.slice(end);
            el.selectionStart = el.selectionEnd = start + text.length;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
    function updateText(el, text) {
        const start = el.selectionStart - 1;
        el.value = el.value.slice(0, start) + text + el.value.slice(start + 1);
        el.selectionStart = el.selectionEnd = start + 1;
    }
})();
