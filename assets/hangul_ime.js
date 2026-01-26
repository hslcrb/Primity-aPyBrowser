/**
 * Primity Omni-Engine v5.1 (Emergency Fix)
 * Restores disconnected event listeners caused by v5.0 class encapsulation.
 * Ensures 'Han/Eng' key and toggle button work correctly.
 */

(function () {
    'use strict';

    // =================================================================================================
    // SECTION 1: CONSTANTS & TABLES (Unchanged from v5.0)
    // =================================================================================================
    const BASE_CODE = 0xAC00;
    const CHO_TABLE = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];
    const JUN_TABLE = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"];
    const JON_TABLE = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"];

    const MIX_VOWEL_MAP = {
        8: { 0: 9, 1: 10, 20: 11 },
        13: { 4: 14, 5: 15, 20: 16 },
        18: { 20: 19 }
    };

    const MIX_JONG_MAP = {
        1: { 19: 3 }, 4: { 22: 5, 27: 6 },
        8: { 1: 9, 16: 10, 17: 11, 19: 12, 25: 13, 26: 14, 27: 15 },
        17: { 19: 18 }
    };

    const REVERSE_JONG_MAP = {};
    for (let first in MIX_JONG_MAP) {
        for (let second in MIX_JONG_MAP[first]) {
            REVERSE_JONG_MAP[MIX_JONG_MAP[first][second]] = [parseInt(first), parseInt(second)];
        }
    }

    const LAYOUT_DUBEOL = {
        'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
        'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
        'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
        'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'O': 'ㅒ', 'P': 'ㅖ'
    };

    // =================================================================================================
    // SECTION 2: ENGINE CLASS
    // =================================================================================================

    class HangulAutomata {
        constructor() {
            this.state = 0;
            this.idxCho = -1;
            this.idxJun = -1;
            this.idxJon = 0;
            this.isActive = false;
            this.layout = LAYOUT_DUBEOL;
        }

        reset() {
            this.state = 0; this.idxCho = -1; this.idxJun = -1; this.idxJon = 0;
        }

        getChoIndex(char) { return CHO_TABLE.indexOf(char); }
        getJunIndex(char) { return JUN_TABLE.indexOf(char); }
        getJonIndex(char) { return JON_TABLE.indexOf(char); }
        makeSyllable(c, v, t) { return String.fromCharCode(BASE_CODE + (c * 588) + (v * 28) + t); }

        // --- PUBLIC API ---

        toggle(forceState) {
            if (forceState !== undefined) this.isActive = forceState;
            else this.isActive = !this.isActive;
            this.reset();
            return this.isActive;
        }

        handleKey(e) {
            // 1. Toggle Key
            if (e.code === 'AltRight' || e.key === 'HangulMode') {
                this.toggle();
                e.preventDefault();
                // Notify Python
                console.log("PRIMITY_IME_TOGGLED_VIA_KBD:" + this.isActive);
                return;
            }

            if (!this.isActive || e.ctrlKey || e.altKey || e.metaKey || e.key.length > 1 && e.key !== 'Backspace') return;

            const mappedChar = this.layout[e.key];

            if (e.key === 'Backspace') {
                if (this.state !== 0) {
                    this.processBackspace(e.target);
                    e.preventDefault();
                }
                return;
            }

            if (!mappedChar) {
                if (this.state !== 0) this.reset();
                return;
            }

            e.preventDefault();
            this.processInput(e.target, mappedChar);
        }

        processInput(target, char) {
            const isConsonant = CHO_TABLE.includes(char);
            const isVowel = JUN_TABLE.includes(char);

            const inCho = isConsonant ? this.getChoIndex(char) : -1;
            const inJun = isVowel ? this.getJunIndex(char) : -1;
            const inJon = isConsonant ? this.getJonIndex(char) : 0;

            // State 0: Empty
            if (this.state === 0) {
                if (isConsonant) {
                    this.state = 1; this.idxCho = inCho;
                    this.commit(target, CHO_TABLE[this.idxCho]);
                } else {
                    this.commit(target, char); this.reset();
                }
                return;
            }

            // State 1: Cho
            if (this.state === 1) {
                if (isVowel) {
                    this.state = 2; this.idxJun = inJun;
                    this.update(target, this.makeSyllable(this.idxCho, this.idxJun, 0));
                } else {
                    this.reset(); this.state = 1; this.idxCho = inCho;
                    this.commit(target, CHO_TABLE[this.idxCho]);
                }
                return;
            }

            // State 2: Cho + Jun
            if (this.state === 2) {
                if (isVowel) {
                    if (MIX_VOWEL_MAP[this.idxJun] && MIX_VOWEL_MAP[this.idxJun][inJun]) {
                        this.idxJun = MIX_VOWEL_MAP[this.idxJun][inJun];
                        this.update(target, this.makeSyllable(this.idxCho, this.idxJun, 0));
                    } else {
                        this.reset(); this.commit(target, char);
                    }
                } else {
                    if (inJon > 0) {
                        this.state = 3; this.idxJon = inJon;
                        this.update(target, this.makeSyllable(this.idxCho, this.idxJun, this.idxJon));
                    } else {
                        this.reset(); this.state = 1; this.idxCho = inCho;
                        this.commit(target, CHO_TABLE[this.idxCho]);
                    }
                }
                return;
            }

            // State 3: Cho + Jun + Jon
            if (this.state === 3) {
                if (isVowel) {
                    let prevJon = this.idxJon;
                    let leftJon = 0;
                    let movedCho = -1;

                    if (REVERSE_JONG_MAP[prevJon]) {
                        leftJon = REVERSE_JONG_MAP[prevJon][0];
                        movedCho = this.getChoIndex(JON_TABLE[REVERSE_JONG_MAP[prevJon][1]]);
                    } else {
                        leftJon = 0;
                        movedCho = this.getChoIndex(JON_TABLE[prevJon]);
                    }

                    this.update(target, this.makeSyllable(this.idxCho, this.idxJun, leftJon));
                    this.reset();
                    this.state = 2; this.idxCho = movedCho; this.idxJun = inJun;
                    this.commit(target, this.makeSyllable(this.idxCho, this.idxJun, 0));
                } else {
                    if (MIX_JONG_MAP[this.idxJon] && MIX_JONG_MAP[this.idxJon][inJon]) {
                        this.idxJon = MIX_JONG_MAP[this.idxJon][inJon];
                        this.update(target, this.makeSyllable(this.idxCho, this.idxJun, this.idxJon));
                    } else {
                        this.reset(); this.state = 1; this.idxCho = inCho;
                        this.commit(target, CHO_TABLE[this.idxCho]);
                    }
                }
                return;
            }
        }

        processBackspace(target) {
            if (this.state === 1) {
                document.execCommand('delete'); this.reset();
            } else if (this.state === 2) {
                this.state = 1; this.idxJun = -1;
                this.update(target, CHO_TABLE[this.idxCho]);
            } else if (this.state === 3) {
                if (REVERSE_JONG_MAP[this.idxJon]) {
                    this.idxJon = REVERSE_JONG_MAP[this.idxJon][0];
                    this.update(target, this.makeSyllable(this.idxCho, this.idxJun, this.idxJon));
                } else {
                    this.state = 2; this.idxJon = 0;
                    this.update(target, this.makeSyllable(this.idxCho, this.idxJun, 0));
                }
            }
        }

        commit(el, t) {
            if (el.isContentEditable) document.execCommand('insertText', false, t);
            else {
                const s = el.selectionStart, e = el.selectionEnd, v = el.value;
                el.value = v.slice(0, s) + t + v.slice(e);
                el.selectionStart = el.selectionEnd = s + t.length;
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }

        update(el, t) {
            if (el.isContentEditable) {
                document.execCommand('delete'); document.execCommand('insertText', false, t);
            } else {
                const s = el.selectionStart - 1, v = el.value;
                if (s >= 0) {
                    el.value = v.slice(0, s) + t + v.slice(s + 1);
                    el.selectionStart = el.selectionEnd = s + 1;
                }
            }
        }
    }

    // =================================================================================================
    // SECTION 3: WIRING
    // =================================================================================================

    // Create Instance
    const engine = new HangulAutomata();

    // Listen to Python Control Events
    window.addEventListener('PRIMITY_TOGGLE_IME', (e) => {
        // e.detail.active is boolean
        engine.toggle(e.detail.active);
    });

    // Listen to Keyboard (Capture Phase to intercept)
    document.addEventListener('keydown', (e) => {
        engine.handleKey(e);
    }, true);

    console.log("Primity Omni-Engine v5.1 Wired & Ready.");

})();
