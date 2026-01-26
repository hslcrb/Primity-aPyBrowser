/**
 * Primity Professional Hangul Automata (2-Beolshik)
 * Handles complex syllables and vowels (e.g., '국가와').
 */
(function () {
    const CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];
    const JUNG = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"];
    const JON = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];

    const COMPLEX_JUNG = {
        'ㅗㅏ': 'ㅘ', 'ㅗㅐ': 'ㅙ', 'ㅗㅣ': 'ㅚ',
        'ㅜㅓ': 'ㅝ', 'ㅜㅔ': 'ㅞ', 'ㅜㅣ': 'ㅟ',
        'ㅡㅣ': 'ㅢ'
    };

    const COMPLEX_JON = {
        'ㄱㅅ': 'ㄳ', 'ㄴㅈ': 'ㄵ', 'ㄴㅎ': 'ㄶ', 'ㄹㄱ': 'ㄺ',
        'ㄹㅁ': 'ㄻ', 'ㄹㅂ': 'ㄼ', 'ㄹㅅ': 'ㄽ', 'ㄹㅌ': 'ㄾ',
        'ㄹㅍ': 'ㄿ', 'ㄹㅎ': 'ㅀ', 'ㅂㅅ': 'ㅄ'
    };

    const LAYOUTS = {
        'dubeol': {
            'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
            'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
            'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
            'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'O': 'ㅒ', 'P': 'ㅖ'
        },
        'sebeol390': { /* ... */ }
    };

    let hangulActive = false;
    let currentLayout = 'dubeol';

    // State variables
    let S = 0; // State: 0:Start, 1:Cho, 2:Jung, 3:JungCombined, 4:Jon, 5:JonCombined
    let cI = -1, jI = -1, oI = -1; // Cho index, Jung index, Jon index

    window.addEventListener('PRIMITY_TOGGLE_IME', (e) => {
        hangulActive = e.detail.active;
        if (e.detail.layout) currentLayout = e.detail.layout;
        reset();
    });

    function reset() { S = 0; cI = -1; jI = -1; oI = -1; }

    function makeChar(cidx, jidx, oidx) {
        if (oidx < 0) oidx = 0;
        return String.fromCharCode(0xAC00 + (cidx * 588) + (jidx * 28) + oidx);
    }

    document.addEventListener('keydown', function (e) {
        if (e.code === 'AltRight' || e.key === 'HangulMode') {
            hangulActive = !hangulActive;
            console.log("PRIMITY_IME_TOGGLE:" + hangulActive);
            reset(); e.preventDefault(); return;
        }

        if (!hangulActive) return;
        if (e.ctrlKey || e.altKey || e.metaKey || e.key.length > 1) {
            reset(); return;
        }

        const map = LAYOUTS[currentLayout] || LAYOUTS['dubeol'];
        const kor = map[e.key];
        if (!kor) { reset(); return; }

        e.preventDefault();
        const target = e.target;
        const isConsonant = CHO.includes(kor);

        if (isConsonant) {
            handleConsonant(target, kor);
        } else {
            handleVowel(target, kor);
        }
    }, true);

    function handleConsonant(target, kor) {
        const idx = CHO.indexOf(kor);
        const jidx = JON.indexOf(kor);

        if (S === 0) {
            S = 1; cI = idx;
            insert(target, kor);
        } else if (S === 1) {
            reset(); S = 1; cI = idx;
            insert(target, kor);
        } else if (S === 2 || S === 3) {
            if (jidx > 0) {
                S = 4; oI = jidx;
                update(target, makeChar(cI, jI, oI));
            } else {
                reset(); S = 1; cI = idx;
                insert(target, kor);
            }
        } else if (S === 4) {
            const combined = COMPLEX_JON[JON[oI] + kor];
            if (combined) {
                S = 5; oI = JON.indexOf(combined);
                update(target, makeChar(cI, jI, oI));
            } else {
                reset(); S = 1; cI = idx;
                insert(target, kor);
            }
        } else {
            reset(); S = 1; cI = idx;
            insert(target, kor);
        }
    }

    function handleVowel(target, kor) {
        const idx = JUNG.indexOf(kor);

        if (S === 0) {
            insert(target, kor);
        } else if (S === 1) {
            S = 2; jI = idx;
            update(target, makeChar(cI, jI, 0));
        } else if (S === 2) {
            const combined = COMPLEX_JUNG[JUNG[jI] + kor];
            if (combined) {
                jI = JUNG.indexOf(combined);
                update(target, makeChar(cI, jI, 0));
            } else {
                reset(); insert(target, kor);
            }
        } else if (S === 4 || S === 5) {
            // 연음 법칙: '국' + 'ㅏ' -> '구' + '가'
            let oldJon = JON[oI];
            let newCho = "";
            let leftJon = "";

            // If complex jongsung, split it
            for (let pair in COMPLEX_JON) {
                if (COMPLEX_JON[pair] === oldJon) {
                    leftJon = JON.indexOf(pair[0]);
                    newCho = pair[1];
                    break;
                }
            }

            if (newCho) {
                update(target, makeChar(cI, jI, leftJon));
                S = 2; cI = CHO.indexOf(newCho); jI = idx;
                insert(target, makeChar(cI, jI, 0));
            } else {
                update(target, makeChar(cI, jI, 0));
                S = 2; cI = CHO.indexOf(oldJon); jI = idx;
                insert(target, makeChar(cI, jI, 0));
            }
        } else {
            reset(); insert(target, kor);
        }
    }

    function insert(el, text) {
        if (el.isContentEditable) { document.execCommand('insertText', false, text); }
        else {
            const start = el.selectionStart;
            const end = el.selectionEnd;
            el.value = el.value.slice(0, start) + text + el.value.slice(end);
            el.selectionStart = el.selectionEnd = start + text.length;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    function update(el, text) {
        if (el.isContentEditable) {
            document.execCommand('undo');
            document.execCommand('insertText', false, text);
        } else {
            const start = el.selectionStart - 1;
            el.value = el.value.slice(0, start) + text + el.value.slice(start + 1);
            el.selectionStart = el.selectionEnd = start + 1;
        }
    }
})();
