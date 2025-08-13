// == Medical Fact Verifier Background Script ==
// Handles context menu and basic extension setup

chrome.runtime.onInstalled.addListener(() => {
  // Create context menu for text selection
  chrome.contextMenus.create({
    id: 'verify-medical-fact',
    title: 'Verify Medical Fact',
    contexts: ['selection']
  });
  
  console.log('Medical Fact Verifier extension installed');
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'verify-medical-fact' && info.selectionText) {
    // Send message to content script to verify the selected text
    try {
      await chrome.tabs.sendMessage(tab.id, {
        action: 'verifyFact',
        text: info.selectionText
      });
    } catch (error) {
      console.error('Error sending message to content script:', error);
    }
  }
});

console.log('Medical Fact Verifier background script loaded');
