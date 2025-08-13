// == Medical Fact Verifier content script ==
// Adds a floating 'Verify' bubble near any selection and receives context-menu triggers.

const BACKEND_URL = "http://localhost:5000"; // Your backend URL
let floatBtn = null;

function createFloatButton(x, y, text) {
  removeFloatButton();
  floatBtn = document.createElement("button");
  floatBtn.textContent = "Verify";
  floatBtn.id = "medical-verifier-float-btn";
  floatBtn.style.position = "absolute";
  floatBtn.style.top = `${y + 10}px`;
  floatBtn.style.left = `${x}px`;
  floatBtn.style.zIndex = 2147483647;
  floatBtn.className = "medical-verifier-float-btn";
  floatBtn.onclick = () => verifyFact(text);
  document.body.appendChild(floatBtn);
}

function removeFloatButton() {
  if (floatBtn && floatBtn.parentNode)
    floatBtn.parentNode.removeChild(floatBtn);
  floatBtn = null;
}

document.addEventListener("mouseup", (e) => {
  // Ignore mouseup on our own UI so the button's click can fire
  if (
    e.target &&
    (e.target.id === "medical-verifier-float-btn" ||
      (e.target.closest && e.target.closest(".medical-verifier-popup")))
  ) {
    return;
  }

  const sel = window.getSelection();
  const text = sel && sel.toString().trim();
  removeFloatButton();
  if (text && text.length > 3) {
    const rect = sel.getRangeAt(0).getBoundingClientRect();
    createFloatButton(
      rect.left + window.scrollX,
      rect.bottom + window.scrollY,
      text
    );
  }
});

chrome.runtime.onMessage.addListener((request) => {
  if (request.action === "verifyFact") {
    verifyFact(request.text);
  }
});

async function verifyFact(factText) {
  try {
    // Clean up the floating button as we start verification
    removeFloatButton();
    const resp = await fetch(`${BACKEND_URL}/api/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: factText }),
    });
    const data = await resp.json();
    showVerdictPopup(data, factText);
  } catch (e) {
    showVerdictPopup({ 
      status: "error",
      corrected_fact: "Caution — Backend not reachable.",
      explanation: "Please check if the backend server is running.",
      source_links: []
    }, factText);
  }
}

function showVerdictPopup(data, factText) {
  const sel = window.getSelection();
  const rect = sel.rangeCount
    ? sel.getRangeAt(0).getBoundingClientRect()
    : { left: 20, bottom: 20 };

  const popup = document.createElement("div");
  popup.className = "medical-verifier-popup";
  
  // Get status color and icon
  const statusInfo = getStatusInfo(data.status);
  
  popup.innerHTML = `
    <div class="mv-header">
      ${statusInfo.icon} Medical Fact Verification
    </div>
    <div class="mv-claim"><b>Claim:</b> ${escapeHtml(
      factText.slice(0, 160)
    )}</div>
    <div class="mv-verdict ${data.status}" style="background: ${statusInfo.bgColor}; color: ${statusInfo.textColor};">
      <b>Verdict:</b> ${escapeHtml(data.corrected_fact || "Unable to verify")}
    </div>
    ${data.explanation ? `<div class="mv-explanation"><b>Explanation:</b> ${escapeHtml(data.explanation)}</div>` : ''}
    ${renderSources(data.source_links)}
    <div class="mv-close" onclick="this.parentElement.remove()">✕</div>
  `;

  popup.style.top = `${rect.bottom + window.scrollY + 8}px`;
  popup.style.left = `${rect.left + window.scrollX}px`;
  document.body.appendChild(popup);

  setTimeout(() => {
    if (popup && popup.parentNode) popup.parentNode.removeChild(popup);
  }, 15000);
}

function getStatusInfo(status) {
  switch(status) {
    case 'safe':
      return { icon: '✅', bgColor: '#d4edda', textColor: '#155724' };
    case 'caution':
      return { icon: '⚠️', bgColor: '#fff3cd', textColor: '#856404' };
    case 'harmful':
      return { icon: '❌', bgColor: '#f8d7da', textColor: '#721c24' };
    default:
      return { icon: '❓', bgColor: '#f8f9fa', textColor: '#495057' };
  }
}

function renderSources(sources) {
  if (!sources || !sources.length)
    return "<div class='mv-sources'>No sources available.</div>";
  const links = sources
    .slice(0, 3)
    .map((url) => {
      const domain = new URL(url).hostname;
      return `<a href="${url}" target="_blank" rel="noreferrer">${escapeHtml(domain)}</a>`;
    })
    .join(" • ");
  return `<div class='mv-sources'><b>Sources:</b> ${links}</div>`;
}

function escapeHtml(s) {
  return (s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

console.log('Medical Fact Verifier content script loaded');
