/**
 * Primity Network Replay Mock
 * ===========================
 * This script is injected when viewing an archived page.
 * It intercepts fetch/XHR and serves data from local network_logs.json.
 */

(function () {
    console.log("[Primity] Initializing Network Replay Mock...");

    const logPath = window.location.href.substring(0, window.location.href.lastIndexOf('/')) + '/network_logs.json';
    let networkLogs = [];

    // Load saved logs
    fetch(logPath)
        .then(response => response.json())
        .then(data => {
            networkLogs = data;
            console.log("[Primity] Loaded", networkLogs.length, "network logs for replay.");
            setupMocks();
        })
        .catch(err => console.warn("[Primity] No network logs found for replay."));

    function setupMocks() {
        // 1. Mock window.fetch
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const url = args[0] instanceof Request ? args[0].url : args[0];
            const matchingLog = networkLogs.find(log => log.url === url);

            if (matchingLog && matchingLog.payload) {
                console.log("[Primity Replay] 🚀 Mocking fetch (with data):", url);
                const binary = atob(matchingLog.payload);
                const bytes = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);

                return new Response(bytes, {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                });
            }
            return originalFetch(...args);
        };

        // 2. Mock XMLHttpRequest
        const originalXHR = window.XMLHttpRequest;
        window.XMLHttpRequest = function () {
            const xhr = new originalXHR();
            const originalOpen = xhr.open;
            xhr.open = function (method, url, ...rest) {
                this._url = url;
                return originalOpen.apply(this, [method, url, ...rest]);
            };

            const originalSend = xhr.send;
            xhr.send = function (body) {
                const matchingLog = networkLogs.find(log => log.url === this._url);
                if (matchingLog && matchingLog.payload) {
                    console.log("[Primity Replay] 🚀 Mocking XHR (with data):", this._url);
                    const binary = atob(matchingLog.payload);
                    Object.defineProperty(this, 'status', { value: 200 });
                    Object.defineProperty(this, 'responseText', { value: binary });
                    Object.defineProperty(this, 'response', { value: binary });
                    this.dispatchEvent(new Event('load'));
                    return;
                }
                return originalSend.apply(this, [body]);
            };
            return xhr;
        };
    }
})();
