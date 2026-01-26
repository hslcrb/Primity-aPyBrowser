/**
 * Primity Advanced Hangul Automata (Multi-Layout)
 * System-independent Korean input.
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
        'sebeol390': { /* Layout implementation... */ },
        'sebeolfinal': { /* Layout implementation... */ }
    };

    let hangulActive = false;
    let currentLayout = 'dubeol';
    let state = 0; // 0:Empty, 1:Cho, 2:Jung, 3:Jon
    let cIdx = -1, juIdx = -1, joIdx = -1;

    window.addEventListener('PRIMITY_TOGGLE_IME', (e) => {
        hangulActive = e.detail.active;
        if (e.detail.layout) currentLayout = e.detail.layout;
        reset();
    });

    function reset() { state = 0; cIdx = -1; juIdx = -1; joIdx = -1; }

    function getChar() {
        if (state === 0) return "";
        if (state === 1) return CHO[cIdx];
        if (state === 2) return String.fromCharCode(0xAC00 + (cIdx * 588) + (juIdx * 28));
        if (state === 3) return String.fromCharCode(0xAC00 + (cIdx * 588) + (juIdx * 28) + joIdx);
        return "";
    }

    document.addEventListener('keydown', function (e) {
        if (e.code === 'AltRight' || e.key === 'HangulMode') {
            hangulActive = !hangulActive;
            console.log("PRIMITY_IME_TOGGLED_VIA_KBD:" + hangulActive);
            reset(); e.preventDefault(); return;
        }

        if (!hangulActive) return;

        // Skip control keys
        if (e.ctrlKey || e.altKey || e.metaKey || e.key.length > 1) {
            reset(); return;
        }

        const map = LAYOUTS[currentLayout] || LAYOUTS['dubeol'];
        const kor = map[e.key];
        if (!kor) { reset(); return; }

        e.preventDefault();
        const isConsonant = CHO.includes(kor);
        const target = e.target;

        // COMBINATION LOGIC (Simplistic but avoids ㄱㅜㄱㅏ)
        if (isConsonant) {
            if (state === 0) { // Empty -> Cho
                state = 1; cIdx = CHO.indexOf(kor); insertText(target, CHO[cIdx]);
            } else if (state === 1) { // Cho + Cho -> Reset and new Cho
                reset(); state = 1; cIdx = CHO.indexOf(kor); insertText(target, CHO[cIdx]);
            } else if (state === 2) { // Cho + Jung + Cho -> Jon
                const idx = JON.indexOf(kor);
                if (idx > 0) { state = 3; joIdx = idx; updateText(target, getChar()); }
                else { reset(); state = 1; cIdx = CHO.indexOf(kor); insertText(target, CHO[cIdx]); }
            } else if (state === 3) { // Jon + Cho -> New Syllable
                reset(); state = 1; cIdx = CHO.indexOf(kor); insertText(target, CHO[cIdx]);
            }
        } else {
            if (state === 1) { // Cho + Jung -> Syllable
                state = 2; juIdx = JUNG.indexOf(kor); updateText(target, getChar());
            } else if (state === 3) { // Jon + Jung -> Moving Jon to new Cho
                // '국' + 'ㅏ' -> '구가'
                const prevJo = JON[joIdx];
                const newChoIdx = CHO.indexOf(prevJo);
                if (newChoIdx >= 0) {
                    // 1. Remove Jongsung from previous char
                    const finishedChar = String.fromCharCode(0xAC00 + (cIdx * 588) + (juIdx * 28));
                    updateText(target, finishedChar);
                    // 2. Start new char with prevJo as Cho and kor as Jung
                    state = 2; cIdx = newChoIdx; juIdx = JUNG.indexOf(kor);
                    insertText(target, getChar());
                } else {
                    reset(); insertText(target, kor);
                }
            } else {
                reset(); insertText(target, kor);
            }
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
        if (el.isContentEditable) {
            document.execCommand('undo'); // Naive undo
            document.execCommand('insertText', false, text);
        } else {
            const start = el.selectionStart - 1;
            el.value = el.value.slice(0, start) + text + el.value.slice(start + 1);
            el.selectionStart = el.selectionEnd = start + 1;
        }
    }
})();
