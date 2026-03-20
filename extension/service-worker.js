/**
 * service-worker.js
 * Responsibilities:
 *   - Maintain session stats for the dashboard
 *   - Handle messages from content script
 *   - No AI logic here — purely administrative
 */

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "VERDICT_LOGGED") {
    logVerdict(msg.verdict);
  }
});

async function logVerdict(verdict) {
  const data = await chrome.storage.local.get(["stats"]);
  const stats = data.stats || { total: 0, critical: 0, high: 0, medium: 0, low: 0 };
  stats.total++;
  const level = (verdict.risk_level || "low").toLowerCase();
  if (stats[level] !== undefined) stats[level]++;
  await chrome.storage.local.set({ stats });
}
