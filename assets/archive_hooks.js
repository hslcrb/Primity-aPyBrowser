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

    console.log("[Primity] Archive Hooks Active. Time frozen at:", new Date().toISOString());
})();
