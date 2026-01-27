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

    // 5. Data Vacuum (Hooking Network calls to Qt WebChannel)
    if (typeof qt !== 'undefined') {
        new QWebChannel(qt.webChannelTransport, function (channel) {
            const recorder = channel.objects.primity_recorder;

            // Helper to blob to base64
            const blobToBase64 = blob => new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result.split(',')[1]);
                reader.onerror = reject;
                reader.readAsDataURL(blob);
            });

            // A. Hook fetch
            const originalFetch = window.fetch;
            window.fetch = async (...args) => {
                const response = await originalFetch(...args);
                const clone = response.clone();
                const url = response.url;

                try {
                    const blob = await clone.blob();
                    const b64 = await blobToBase64(blob);
                    recorder.record(url, b64);
                } catch (e) { console.error("[Vacuum] fetch error", e); }

                return response;
            };

            // B. Hook XHR
            const originalXHR = window.XMLHttpRequest;
            window.XMLHttpRequest = function () {
                const xhr = new originalXHR();
                const originalSend = xhr.send;
                xhr.send = function (...args) {
                    this.addEventListener('load', async () => {
                        const url = this.responseURL;
                        const blob = new Blob([this.response]);
                        const b64 = await blobToBase64(blob);
                        recorder.record(url, b64);
                    });
                    return originalSend.apply(this, args);
                };
                return xhr;
            };

            console.log("[Primity] Data Vacuum Active.");

            // 6. Interaction Observer (Action-driven POI)
            let lastActionTime = 0;
            const observer = new MutationObserver((mutations) => {
                const now = Date.now();
                if (now - lastActionTime > 3000) { // Throttling: 3s
                    lastActionTime = now;
                    console.log("[Primity] Major UI Change detected, marking snapshot...");
                    // No need to call 'record' here, but we can notify Manager if needed.
                }
            });
            observer.observe(document.body, { childList: true, subtree: true, attributes: true });
        });
    }

    console.log("[Primity] Archive Hooks Active. Time frozen at:", new Date().toISOString());
})();
