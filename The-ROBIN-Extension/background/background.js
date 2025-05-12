// Set up context menu
chrome.runtime.onInstalled.addListener(() => {
  // Set default options
  chrome.storage.local.set({
    'autoAnalyze': true
  });
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeFromBackground') {
    // In a real extension, this would call your server API
    // For this demo, we'll just send a simulated response back
    sendResponse({
      success: true,
      fraudScore: 45,
      verdict: 'Suspicious'
    });
  }
});