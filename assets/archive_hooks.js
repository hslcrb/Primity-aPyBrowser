/**
 * Primity Archive Hooks
 * =====================
 * This script is injected during the archiving process to ensure maximum fidelity.
 */

(function () {
    console.log("[Primity] Injecting Archive Hooks...");

    // 1. Unregister Service Workers to prevent caching interference
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(registrations => {
            for (let registration of registrations) {
                registration.unregister();
                console.log("[Primity] Unregistered Service Worker:", registration.scope);
            }
        });
    }

    // 2. Deterministic JS (Freeze Time)
    // We freeze the date to the moment of injection
    const originalDate = Date;
    const frozenTime = new Date().getTime();

    globalThis.Date = class extends originalDate {
        constructor(...args) {
            if (args.length === 0) {
                return new originalDate(frozenTime);
            }
            return new originalDate(...args);
        }
        static now() {
            return frozenTime;
        }
    };

    // 3. Deterministic Randomness
    globalThis.Math.random = function () {
        return 0.5; // Perfectly balanced, as all things should be.
    };

    // 4. REC Visibility (Breathing Red Border)
    const style = document.createElement('style');
    style.id = 'primity-rec-indicator';
    style.innerHTML = `
        @keyframes primity-breathing {
            0% { box-shadow: inset 0 0 15px rgba(211, 47, 47, 0.4); border-color: rgba(211, 47, 47, 0.3); }
            50% { box-shadow: inset 0 0 35px rgba(211, 47, 47, 0.9); border-color: rgba(211, 47, 47, 1); }
            100% { box-shadow: inset 0 0 15px rgba(211, 47, 47, 0.4); border-color: rgba(211, 47, 47, 0.3); }
        }
        :root {
            border: 5px solid rgba(211, 47, 47, 0.5) !important;
            animation: primity-breathing 2.5s infinite ease-in-out !important;
            transition: border 0.5s ease;
            box-sizing: border-box !important;
        }
    `;
    document.head.appendChild(style);

    console.log("[Primity] Archive Hooks Active. Time frozen at:", new Date().toISOString());
})();
