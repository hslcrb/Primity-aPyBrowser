/**
 * Primity Ultimate Hangul Engine v4.0
 * Features "Robust Vowel Acceptance" to fix 'ㄱ'+'ㅖ' -> 'ㄱㅖ' separation bug.
 * Guarantees combination for ALL valid Jamo sequences including direct complex input.
 */
(function () {
    // ----------------------------------------------------------------------
    // Constants & Tables
    // ----------------------------------------------------------------------
    const BASE = 0xAC00;
    const CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];
    const JUN = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"];
    const JON = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];

    // Combinations (Vowel Mixing)
    const JUN_COMBOS = {};
    JUN_COMBOS[8] = { 0: 9, 1: 10, 20: 11 }; // ㅗ + ...
    JUN_COMBOS[13] = { 4: 14, 5: 15, 20: 16 }; // ㅜ + ...
    JUN_COMBOS[18] = { 20: 19 }; // ㅡ + ㅣ

    // Complex Jongsung map
    const JON_COMBOS = {};
    JON_COMBOS[1] = { 19: 3 }; // ㄱ+ㅅ=ㄳ
    JON_COMBOS[4] = { 22: 5, 27: 6 }; // ㄴ+...
    JON_COMBOS[8] = { 1: 9, 16: 10, 17: 11, 19: 12, 25: 13, 26: 14, 27: 15 }; // ㄹ+...
    JON_COMBOS[17] = { 19: 18 }; // ㅂ+ㅅ=ㅄ

    // Reverse map
    const REV_JON = {};
    REV_JON[3] = [1, 19]; REV_JON[5] = [4, 22]; REV_JON[6] = [4, 27];
    REV_JON[9] = [8, 1]; REV_JON[10] = [8, 16]; REV_JON[11] = [8, 17];
    REV_JON[12] = [8, 19]; REV_JON[13] = [8, 25]; REV_JON[14] = [8, 26];
    REV_JON[15] = [8, 27]; REV_JON[18] = [17, 19];

    const KEYMAP = {
        'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
        'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
        'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
        'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'O': 'ㅒ', 'P': 'ㅖ'
    };

    // State Variables
    let state = 0; // 0:Empty, 1:Cho, 2:Cho+Jun, 3:Cho+Jun+Jon
    let idxCho = -1, idxJun = -1, idxJon = 0;
    let hangulActive = false;

    // Helper Functions
    function getChoIdx(c) { return CHO.indexOf(c); }
    function getJunIdx(c) { return JUN.indexOf(c); }
    function getJonIdx(c) { return JON.indexOf(c); }
    function makeChar(c, v, t) {
        return String.fromCharCode(BASE + (c * 588) + (v * 28) + t);
    }
    function reset() { state = 0; idxCho = -1; idxJun = -1; idxJon = 0; }

    // Event Listeners
    window.addEventListener('PRIMITY_TOGGLE_IME', (e) => {
        hangulActive = e.detail.active;
        reset();
    });

    document.addEventListener('keydown', function (e) {
        if (e.code === 'AltRight' || e.key === 'HangulMode') {
            hangulActive = !hangulActive;
            reset();
            e.preventDefault();
            return;
        }

        if (!hangulActive || e.ctrlKey || e.altKey || e.metaKey) return;

        const char = KEYMAP[e.key];
        if (!char) {
            if (e.key === 'Backspace' && state !== 0) {
                processBackspace(e);
                e.preventDefault();
            } else if (!e.key.match(/^[a-zA-Z]$/) && e.key.length === 1) {
                // Symbols/Numbers -> Commit current
                reset();
            }
            return;
        }

        e.preventDefault();
        const el = e.target;

        let isConsonant = CHO.includes(char);
        let isVowel = JUN.includes(char);

        // Input Indices
        let inputCho = isConsonant ? getChoIdx(char) : -1;
        let inputJun = isVowel ? getJunIdx(char) : -1;
        let inputJon = isConsonant ? getJonIdx(char) : 0;

        // --- STATE MACHINE V4.0 ---

        // 0. Empty State
        if (state === 0) {
            if (isConsonant) {
                state = 1; idxCho = inputCho;
                commit(el, CHO[idxCho]);
            } else {
                // Vowel only (Start independently)
                commitAndReset(el, char);
            }
            return;
        }

        // 1. Cho State (e.g. 'ㄱ')
        if (state === 1) {
            if (isVowel) {
                // *** V4.0 FIX: Always Combine ***
                // Even if input is complex (e.g. ㅖ), combine with Cho
                state = 2; idxJun = inputJun;
                update(el, makeChar(idxCho, idxJun, 0));
            } else {
                // Consonant -> Reset and start new Cho (unless double consonant rule, but standard Dubeol doesn't auth-mix Cho)
                reset();
                state = 1; idxCho = inputCho;
                commit(el, CHO[idxCho]);
            }
            return;
        }

        // 2. Cho + Jun State (e.g. '가', '계')
        if (state === 2) {
            if (isVowel) {
                // Try Vowel Mixing (e.g. 고 + ㅏ -> 과)
                if (JUN_COMBOS[idxJun] && JUN_COMBOS[idxJun][inputJun]) {
                    idxJun = JUN_COMBOS[idxJun][inputJun];
                    update(el, makeChar(idxCho, idxJun, 0));
                } else {
                    // Cannot Mix -> Commit Prev, Start Vowel
                    reset();
                    commit(el, char);
                }
            } else {
                // Consonant -> Try Jongsung
                if (inputJon > 0) {
                    state = 3; idxJon = inputJon;
                    update(el, makeChar(idxCho, idxJun, idxJon));
                } else {
                    // Cannot be Jongsung -> Commit Prev, Start Cho
                    reset();
                    state = 1; idxCho = inputCho;
                    commit(el, CHO[idxCho]);
                }
            }
            return;
        }

        // 3. Cho + Jun + Jon State (e.g. '각')
        if (state === 3) {
            if (isVowel) {
                // *** Liaison Logic (Se-Gye) ***
                let prevJon = idxJon;
                let keptJon = 0;
                let nextCho = -1;

                if (REV_JON[prevJon]) {
                    // Complex Jon -> Split
                    keptJon = REV_JON[prevJon][0];
                    nextCho = getChoIdx(JON[REV_JON[prevJon][1]]);
                } else {
                    // Single Jon -> Move all
                    keptJon = 0;
                    nextCho = getChoIdx(JON[prevJon]);
                }

                // Update current char (remove moved jon)
                update(el, makeChar(idxCho, idxJun, keptJon));

                // Start next char (moved jon + input vowel)
                reset();
                state = 2; idxCho = nextCho; idxJun = inputJun;
                commit(el, makeChar(idxCho, idxJun, 0));
            } else {
                // Consonant -> Try Complex Jongsung
                if (JON_COMBOS[idxJon] && JON_COMBOS[idxJon][inputJon]) {
                    idxJon = JON_COMBOS[idxJon][inputJon];
                    update(el, makeChar(idxCho, idxJun, idxJon));
                } else {
                    reset();
                    state = 1; idxCho = inputCho;
                    commit(el, CHO[idxCho]);
                }
            }
            return;
        }

    }, true);

    // DOM Manipulation Helpers
    function processBackspace(e) {
        const el = e.target;
        if (state === 1) { // Cho -> Empty
            document.execCommand('delete');
            reset();
        } else if (state === 2) { // Cho+Jun -> Cho (or split complex vowel)
            // Simplifying: Remove vowel completely
            state = 1; idxJun = -1;
            update(el, CHO[idxCho]);
        } else if (state === 3) { // Cho+Jun+Jon -> Cho+Jun (or split complex jon)
            if (REV_JON[idxJon]) {
                idxJon = REV_JON[idxJon][0];
                update(el, makeChar(idxCho, idxJun, idxJon));
            } else {
                state = 2; idxJon = 0;
                update(el, makeChar(idxCho, idxJun, 0));
            }
        }
    }

    function commit(el, t) {
        if (el.isContentEditable) document.execCommand('insertText', false, t);
        else {
            const val = el.value, s = el.selectionStart, e = el.selectionEnd;
            el.value = val.substring(0, s) + t + val.substring(e);
            el.selectionStart = el.selectionEnd = s + t.length;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    function commitAndReset(el, t) { commit(el, t); reset(); }

    function update(el, t) {
        if (el.isContentEditable) {
            document.execCommand('delete');
            document.execCommand('insertText', false, t);
        } else {
            const val = el.value, s = el.selectionStart - 1;
            if (s >= 0) {
                el.value = val.substring(0, s) + t + val.substring(s + 1);
                el.selectionStart = el.selectionEnd = s + 1;
            }
        }
    }
})();
