// == Medical Fact Verifier Background Script ==

const BACKEND_URL = "http://localhost:5001";

chrome.runtime.onInstalled.addListener(() => {
  // Create context menu for both text and visual elements
  chrome.contextMenus.create({
    id: 'verify-medical-fact',
    title: 'Verify Medical Fact',
    contexts: ['selection', 'image', 'page']
  });
  console.log('Medical Fact Verifier background script loaded');
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'verify-medical-fact') {
    
    // First, ask content.js to try capturing text & context from the DOM
    try {
      chrome.tabs.sendMessage(tab.id, { action: 'verifyFactFromBackground' }, async (response) => {
        
        // If content.js successfully grabbed text, it handles the UI. 
        // But if it failed (e.g., text in canvas, image, or blocked), we escalate.
        if (!response || response.status === "escalate_vision" || info.mediaType === "image") {
          console.log("DOM text hidden. Escalating to Multimodal Vision OCR...");
          
          // Notify content.js to show loading state
          chrome.tabs.sendMessage(tab.id, { action: "showLoading" });
          
          executeVisionFallback(tab);
        }
      });
    } catch (error) {
      console.error('Error talking to content script:', error);
      // Fallback if content script not injected yet
      executeVisionFallback(tab);
    }
  }
});

async function executeVisionFallback(tab) {
  console.log("Executing vision fallback for tab:", tab.id);
  try {
    // 1. Capture the visible tab (Quality: 80 to manage token payload size)
    chrome.tabs.captureVisibleTab(tab.windowId, { format: "jpeg", quality: 80 }, async (dataUrl) => {
      if (chrome.runtime.lastError || !dataUrl) {
         console.error("Capture failed:", chrome.runtime.lastError);
         chrome.tabs.sendMessage(tab.id, { 
           action: 'showError', 
           error: chrome.runtime.lastError ? chrome.runtime.lastError.message : "Failed to capture screen." 
         });
         return;
      }
      
      // 2. Format multimodal payload
      const base64Image = dataUrl.split(',')[1];
      const payload = {
        text: "",
        context: "",
        extraction_mode: "vision",
        image_data: base64Image,
        source_url: tab.url,
        user_profile: {} 
      };

      console.log("Sending vision payload to backend...");
      // 3. Send to Python Flask backend
      try {
        const response = await fetch(`${BACKEND_URL}/api/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) throw new Error(`Backend returned ${response.status}`);
        
        const verdict = await response.json();
        console.log("Verdict received:", verdict);
        
        // 4. Send the result back to content.js for UI rendering
        chrome.tabs.sendMessage(tab.id, {
          action: 'showVerdict',
          data: verdict
        }, (response) => {
          if (chrome.runtime.lastError) {
            console.warn("Could not send verdict to content script (tab might be closed or script not injected).");
            // Still update stats locally if possible
            if (verdict && verdict.status) {
              updateVerificationStats(verdict.status);
            }
          }
        });

      } catch (backendError) {
        console.error("Backend error:", backendError);
        chrome.tabs.sendMessage(tab.id, { 
          action: 'showError', 
          error: "Backend not reachable or returned an error." 
        });
      }
    });

  } catch (err) {
    console.error("Vision fallback critical failure:", err);
  }
}

function updateVerificationStats(status) {
  if (!status || status === 'error') return;
  
  chrome.storage.local.get(['verificationStats'], (result) => {
    let stats = result.verificationStats || { total: 0, safe: 0, caution: 0, harmful: 0 };
    stats.total++;
    if (status === 'safe') stats.safe++;
    else if (status === 'caution') stats.caution++;
    else if (status === 'harmful') stats.harmful++;
    chrome.storage.local.set({ verificationStats: stats });
  });
}
