// Set up context menu
chrome.runtime.onInstalled.addListener(() => {
  // Set default options
  chrome.storage.local.set({
    'autoAnalyze': true,
    'apiUrl': 'http://localhost:5000' // Add this line to store the API URL
  });
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeFromBackground') {
    // Get the API URL from storage
    chrome.storage.local.get(['apiUrl'], function(data) {
      const apiUrl = data.apiUrl || 'http://localhost:5000';
      
      fetch(`${apiUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request.jobData)
      })
      .then(response => response.json())
      .then(result => {
        sendResponse(result);
      })
      .catch(error => {
        console.error('Error analyzing job:', error);
        sendResponse({ success: false, error: 'Error analyzing job' });
      });
    });
    
    // Return true to indicate we will send a response asynchronously
    return true;
  }
});

// Add a function to get the API URL
function getApiUrl(callback) {
  chrome.storage.local.get(['apiUrl'], function(data) {
    callback(data.apiUrl || 'http://localhost:5000');
  });
}