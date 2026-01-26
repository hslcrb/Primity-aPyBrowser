/**
 * Primity Hyper-Advanced Hangul Automata Engine v2.1
 * Critical Fix: Force liaison for complex vowels (e.g., '세계').
 */
(function () {
    // Hangul Unicode Constants
    const BASE = 0xAC00;
    const CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];
    const JUN = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"];
    const JON = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];

    const COMP_JUN = { 'ㅗㅏ': 9, 'ㅗㅐ': 10, 'ㅗㅣ': 11, 'ㅜㅓ': 14, 'ㅜㅔ': 15, 'ㅜㅣ': 16, 'ㅡㅣ': 19 };
    const COMP_JON = { 'ㄱㅅ': 3, 'ㄴㅈ': 5, 'ㄴㅎ': 6, 'ㄹㄱ': 9, 'ㄹㅁ': 10, 'ㄹㅂ': 11, 'ㄹㅅ': 12, 'ㄹㅌ': 13, 'ㄹㅍ': 14, 'ㄹㅎ': 15, 'ㅂㅅ': 18 };

    const REV_JON = {};
    for (let k in COMP_JON) REV_JON[COMP_JON[k]] = k;

    const LAYOUTS = {
        'dubeol': {
            'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
            'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
            'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
            'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'O': 'ㅒ', 'P': 'ㅖ'
        },
        'sebeol390': { /* Placeholder */ },
        'english': {}
    };

    let hangulActive = false;
    let currentLayout = 'dubeol';

    class Buffer {
        constructor() { this.reset(); }
        reset() { this.cho = -1; this.jun = -1; this.jon = -1; }
        get char() {
            if (this.cho === -1) return "";
            if (this.jun === -1) return CHO[this.cho];
            return String.fromCharCode(BASE + (this.cho * 588) + (this.jun * 28) + (this.jon > 0 ? this.jon : 0));
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
            console.log("IME_TOGGLE:" + hangulActive);
            B.reset(); isComposing = false;
            e.preventDefault(); return;
        }

        if (!hangulActive || currentLayout === 'english' || e.ctrlKey || e.altKey || e.metaKey) return;

        const k = (LAYOUTS[currentLayout] || LAYOUTS['dubeol'])[e.key];
        if (!k) {
            if (e.key === 'Backspace' && isComposing) {
                handleBackspace(e);
            } else {
                B.reset(); isComposing = false;
            }
            return;
        }

        e.preventDefault();
        const target = e.target;
        const isC = CHO.includes(k);

        if (isC) handleConsonant(target, k);
        else handleVowel(target, k);
    }, true);

    function handleConsonant(target, k) {
        const cIdx = CHO.indexOf(k);
        const jIdx = JON.indexOf(k);

        if (!isComposing) {
            B.cho = cIdx; isComposing = true;
            insert(target, B.char);
        } else {
            if (B.jun === -1) {
                B.reset(); B.cho = cIdx; insert(target, B.char);
            } else if (B.jon === -1) {
                if (jIdx > 0) { B.jon = jIdx; update(target, B.char); }
                else { B.reset(); B.cho = cIdx; insert(target, B.char); }
            } else {
                const combined = COMP_JON[JON[B.jon] + k];
                if (combined) { B.jon = combined; update(target, B.char); }
                else { B.reset(); B.cho = cIdx; insert(target, B.char); }
            }
        }
    }

    function handleVowel(target, k) {
        const vIdx = JUN.indexOf(k);

        if (!isComposing) {
            insert(target, k);
        } else {
            if (B.jun === -1) { // 초성만->초+중 (ㅅ+ㅖ -> 셰)
                B.jun = vIdx; update(target, B.char);
            } else if (B.jon === -1) { // 중성 결합 시도 (고+ㅏ -> 과)
                const combined = COMP_JUN[JUN[B.jun] + k];
                if (combined) { B.jun = combined; update(target, B.char); }
                else { B.reset(); insert(target, k); isComposing = false; }
            } else {
                // *** 여기가 핵심: 받침이 있는 상태(섹) + 모음(ㅖ) ***
                // 1. 복합 모음 결합 시도 (거의 없음, 예: 앉+ㅏ 등은 여기 안 옴)
                // 2. 연음 처리: 받침 떼서 뒷글자로 (섹+ㅖ -> 세+계)

                // 받침 분해
                let oldJon = B.jon;
                let leftJon = 0;
                let moveCho = -1;

                if (REV_JON[oldJon]) { // 겹받침
                    const parts = REV_JON[oldJon];
                    leftJon = JON.indexOf(parts[0]);
                    moveCho = CHO.indexOf(parts[1]);
                } else { // 홑받침
                    moveCho = CHO.indexOf(JON[oldJon]); // ㄱ -> 초성 ㄱ
                }

                if (moveCho !== -1) {
                    // 앞 글자: 받침 제거 또는 축소
                    B.jon = leftJon; // 0이면 받침 없음
                    // 앞 글자 업데이트
                    update(target, B.char);

                    // 뒷 글자 시작: 떼어낸 자음 + 현재 입력된 모음
                    B.reset();
                    B.cho = moveCho;
                    B.jun = vIdx;
                    isComposing = true;
                    insert(target, B.char);
                } else {
                    // 받침이 초성으로 갈 수 없는 경우 (거의 없음)
                    B.reset(); insert(target, k); isComposing = false;
                }
            }
        }
    }

    function handleBackspace(e) {
        const target = e.target;
        if (B.jon !== -1) {
            let prevJon = 0;
            if (REV_JON[B.jon]) prevJon = JON.indexOf(REV_JON[B.jon][0]);
            else prevJon = -1;
            B.jon = prevJon;
            if (B.jon === -1) update(target, String.fromCharCode(BASE + (B.cho * 588) + (B.jun * 28)));
            else update(target, B.char);
            e.preventDefault();
        } else if (B.jun !== -1) {
            B.jun = -1;
            update(target, CHO[B.cho]);
            e.preventDefault();
        } else {
            document.execCommand('delete');
            B.reset(); isComposing = false;
            e.preventDefault();
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
        if (el.isContentEditable) {
            const sel = window.getSelection();
            if (sel.rangeCount > 0) {
                const range = sel.getRangeAt(0);
                range.setStart(range.startContainer, range.startOffset - 1);
                range.deleteContents();
                range.insertNode(document.createTextNode(t));
                range.collapse(false);
            }
        } else {
            const s = el.selectionStart - 1, v = el.value;
            el.value = v.slice(0, s) + t + v.slice(s + 1);
            el.selectionStart = el.selectionEnd = s + 1;
        }
    }
})();
