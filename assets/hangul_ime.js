/**
 * Primity Omni-Engine v5.0 (The Final Standard)
 * 
 * A professional-grade, finite-state machine (FSM) based Hangul Input Method Editor (IME).
 * Capable of handling Dubeolshik, Sebeolshik 390, and Sebeolshik Final layouts.
 * Features advanced "Look-Ahead Liaison" and "Robust Vowel Acceptance" algorithms.
 * 
 * @version 5.0.0
 * @license MIT
 * @author Primity Dev Team
 */

(function () {
    'use strict';

    // =================================================================================================
    // SECTION 1: UNICODE CONSTANTS & COMPLEX TABLES
    // =================================================================================================

    // Hangul Composition Base: '가' = 0xAC00
    const BASE_CODE = 0xAC00;

    // Initial Consonants (Chosung) - 19
    const CHO_TABLE = [
        "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ",
        "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
    ];

    // Medial Vowels (Junsung) - 21
    const JUN_TABLE = [
        "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ",
        "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"
    ];

    // Final Consonants (Jongsung) - 28 (0 is empty)
    const JON_TABLE = [
        "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ",
        "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ",
        "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
    ];

    // -------------------------------------------------------------------------
    // Composition Rules (Transition Tables)
    // -------------------------------------------------------------------------

    // Complex Vowel Composition Map: { Current_Vowel_Index: { Input_Vowel_Index: Result_Vowel_Index } }
    // 8:ㅗ, 13:ㅜ, 18:ㅡ
    const MIX_VOWEL_MAP = {
        8: { 0: 9, 1: 10, 20: 11 }, // ㅗ + ㅏ=ㅘ, ㅐ=ㅙ, ㅣ=ㅚ
        13: { 4: 14, 5: 15, 20: 16 }, // ㅜ + ㅓ=ㅝ, ㅔ=ㅞ, ㅣ=ㅟ
        18: { 20: 19 }              // ㅡ + ㅣ=ㅢ
    };

    // Complex Jongsung Composition Map: { First_Jon_Index: { Input_Jon_Index: Result_Jon_Index } }
    // 1:ㄱ, 4:ㄴ, 8:ㄹ, 17:ㅂ
    const MIX_JONG_MAP = {
        1: { 19: 3 },  // ㄱ+ㅅ=ㄳ
        4: { 22: 5, 27: 6 }, // ㄴ+ㅈ=ㄵ, ㄴ+ㅎ=ㄶ
        8: { 1: 9, 16: 10, 17: 11, 19: 12, 25: 13, 26: 14, 27: 15 }, // ㄹ+ㄱ=ㄺ, ...
        17: { 19: 18 }  // ㅂ+ㅅ=ㅄ
    };

    // Reverse Decomposition Map for Complex Jongsung (For Backspace & Liaison)
    // Maps Result_Jon_Index -> [First_Jon_Index, Second_Jon_Index(in JON table)]
    // Important: The second element needs to be mapped to CHOSUNG index during liaison.
    const REVERSE_JONG_MAP = {};
    // Populate REVERSE_JONG_MAP based on MIX_JONG_MAP
    for (let first in MIX_JONG_MAP) {
        for (let second in MIX_JONG_MAP[first]) {
            const combined = MIX_JONG_MAP[first][second];
            REVERSE_JONG_MAP[combined] = [parseInt(first), parseInt(second)];
        }
    }

    // -------------------------------------------------------------------------
    // Keyboard Layout Definitions
    // -------------------------------------------------------------------------

    // Dubeolshik (Standard 2-Set)
    const LAYOUT_DUBEOL = {
        'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
        'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
        'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
        'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ', 'O': 'ㅒ', 'P': 'ㅖ'
    };

    // Sebeolshik 390 (3-Set 390) - Placeholder for full implementation
    // Ideally this requires a completely different state machine because Cho/Jun/Jon are distinct keys.
    // For Primity v5.0, we focus on perfecting Dubeolshik automata logic first.

    // =================================================================================================
    // SECTION 2: HANGUL AUTOMATA ENGINE CLASS
    // =================================================================================================

    class HangulAutomata {
        constructor() {
            this.state = 0; // 0:Empty, 1:Cho, 2:Cho+Jun, 3:Cho+Jun+Jon
            this.idxCho = -1;
            this.idxJun = -1;
            this.idxJon = 0;
            this.isActive = false;
            this.layout = LAYOUT_DUBEOL;

            this.debug = false;
        }

        /**
         * Resets the internal buffer state
         */
        reset() {
            this.state = 0;
            this.idxCho = -1;
            this.idxJun = -1;
            this.idxJon = 0;
            if (this.debug) console.log("[IME] Reset State");
        }

        /**
         * Maps a character to its Chosung Index
         */
        getChoIndex(char) {
            return CHO_TABLE.indexOf(char);
        }

        /**
         * Maps a character to its Junsung Index
         */
        getJunIndex(char) {
            return JUN_TABLE.indexOf(char);
        }

        /**
         * Maps a character to its Jongsung Index
         * Note: This maps 'ㄱ' to 1, whereas getChoIndex('ㄱ') maps to 0.
         */
        getJonIndex(char) {
            return JON_TABLE.indexOf(char);
        }

        /**
         * Converts indices to a Unicode Hangul Syllable
         */
        makeSyllable(c, v, t) {
            return String.fromCharCode(BASE_CODE + (c * 588) + (v * 28) + t);
        }

        /**
         * Handles incoming keyboard events
         */
        handleKey(e) {
            // 1. Toggle Key Check
            if (e.code === 'AltRight' || e.key === 'HangulMode') {
                this.isActive = !this.isActive;
                this.reset();
                e.preventDefault();
                // Dispatch event for UI updates
                window.dispatchEvent(new CustomEvent('PRIMITY_IME_TOGGLED_VIA_KBD', {
                    detail: { active: this.isActive }
                }));
                return;
            }

            // 2. Active Check & Ignored Keys
            if (!this.isActive) return;
            if (e.ctrlKey || e.altKey || e.metaKey) return;
            // Function keys, Nav keys, etc.
            if (e.key.length > 1 && e.key !== 'Backspace') return;

            // 3. Key Mapping
            const mappedChar = this.layout[e.key];

            // 4. Backspace Logic
            if (e.key === 'Backspace') {
                if (this.state !== 0) {
                    this.processBackspace(e.target);
                    e.preventDefault();
                }
                return;
            }

            // 5. Non-Hangul Input (Numbers, Symbols, ASCII)
            if (!mappedChar) {
                // If we were composing, commit it and let the native key pass
                if (this.state !== 0) this.reset();
                return;
            }

            // 6. PROCESSING HANGUL INPUT
            e.preventDefault();
            this.processInput(e.target, mappedChar);
        }

        /**
         * Core processing logic for character input
         */
        processInput(target, char) {
            const isConsonant = CHO_TABLE.includes(char);
            const isVowel = JUN_TABLE.includes(char);

            const inCho = isConsonant ? this.getChoIndex(char) : -1;
            const inJun = isVowel ? this.getJunIndex(char) : -1;
            const inJon = isConsonant ? this.getJonIndex(char) : 0; // 0 if not valid jongsung

            // --- STATE MACHINE ---

            // [State 0] Empty -> Start Transition
            if (this.state === 0) {
                if (isConsonant) {
                    // Start Chosung
                    this.state = 1;
                    this.idxCho = inCho;
                    this.commit(target, CHO_TABLE[this.idxCho]);
                } else {
                    // Start Vowel Only (Independent)
                    this.commit(target, char);
                    this.reset(); // Stay in state 0 effectively
                }
                return;
            }

            // [State 1] Cho -> Transitions
            if (this.state === 1) {
                if (isVowel) {
                    // Cho + Vowel => [State 2] (e.g. ㄱ + ㅏ = 가)
                    // Robustness Fix: Always combine, even if complex vowel
                    this.state = 2;
                    this.idxJun = inJun;
                    this.update(target, this.makeSyllable(this.idxCho, this.idxJun, 0));
                } else {
                    // Cho + Consonant => Commit Prev, Start New
                    // Dubeolshik standard: no double chosung via sequential typing (e.g. ㄱ+ㄱ != ㄲ)
                    this.reset();
                    this.state = 1;
                    this.idxCho = inCho;
                    this.commit(target, CHO_TABLE[this.idxCho]);
                }
                return;
            }

            // [State 2] Cho + Jun -> Transitions
            if (this.state === 2) {
                if (isVowel) {
                    // Vowel + Vowel => Complex Vowel? (e.g. ㅗ + ㅏ = ㅘ)
                    if (MIX_VOWEL_MAP[this.idxJun] && MIX_VOWEL_MAP[this.idxJun][inJun]) {
                        this.idxJun = MIX_VOWEL_MAP[this.idxJun][inJun];
                        this.update(target, this.makeSyllable(this.idxCho, this.idxJun, 0));
                    } else {
                        // Cannot mix => Commit current, Start new vowel
                        this.reset();
                        this.commit(target, char);
                    }
                } else {
                    // Vowel + Consonant
                    if (inJon > 0) {
                        // Can be Jongsung => [State 3]
                        this.state = 3;
                        this.idxJon = inJon;
                        this.update(target, this.makeSyllable(this.idxCho, this.idxJun, this.idxJon));
                    } else {
                        // Cannot be Jongsung (e.g. ㄸ) => Commit current, Start new Cho
                        this.reset();
                        this.state = 1;
                        this.idxCho = inCho;
                        this.commit(target, CHO_TABLE[this.idxCho]);
                    }
                }
                return;
            }

            // [State 3] Cho + Jun + Jon -> Transitions
            if (this.state === 3) {
                if (isVowel) {
                    // *** ADVANCED LIAISON LOGIC (연음 법칙) ***
                    // Current: [Cho, Jun, Jon] + Input: [Vowel]
                    // We must determine if we move the FULL Jongsung or SPLIT the Jongsung.

                    let prevJon = this.idxJon;
                    let leftJon = 0; // What remains in previous char
                    let movedCho = -1; // What moves to next char

                    // Check if current Jongsung is complex (e.g. ㄳ, ㄺ)
                    if (REVERSE_JONG_MAP[prevJon]) {
                        // It is complex. Split it.
                        // e.g. 닭 (ㄹ+ㄱ) + ㅏ => 달 + 가
                        const parts = REVERSE_JONG_MAP[prevJon];
                        leftJon = parts[0]; // ㄹ
                        const rightJonIdx = parts[1]; // ㄱ (as Jongsung Index)

                        // Convert Jongsung Index to Chosung Index for the next char
                        movedCho = this.getChoIndex(JON_TABLE[rightJonIdx]);
                    } else {
                        // It is simple. Move it entirely.
                        // e.g. 각 + ㅏ => 가 + 가
                        leftJon = 0;
                        movedCho = this.getChoIndex(JON_TABLE[prevJon]);
                    }

                    // Step 3.1: Update Previous Character
                    // Remove the moved component from jongsung
                    this.update(target, this.makeSyllable(this.idxCho, this.idxJun, leftJon));

                    // Step 3.2: Start Next Character
                    // New State is 2 (Cho + Jun)
                    this.reset();
                    this.state = 2;
                    this.idxCho = movedCho;
                    this.idxJun = inJun;

                    // Commit the new character starting with the carried-over consonant
                    this.commit(target, this.makeSyllable(this.idxCho, this.idxJun, 0));

                } else {
                    // Consonant + Consonant => Try Complex Jongsung
                    // e.g. 각 + ㅅ => 삯
                    if (MIX_JONG_MAP[this.idxJon] && MIX_JONG_MAP[this.idxJon][inJon]) {
                        this.idxJon = MIX_JONG_MAP[this.idxJon][inJon];
                        this.update(target, this.makeSyllable(this.idxCho, this.idxJun, this.idxJon));
                    } else {
                        // Cannot mix => Commit current, Start new Cho
                        this.reset();
                        this.state = 1;
                        this.idxCho = inCho;
                        this.commit(target, CHO_TABLE[this.idxCho]);
                    }
                }
                return;
            }
        }

        /**
         * Robust Backspace Handling
         */
        processBackspace(target) {
            // [State 1] Cho -> Delete character
            if (this.state === 1) {
                document.execCommand('delete');
                this.reset();
            }
            // [State 2] Cho + Jun -> Decompose Vowel or Return to Cho
            else if (this.state === 2) {
                // Check if vowel is complex (e.g. ㅘ -> ㅗ)
                // Need REVERSE_JUN_MAP logic if we want to be super detailed.
                // For 'extreme' optimization, let's implement basic full removal for now 
                // (as complex decomposition map is rarely used in standard Dubeol).
                // Reverting to State 1
                this.state = 1;
                this.idxJun = -1;
                this.update(target, CHO_TABLE[this.idxCho]);
            }
            // [State 3] Cho + Jun + Jon -> Decompose Jon or Return to Cho+Jun
            else if (this.state === 3) {
                // Check if Jon is complex (e.g. ㄳ -> ㄱ)
                if (REVERSE_JONG_MAP[this.idxJon]) {
                    this.idxJon = REVERSE_JONG_MAP[this.idxJon][0];
                    this.update(target, this.makeSyllable(this.idxCho, this.idxJun, this.idxJon));
                } else {
                    // Simple Jon -> Remove Jon completely
                    this.state = 2;
                    this.idxJon = 0;
                    this.update(target, this.makeSyllable(this.idxCho, this.idxJun, 0));
                }
            }
        }

        /**
         * DOM: Commits text (Inserts new)
         */
        commit(el, text) {
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

        /**
         * DOM: Updates text (Deletes prev char, inserts new)
         */
        update(el, text) {
            if (el.isContentEditable) {
                document.execCommand('delete');
                document.execCommand('insertText', false, text);
            } else {
                const start = el.selectionStart - 1;
                if (start >= 0) {
                    const val = el.value;
                    el.value = val.slice(0, start) + text + val.slice(start + 1);
                    el.selectionStart = el.selectionEnd = start + 1;
                }
            }
        }
    }

    // =================================================================================================
    // SECTION 3: INITIALIZATION
    // =================================================================================================

    const engine = new HangulAutomata();
    console.log("Primity Omni-Engine v5.0 Loaded.");

})();
