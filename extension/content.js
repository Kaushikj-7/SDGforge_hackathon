/**
 * content.js — Health Fact Checker
 *
 * Responsibilities:
 *   1. Detect when user highlights text containing a health claim
 *   2. Show a micro-popup button anchored to the selection
 *   3. On click, expand the popup and stream the verdict from backend
 *
 * Critical constraints:
 *   - Zero DOM mutation on the host page (Shadow DOM only)
 *   - Works on sites with strict CSP (WebMD, Healthline, NEJM, etc.)
 *   - No external libraries — vanilla JS only
 *   - Bundle size: this file should stay under 15kb
 */

const BACKEND_URL = "http://127.0.0.1:8000";  // change to prod URL
const MIN_SELECTION_LENGTH = 15;
const HEALTH_TRIGGER_WORDS = [
  "cure", "treat", "prevent", "cancer", "diabetes", "vaccine", "drug",
  "vitamin", "supplement", "dose", "medication", "symptom", "disease",
  "infection", "antibody", "immune", "clinical", "study", "research",
  "mg", "proven", "natural", "toxic", "harmful", "safe", "effective"
];

// ─── Shadow DOM container ──────────────────────────────────────────────────

let hostEl = null;
let shadowRoot = null;
let currentPopup = null;

function ensureShadowHost() {
  if (hostEl) return;
  hostEl = document.createElement("div");
  hostEl.id = "hfc-host";
  // position: fixed so it floats above page content
  // pointer-events: none so it doesn't block page clicks by default
  hostEl.style.cssText = "position:fixed;top:0;left:0;width:0;height:0;z-index:2147483647;pointer-events:none;";
  document.body.appendChild(hostEl);
  shadowRoot = hostEl.attachShadow({ mode: "open" });

  // All styles live inside Shadow DOM — completely isolated from host page
  const style = document.createElement("style");
  style.textContent = `
    .hfc-btn {
      position: fixed;
      background: #1a73e8;
      color: #fff;
      border: none;
      border-radius: 6px;
      padding: 5px 10px;
      font-size: 12px;
      font-family: -apple-system, sans-serif;
      cursor: pointer;
      pointer-events: all;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      white-space: nowrap;
      transition: background 0.15s;
      z-index: 1;
    }
    .hfc-btn:hover { background: #1557b0; }

    .hfc-card {
      position: fixed;
      background: #fff;
      border: 1px solid #e0e0e0;
      border-radius: 10px;
      padding: 14px 16px;
      font-family: -apple-system, sans-serif;
      font-size: 13px;
      color: #202124;
      min-width: 280px;
      max-width: 360px;
      pointer-events: all;
      z-index: 2;
    }
    @media (prefers-color-scheme: dark) {
      .hfc-card { background: #1e1e1e; border-color: #333; color: #e0e0e0; }
    }

    .hfc-status {
      color: #666;
      font-size: 12px;
      margin-bottom: 8px;
      min-height: 18px;
    }
    .hfc-verdict-badge {
      display: inline-block;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .hfc-CRITICAL { background: #fce8e6; color: #c5221f; }
    .hfc-HIGH     { background: #fef3e2; color: #b45309; }
    .hfc-MEDIUM   { background: #fef9e7; color: #92400e; }
    .hfc-LOW      { background: #e6f4ea; color: #137333; }

    .hfc-confidence-bar {
      height: 4px;
      background: #e0e0e0;
      border-radius: 2px;
      margin: 6px 0;
      overflow: hidden;
    }
    .hfc-confidence-fill {
      height: 100%;
      border-radius: 2px;
      background: #1a73e8;
      transition: width 0.4s ease;
    }
    .hfc-correction {
      font-size: 12px;
      color: #333;
      line-height: 1.5;
      margin: 8px 0;
    }
    @media (prefers-color-scheme: dark) {
      .hfc-correction { color: #ccc; }
      .hfc-status { color: #888; }
    }
    .hfc-sources {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-top: 8px;
    }
    .hfc-source-pill {
      background: #e8f0fe;
      color: #1a73e8;
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 10px;
      text-decoration: none;
      pointer-events: all;
    }
    .hfc-source-pill:hover { background: #d2e3fc; }
    .hfc-close {
      position: absolute;
      top: 8px;
      right: 10px;
      background: none;
      border: none;
      font-size: 16px;
      cursor: pointer;
      color: #666;
      pointer-events: all;
      line-height: 1;
    }
    .hfc-spinner {
      display: inline-block;
      width: 12px;
      height: 12px;
      border: 2px solid #e0e0e0;
      border-top-color: #1a73e8;
      border-radius: 50%;
      animation: hfc-spin 0.6s linear infinite;
      margin-right: 6px;
      vertical-align: middle;
    }
    @keyframes hfc-spin { to { transform: rotate(360deg); } }
  `;
  shadowRoot.appendChild(style);
}

// ─── Health claim detector ──────────────────────────────────────────────────

function isHealthRelated(text) {
  const lower = text.toLowerCase();
  return HEALTH_TRIGGER_WORDS.some(word => lower.includes(word));
}

function getSurroundingContext(selection) {
  /**
   * Extract ±500 chars of surrounding text from the DOM.
   * Uses the Range API — no fetch, no network, reads from live DOM.
   */
  try {
    const range = selection.getRangeAt(0);
    const container = range.commonAncestorContainer;
    const parent = container.nodeType === 3 ? container.parentElement : container;
    const fullText = parent.innerText || parent.textContent || "";
    const selectedText = selection.toString();
    const idx = fullText.indexOf(selectedText);
    if (idx === -1) return fullText.slice(0, 500);
    const start = Math.max(0, idx - 250);
    const end   = Math.min(fullText.length, idx + selectedText.length + 250);
    return fullText.slice(start, end);
  } catch {
    return "";
  }
}

// ─── Popup builder ─────────────────────────────────────────────────────────

function removeCurrentPopup() {
  if (currentPopup && shadowRoot.contains(currentPopup)) {
    shadowRoot.removeChild(currentPopup);
  }
  currentPopup = null;
}

function showMicroButton(x, y, onVerify) {
  ensureShadowHost();
  removeCurrentPopup();

  const btn = document.createElement("button");
  btn.className = "hfc-btn";
  btn.textContent = "Check  Verify claim";
  btn.style.left = `${Math.min(x, window.innerWidth - 160)}px`;
  btn.style.top  = `${y + 8}px`;

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    onVerify();
  });

  hostEl.style.pointerEvents = "none"; // allow pass-through except on the button
  shadowRoot.appendChild(btn);
  currentPopup = btn;
}

function showLoadingCard(x, y, selectedText) {
  ensureShadowHost();
  removeCurrentPopup();

  const card = document.createElement("div");
  card.className = "hfc-card";
  card.style.left = `${Math.min(x, window.innerWidth - 380)}px`;
  card.style.top  = `${Math.min(y + 8, window.innerHeight - 300)}px`;

  card.innerHTML = `
    <button class="hfc-close">×</button>
    <div style="font-size:12px;color:#666;margin-bottom:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:280px;">
      "${selectedText.slice(0, 60)}${selectedText.length > 60 ? '...' : ''}"
    </div>
    <div class="hfc-status">
      <span class="hfc-spinner"></span>
      <span id="hfc-status-text">Analyzing claim...</span>
    </div>
    <div class="hfc-confidence-bar">
      <div class="hfc-confidence-fill" id="hfc-conf-fill" style="width:5%"></div>
    </div>
  `;

  card.querySelector(".hfc-close").addEventListener("click", removeCurrentPopup);
  shadowRoot.appendChild(card);
  currentPopup = card;
  return card;
}

function updateStatus(card, message, confidence) {
  const statusEl = card.querySelector("#hfc-status-text");
  const confFill = card.querySelector("#hfc-conf-fill");
  if (statusEl) statusEl.textContent = message;
  if (confFill && confidence) confFill.style.width = `${Math.round(confidence * 100)}%`;
}

function renderVerdict(card, verdict) {
  const riskColor = {
    CRITICAL: "#c5221f",
    HIGH:     "#b45309",
    MEDIUM:   "#92400e",
    LOW:      "#137333"
  };

  const sourcePills = (verdict.sources || [])
    .slice(0, 3)
    .map(s => `<a class="hfc-source-pill" href="${s.url}" target="_blank">${s.name}</a>`)
    .join("");

  card.innerHTML = `
    <button class="hfc-close">×</button>
    <div>
      <span class="hfc-verdict-badge hfc-${verdict.risk_level}">
        ${verdict.risk_level} — ${verdict.verdict}
      </span>
    </div>
    <div class="hfc-confidence-bar">
      <div class="hfc-confidence-fill" style="width:${Math.round((verdict.confidence || 0) * 100)}%"></div>
    </div>
    <div style="font-size:11px;color:#888;margin-bottom:6px;">
      Confidence: ${Math.round((verdict.confidence || 0) * 100)}%
    </div>
    <div class="hfc-correction">${verdict.correction || ""}</div>
    <div class="hfc-sources">${sourcePills}</div>
  `;
  card.querySelector(".hfc-close").addEventListener("click", removeCurrentPopup);
}

// ─── SSE stream handler ────────────────────────────────────────────────────

async function streamVerdict(payload, card, x, y) {
  /**
   * Connects to the backend SSE endpoint.
   * Updates the card UI as each status event arrives.
   * Renders final verdict when "done" event received.
   *
   * Uses fetch + ReadableStream — works in all MV3 service workers
   * and content scripts. No EventSource needed (doesn't support POST).
   */
  try {
    const response = await fetch(`${BACKEND_URL}/verify/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      updateStatus(card, `Server error: ${response.status}`, 0);
      return;
    }

    const reader  = response.body.getReader();
    const decoder = new TextDecoder();
    let   buffer  = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop(); // keep incomplete last line

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        try {
          const event = JSON.parse(line.slice(6));
          if (!currentPopup) return; // user closed popup — stop

          if (event.status === "done") {
            renderVerdict(card, event.verdict);
            // Log to service worker for dashboard stats
            chrome.runtime.sendMessage({ type: "VERDICT_LOGGED", verdict: event.verdict });
            return;
          }
          if (event.status === "error") {
            updateStatus(card, `Error: ${event.message}`, 0);
            return;
          }
          // Update progress
          updateStatus(card, event.message || "Processing...", event.confidence_so_far || 0);
        } catch {
          // malformed JSON line — skip
        }
      }
    }
  } catch (err) {
    if (currentPopup) updateStatus(card, "Connection failed. Is the backend running?", 0);
  }
}

// ─── Main selection listener ──────────────────────────────────────────────

let selectionTimeout = null;

document.addEventListener("mouseup", (e) => {
  // Debounce — wait 200ms after mouseup to read stable selection
  clearTimeout(selectionTimeout);
  selectionTimeout = setTimeout(() => handleSelectionEnd(e), 200);
});

document.addEventListener("touchend", (e) => {
  clearTimeout(selectionTimeout);
  selectionTimeout = setTimeout(() => handleSelectionEnd(e), 300);
});

function handleSelectionEnd(e) {
  // Don't trigger inside our own Shadow DOM
  if (e.target === hostEl || (shadowRoot && shadowRoot.contains(e.target))) return;

  const selection = window.getSelection();
  if (!selection || selection.isCollapsed) {
    // User clicked somewhere without selecting — dismiss micro-button
    // but NOT the card (they might be clicking a source link)
    if (currentPopup && currentPopup.className === "hfc-btn") {
      removeCurrentPopup();
    }
    return;
  }

  const selectedText = selection.toString().trim();
  if (selectedText.length < MIN_SELECTION_LENGTH) return;
  if (!isHealthRelated(selectedText)) return;

  // Get position for popup anchor
  const rect = selection.getRangeAt(0).getBoundingClientRect();
  const x = rect.left + window.scrollX;
  const y = rect.bottom + window.scrollY;

  const surrounding = getSurroundingContext(selection);

  showMicroButton(rect.right, rect.bottom, () => {
    const card = showLoadingCard(rect.left, rect.bottom, selectedText);

    const payload = {
      selected_text:       selectedText,
      surrounding_context: surrounding,
      page_title:          document.title,
      page_url:            window.location.href
    };

    streamVerdict(payload, card, rect.left, rect.bottom);
  });
}

// Dismiss popup on Escape
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") removeCurrentPopup();
});
