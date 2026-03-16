const BACKEND_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
    checkServerStatus();
    loadStats();

    document.getElementById("refresh-btn").addEventListener("click", () => {
        checkServerStatus();
        loadStats();
    });

    document.getElementById("clear-btn").addEventListener("click", async () => {
        await chrome.storage.local.set({ stats: { total: 0, critical: 0, high: 0, medium: 0, low: 0 } });
        loadStats();
    });
});

async function checkServerStatus() {
    const dot = document.getElementById("status-dot");
    dot.className = "status-dot"; // reset
    try {
        const response = await fetch(`${BACKEND_URL}/health`);
        if (response.ok) {
            dot.classList.add("online");
        } else {
            dot.classList.add("offline");
        }
    } catch (e) {
        dot.classList.add("offline");
    }
}

async function loadStats() {
    chrome.storage.local.get(["stats"], (result) => {
        const stats = result.stats || { total: 0, critical: 0, high: 0, medium: 0, low: 0 };
        document.getElementById("total-checks").textContent = stats.total;
        document.getElementById("stat-critical").textContent = stats.critical || 0;
        document.getElementById("stat-high").textContent = stats.high || 0;
        document.getElementById("stat-medium").textContent = stats.medium || 0;
        document.getElementById("stat-low").textContent = stats.low || 0;
    });
}
