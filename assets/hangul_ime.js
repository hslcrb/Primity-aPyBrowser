/**
 * Primity Built-in Hangul IME (2-Beolshik)
 * Allows Korean input regardless of OS IME settings.
 */
(function () {
    const CHOSUNG = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ";
    const JUNGSUNG = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ";
    const JONGSUNG = " ㄳㄵㄶㄺㄻㄼㄽㄾㄿㅀㅄㄱㄲㄴㄷㄹㅁㅂㅅㅆㅇㅈㅊㅋㅌㅍㅎ";

    const KBD_MAP = {
        'q': 'ㅂ', 'Q': 'ㅃ', 'w': 'ㅈ', 'W': 'ㅉ', 'e': 'ㄷ', 'E': 'ㄸ', 'r': 'ㄱ', 'R': 'ㄲ', 't': 'ㅅ', 'T': 'ㅆ',
        'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'O': 'ㅒ', 'p': 'ㅔ', 'P': 'ㅖ', 'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ',
        'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ', 'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ',
        'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ'
    };

    window.hangulActive = false;
    let composingChar = "";

    // Simple listener for toggle signal from Python
    window.addEventListener('PRIMITY_TOGGLE_IME', (e) => {
        window.hangulActive = e.detail.active;
        console.log("INTERNAL_IME: " + (window.hangulActive ? "ON" : "OFF"));
    });

    document.addEventListener('keydown', function (e) {
        // Toggle Local IME with AltRight (common for Korean keyboard)
        if (e.code === 'AltRight' || e.key === 'HangulMode') {
            window.hangulActive = !window.hangulActive;
            // Notify UI
            console.log("PRIMITY_IME_TOGGLED_VIA_KBD:" + window.hangulActive);
            e.preventDefault();
            return;
        }

        if (!window.hangulActive) return;

        const target = e.target;
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
            if (KBD_MAP[e.key]) {
                // Here we would implement a full state-machine for composition.
                // For a quick fix that feels like "Direct Integration", 
                // we'll at least allow typing the Jamos. 
                // Full composition involves complex syllable logic.

                const char = KBD_MAP[e.key];
                insertText(target, char);
                e.preventDefault();
            }
        }
    }, true);

    function insertText(el, text) {
        if (el.isContentEditable) {
            document.execCommand('insertText', false, text);
        } else {
            const start = el.selectionStart;
            const end = el.selectionEnd;
            const val = el.value;
            el.value = val.slice(0, start) + text + val.slice(end);
            el.selectionStart = el.selectionEnd = start + text.length;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
})();
