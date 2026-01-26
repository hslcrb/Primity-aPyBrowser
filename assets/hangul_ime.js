/**
 * Primity Hyper-Advanced Hangul Automata Engine (v2.0)
 * Solves '세계' vs '섹ㅖ' logic flaw using full Jamo decomposition and re-composition.
 */
(function () {
    const BASE = 0xAC00;
    const CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];
    const JUN = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"];
    const JON = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];

    const COMP_JUN = { 'ㅗㅏ': 9, 'ㅗㅐ': 10, 'ㅗㅣ': 11, 'ㅜㅓ': 14, 'ㅜㅔ': 15, 'ㅜㅣ': 16, 'ㅡㅣ': 19 };
    const COMP_JON = { 'ㄱㅅ': 3, 'ㄴㅈ': 5, 'ㄴㅎ': 6, 'ㄹㄱ': 9, 'ㄹㅁ': 10, 'ㄹㅂ': 11, 'ㄹㅅ': 12, 'ㄹㅌ': 13, 'ㄹㅍ': 14, 'ㄹㅎ': 15, 'ㅂㅅ': 18 };

    // Reverse mapping for decomposition
    const REV_JON = {};
    for (let k in COMP_JON) REV_JON[COMP_JON[k]] = k;

    const LAYOUTS = {
        'dubeol': {
            'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
            'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
            'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
            'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'O': 'ㅒ', 'P': 'ㅖ'
        },
        'sebeol390': { /* ... existing ... */ },
        'english': {}
    };

    let hangulActive = false;
    let currentLayout = 'dubeol';

    // State Buffer
    class Buffer {
        constructor() { this.reset(); }
        reset() { this.cho = -1; this.jun = -1; this.jon = -1; }

        get char() {
            if (this.cho === -1) return "";
            if (this.jun === -1) return CHO[this.cho];
            return String.fromCharCode(BASE + (this.cho * 588) + (this.jun * 28) + (this.jon > 0 ? this.jon : 0));
        }

        // Returns true if buffer is empty
        get isEmpty() { return this.cho === -1 && this.jun === -1 && this.jon === -1; }
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
        const jIdx = JON.indexOf(k); // Map to Jongsung index if applicable

        if (!isComposing) {
            B.cho = cIdx; isComposing = true;
            insert(target, B.char);
        } else {
            if (B.jun === -1) { // 초성만 있는 상태 (ㄱ -> ㄲ 등 아님, 그냥 앞글자 완료)
                B.reset(); B.cho = cIdx; insert(target, B.char);
            } else if (B.jon === -1) { // 초성+중성 상태 (세 + ㄱ -> 섹)
                if (jIdx > 0) {
                    B.jon = jIdx; update(target, B.char);
                } else { // 받침 불가 자음 (ㄸ, ㅉ, ㅃ 등)
                    B.reset(); B.cho = cIdx; insert(target, B.char);
                }
            } else { // 종성 있는 상태 (섹 -> 셇 or 섹+ㄱ)
                const combined = COMP_JON[JON[B.jon] + k];
                if (combined) {
                    B.jon = combined; update(target, B.char);
                } else {
                    B.reset(); B.cho = cIdx; insert(target, B.char);
                }
            }
        }
    }

    function handleVowel(target, k) {
        const vIdx = JUN.indexOf(k);

        if (!isComposing) {
            insert(target, k);
        } else {
            if (B.jun === -1) { // 초성만 있는 상태 (ㅅ + ㅔ -> 세)
                B.jun = vIdx; update(target, B.char);
            } else if (B.jon === -1) { // 중성 있는 상태 (고 + ㅏ -> 과)
                const combined = COMP_JUN[JUN[B.jun] + k];
                if (combined) {
                    B.jun = combined; update(target, B.char);
                } else {
                    B.reset(); insert(target, k); isComposing = false;
                }
            } else {
                // *** 핵심: '세계' 문제 해결 로직 *** (섹 + ㅖ -> 세 + 계)
                // 1. 현재 종성(ㄱ)을 떼어냄
                let oldJon = B.jon;
                let leftJon = 0;
                let moveCho = -1;

                // 겹받침 분해 (셇 + ㅏ -> 설 + 하)
                if (REV_JON[oldJon]) {
                    const parts = REV_JON[oldJon]; // e.g. 'ㄹㅎ'
                    leftJon = JON.indexOf(parts[0]);
                    moveCho = CHO.indexOf(parts[1]);
                } else {
                    // 홑받침 분해 (섹 + ㅖ -> 세 + 계)
                    moveCho = CHO.indexOf(JON[oldJon]);
                }

                // 2. 앞 글자 업데이트 (받침 제거 or 축소)
                if (moveCho !== -1) {
                    const prevChar = String.fromCharCode(BASE + (B.cho * 588) + (B.jun * 28) + leftJon);
                    update(target, prevChar);

                    // 3. 뒷 글자 시작 (ㄱ + ㅖ -> 계)
                    B.reset();
                    B.cho = moveCho;
                    B.jun = vIdx;
                    isComposing = true;
                    insert(target, B.char);
                } else {
                    // 이론상 올 수 없는 경우
                    B.reset(); insert(target, k); isComposing = false;
                }
            }
        }
    }

    function handleBackspace(e) {
        // 복잡한 역조합 로직 생략, 일단 단순 삭제 처리로 안정성 확보
        // 고급 역조합이 필요하면 추가 구현 가능
        // 현재는 OS 기본 동작에 맡기거나 단순 undo
        // 커스텀 구현 시 로직이 매우 복잡해지므로, 가장 마지막 상태만 되돌림
        const target = e.target;
        if (B.jon !== -1) {
            // 종성 삭제 -> 중성 상태로
            // 겹받침이면 분해 로직 필요, 여기선 단순화
            let prevJon = 0;
            if (REV_JON[B.jon]) { // 겹받침이면 앞쪽만 남김
                prevJon = JON.indexOf(REV_JON[B.jon][0]);
            } else {
                prevJon = -1; // 종성 없음
            }
            B.jon = prevJon;
            if (B.jon === -1)
                update(target, String.fromCharCode(BASE + (B.cho * 588) + (B.jun * 28)));
            else
                update(target, B.char); // 겹받침 앞부분
            e.preventDefault();
        } else if (B.jun !== -1) {
            // 중성 삭제 -> 초성 상태로
            // 복합 모음이면 분해 로직 필요 (ㅘ -> ㅗ)
            B.jun = -1;
            update(target, CHO[B.cho]);
            e.preventDefault();
        } else {
            // 초성 삭제 -> 제거
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
            // Select previous char to replace
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
