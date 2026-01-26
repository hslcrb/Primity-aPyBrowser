/**
 * Primity Ultimate Hangul Engine v3.0 (State-Machine Based)
 * Completely rewritten to solve '세계' (Se-Gye) and other complex liaison cases.
 * Implements standard Korean IME state transitions.
 */
(function () {
    // ----------------------------------------------------------------------
    // Constants & Tables
    // ----------------------------------------------------------------------
    const BASE = 0xAC00;
    const CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];
    const JUN = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"];
    const JON = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];

    // Combinations
    const MIX_JUN = {
        '9': [['0', '0'], 9], '10': [['0', '1'], 10], '11': [['0', '20'], 11], // ㅗ+...
        '14': [['13', '4'], 14], '15': [['13', '5'], 15], '16': [['13', '20'], 16], // ㅜ+...
        '19': [['18', '20'], 19] // ㅡ+ㅣ
    };
    // To check if two vowels can mix: map[first_idx][second_idx] = result_idx
    const JUN_COMBOS = {};
    JUN_COMBOS[8] = { 0: 9, 1: 10, 20: 11 }; // ㅗ + ㅏ,ㅐ,ㅣ
    JUN_COMBOS[13] = { 4: 14, 5: 15, 20: 16 }; // ㅜ + ㅓ,ㅔ,ㅣ
    JUN_COMBOS[18] = { 20: 19 }; // ㅡ + ㅣ

    // Complex Jongsung map: map[first_jon][second_jon] = result_jon
    // ㄱ(1), ㄴ(4), ㄹ(8), ㅂ(17)
    const JON_COMBOS = {};
    JON_COMBOS[1] = { 19: 3 }; // ㄱ+ㅅ=ㄳ
    JON_COMBOS[4] = { 22: 5, 27: 6 }; // ㄴ+ㅈ=ㄵ, ㄴ+ㅎ=ㄶ
    JON_COMBOS[8] = { 1: 9, 16: 10, 17: 11, 19: 12, 25: 13, 26: 14, 27: 15 }; // ㄹ+...
    JON_COMBOS[17] = { 19: 18 }; // ㅂ+ㅅ=ㅄ

    // Reverse map for decomposing complex Jongsung (JON index -> [first, second] JON indices)
    const REV_JON = {};
    REV_JON[3] = [1, 19]; REV_JON[5] = [4, 22]; REV_JON[6] = [4, 27];
    REV_JON[9] = [8, 1]; REV_JON[10] = [8, 16]; REV_JON[11] = [8, 17];
    REV_JON[12] = [8, 19]; REV_JON[13] = [8, 25]; REV_JON[14] = [8, 26];
    REV_JON[15] = [8, 27]; REV_JON[18] = [17, 19];

    // Keyboard Maps (Dubeolshik Standard)
    const KEYMAP = {
        'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
        'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
        'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
        'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'O': 'ㅒ', 'P': 'ㅖ'
    };

    // ----------------------------------------------------------------------
    // Hangul Engine State
    // ----------------------------------------------------------------------
    let composed = ""; // Currently composing text block characters (e.g. "세") before final logic
    let state = 0; // 0:Empty, 1:Cho, 2:Cho+Jun, 3:Cho+Jun+Jon

    // Indices for current composition
    let idxCho = -1;
    let idxJun = -1;
    let idxJon = 0; // 0 means empty

    let hangulActive = false;

    // Helper: Map Jamo Char to Index
    function getChoIdx(c) { return CHO.indexOf(c); }
    function getJunIdx(c) { return JUN.indexOf(c); }
    function getJonIdx(c) { return JON.indexOf(c); } // returns 0 if "" matches, >0 if real jongsung

    // Helper: Build Hangul Syllable
    function makeChar(c, v, t) {
        return String.fromCharCode(BASE + (c * 588) + (v * 28) + t);
    }

    // Reset Engine
    function reset() {
        state = 0; idxCho = -1; idxJun = -1; idxJon = 0;
    }

    // Main event listener
    window.addEventListener('PRIMITY_TOGGLE_IME', (e) => {
        hangulActive = e.detail.active;
        reset();
    });

    document.addEventListener('keydown', function (e) {
        // Toggle Logic
        if (e.code === 'AltRight' || e.key === 'HangulMode') {
            hangulActive = !hangulActive;
            reset();
            e.preventDefault();
            return;
        }

        if (!hangulActive || e.ctrlKey || e.altKey || e.metaKey || e.code.startsWith('F')) return;

        // 1. Get mapped jamo
        const char = KEYMAP[e.key];
        if (!char) {
            if (e.key === 'Backspace') {
                if (state !== 0) {
                    processBackspace(e);
                    e.preventDefault();
                } else {
                    // Let native backspace happen
                }
            } else {
                // Non-mapped key (numbers, space, enter etc) -> Commit current composition
                reset();
            }
            return;
        }

        // 2. Process Input
        e.preventDefault();
        const el = e.target;

        let isConsonant = CHO.includes(char);
        let isVowel = JUN.includes(char); // Note: KEYMAP values like 'ㅖ' are in JUN

        // Identify Indices
        let inputCho = isConsonant ? getChoIdx(char) : -1;
        let inputJun = isVowel ? getJunIdx(char) : -1;
        let inputJon = isConsonant ? getJonIdx(char) : 0; // Might be valid Jongsung

        // ==================================================================
        // STATE MACHINE TRANSITIONS
        // ==================================================================

        // CASE 0: Empty -> Start new syll or just inert vowel
        if (state === 0) {
            if (isConsonant) {
                state = 1; idxCho = inputCho;
                commit(el, CHO[idxCho]);
            } else {
                // Vowel only: commit as-is (e.g. 'ㅏ')
                commitAndReset(el, char);
            }
            return;
        }

        // CASE 1: Cho (e.g. 'ㄱ')
        if (state === 1) {
            if (isVowel) {
                // Cho + Jun -> "가"
                state = 2; idxJun = inputJun;
                update(el, makeChar(idxCho, idxJun, 0));
            } else {
                // Cho + Cho -> Commit prev, start new
                // If it's a valid complex Cho (not supported in standard automata usually except manual shift), usually just next char
                // e.g. ㄱ + ㅅ -> ㄱㅅ
                reset();
                state = 1; idxCho = inputCho;
                commit(el, CHO[idxCho]);
            }
            return;
        }

        // CASE 2: Cho + Jun (e.g. '가')
        if (state === 2) {
            if (isVowel) {
                // Check complex vowel (e.g. 고 + ㅏ -> 과)
                if (JUN_COMBOS[idxJun] && JUN_COMBOS[idxJun][inputJun]) {
                    idxJun = JUN_COMBOS[idxJun][inputJun];
                    update(el, makeChar(idxCho, idxJun, 0));
                } else {
                    // Cannot mix -> Commit "고", Start "ㅏ"
                    reset();
                    commit(el, char);
                }
            } else {
                // Consonant -> Can it be Jongsung?
                if (inputJon > 0) {
                    state = 3; idxJon = inputJon;
                    update(el, makeChar(idxCho, idxJun, idxJon));
                } else {
                    // Cannot be Jongsung (e.g. ㄸ) -> Commit "가", Start "ㄸ"
                    reset();
                    state = 1; idxCho = inputCho;
                    commit(el, CHO[idxCho]);
                }
            }
            return;
        }

        // CASE 3: Cho + Jun + Jon (e.g. '각')
        if (state === 3) {
            if (isVowel) {
                // *** CRITICAL LIAISON LOGIC FOR '세계' ***
                // Input is Vowel (ㅖ). Current is '각' (Jon=ㄱ).
                // Logic: Detach 'ㄱ', make it Cho for next Char.

                // 1. Decompose current Jon
                let prevJon = idxJon;
                let keptJon = 0;
                let nextCho = -1;

                if (REV_JON[prevJon]) {
                    // Complex Jon (e.g. ㄳ) -> Keep ㄱ(1), Next is ㅅ(19 can be 9 in CHO idx?)
                    // Need mapping Jon index to Cho index
                    let parts = REV_JON[prevJon];
                    keptJon = parts[0]; // Remain attached
                    // Mapping JON 'ㅅ'(19) to CHO 'ㅅ'(9)
                    nextCho = getChoIdx(JON[parts[1]]);
                } else {
                    // Single Jon (e.g. ㄱ) -> detach completely
                    keptJon = 0;
                    nextCho = getChoIdx(JON[prevJon]);
                }

                // 2. Commit modified Char 1
                update(el, makeChar(idxCho, idxJun, keptJon));

                // 3. Start Char 2 with nextCho + inputJun
                reset();
                state = 2;
                idxCho = nextCho;
                idxJun = inputJun;
                commit(el, makeChar(idxCho, idxJun, 0));
            } else {
                // Consonant -> Check complex Jongsung (e.g. 각 + ㅅ -> 삯)
                if (JON_COMBOS[idxJon] && JON_COMBOS[idxJon][inputJon]) {
                    idxJon = JON_COMBOS[idxJon][inputJon];
                    update(el, makeChar(idxCho, idxJun, idxJon));
                } else {
                    // No mix -> Commit '각', Start new Cho
                    reset();
                    state = 1; idxCho = inputCho;
                    commit(el, CHO[idxCho]);
                }
            }
            return;
        }

    }, true);

    // ----------------------------------------------------------------------
    // DOM Helpers
    // ----------------------------------------------------------------------
    function processBackspace(e) {
        const el = e.target;
        if (state === 1) { // ㄱ -> empty
            document.execCommand('delete');
            reset();
        } else if (state === 2) { // 가 -> ㄱ (remove vowel)
            // If complex vowel? (과 -> 고) - skipping for simplicity, usually remove whole vowel
            state = 1; idxJun = -1;
            update(el, CHO[idxCho]);
        } else if (state === 3) { // 각 -> 가 (remove jon)
            // check complex jon
            if (REV_JON[idxJon]) {
                idxJon = REV_JON[idxJon][0];
                update(el, makeChar(idxCho, idxJun, idxJon));
            } else {
                state = 2; idxJon = 0;
                update(el, makeChar(idxCho, idxJun, 0));
            }
        }
    }

    // Insert new text at cursor
    function commit(el, t) {
        if (el.isContentEditable) {
            document.execCommand('insertText', false, t);
        } else {
            const val = el.value;
            const start = el.selectionStart;
            const end = el.selectionEnd;
            el.value = val.substring(0, start) + t + val.substring(end);
            el.selectionStart = el.selectionEnd = start + t.length;
            el.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    // Commit and then hard reset
    function commitAndReset(el, t) {
        commit(el, t);
        reset();
    }

    // Replace previous character with Updated one
    function update(el, t) {
        if (el.isContentEditable) {
            document.execCommand('delete'); // delete prev char
            document.execCommand('insertText', false, t);
        } else {
            const val = el.value;
            const start = el.selectionStart - 1; // assuming 1 char composed
            if (start >= 0) {
                el.value = val.substring(0, start) + t + val.substring(start + 1);
                el.selectionStart = el.selectionEnd = start + 1;
            }
        }
    }

})();
