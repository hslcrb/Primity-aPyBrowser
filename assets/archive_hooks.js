/**
 * Primity Archive Hooks (Final Masterpiece)
 * ========================================
 * Injected during REC mode to capture data and show visual indicators.
 * Bypasses Trusted Types and CSP for maximum fidelity.
 */

(function () {
    console.log("[Primity] Initializing Archive Hooks...");

    // 1. Unregister Service Workers
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.getRegistrations().then(registrations => {
            for (let registration of registrations) {
                registration.unregister();
            }
        });
    }

    // 2. Freeze Time & Randomness
    const frozenTime = new Date().getTime();
    const originalDate = Date;
    globalThis.Date = class extends originalDate {
        constructor(...args) {
            if (args.length === 0) return new originalDate(frozenTime);
            return new originalDate(...args);
        }
        static now() { return frozenTime; }
    };
    globalThis.Math.random = () => 0.5;

    // 3. REC UI (Breathing Border) - Trusted Types safe
    const setupUI = () => {
        if (document.getElementById('primity-rec-indicator')) return;
        const style = document.createElement('style');
        style.id = 'primity-rec-indicator';
        style.textContent = `
            @keyframes primity-breathing {
                0% { box-shadow: inset 0 0 15px rgba(211, 47, 47, 0.4); border-color: rgba(211, 47, 47, 0.3); }
                50% { box-shadow: inset 0 0 35px rgba(211, 47, 47, 0.9); border-color: rgba(211, 47, 47, 1); }
                100% { box-shadow: inset 0 0 15px rgba(211, 47, 47, 0.4); border-color: rgba(211, 47, 47, 0.3); }
            }
            :root {
                border: 5px solid rgba(211, 47, 47, 0.5) !important;
                animation: primity-breathing 2.5s infinite ease-in-out !important;
                box-sizing: border-box !important;
                min-height: 100vh !important;
            }
        `;
        document.head.appendChild(style);
    };
    if (document.head) setupUI();
    else document.addEventListener('DOMContentLoaded', setupUI);

    // 4. Data Vacuum (Qt WebChannel)
    function initVacuum() {
        if (typeof qt !== 'undefined' && typeof QWebChannel !== 'undefined') {
            new QWebChannel(qt.webChannelTransport, function (channel) {
                const recorder = channel.objects.primity_recorder;

                const blobToBase64 = blob => new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result.split(',')[1]);
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                });

                // Hook fetch
                const originalFetch = window.fetch;
                window.fetch = async (...args) => {
                    const response = await originalFetch(...args);
                    const clone = response.clone();
                    try {
                        const blob = await clone.blob();
                        const b64 = await blobToBase64(blob);
                        recorder.record(response.url, b64);
                    } catch (e) { }
                    return response;
                };

                // Hook XHR
                const originalXHR = window.XMLHttpRequest;
                window.XMLHttpRequest = function () {
                    const xhr = new originalXHR();
                    const originalSend = xhr.send;
                    xhr.send = function (...args) {
                        this.addEventListener('load', async () => {
                            try {
                                const blob = new Blob([this.response]);
                                const b64 = await blobToBase64(blob);
                                recorder.record(this.responseURL, b64);
                            } catch (e) { }
                        });
                        return originalSend.apply(this, args);
                    };
                    return xhr;
                };
                console.log("%c[Primity] Data Vacuum Active!", "color: #d32f2f; font-weight: bold;");
            });
        } else if (typeof qt !== 'undefined') {
            setTimeout(initVacuum, 300);
        }
    }
    initVacuum();

    console.log("[Primity] Archive Hooks active at:", new Date().toISOString());
})();
