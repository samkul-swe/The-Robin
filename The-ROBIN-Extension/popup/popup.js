document.addEventListener('DOMContentLoaded', function() {
  const jobTitleEl = document.getElementById('job-title');
  const companyNameEl = document.getElementById('company-name');
  const noJobEl = document.getElementById('no-job');
  const loadingEl = document.getElementById('loading');
  const resultsEl = document.getElementById('results');
  const fraudScoreEl = document.getElementById('fraud-score');
  const scoreMeterEl = document.getElementById('score-meter');
  const verdictIconEl = document.getElementById('verdict-icon');
  const verdictTextEl = document.getElementById('verdict-text');
  const analyzeBtn = document.getElementById('analyze-btn');
  const detailsBtn = document.getElementById('details-btn');

  // Check if we're on a job page
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    const currentTab = tabs[0];
    
    // Check for saved results
    chrome.storage.local.get(['lastAnalyzedUrl', 'lastResult'], function(data) {
      if (data.lastAnalyzedUrl === currentTab.url && data.lastResult) {
        // Show saved results
        displayResults(data.lastResult);
      } else {
        // Check if we're on a job page
        chrome.tabs.sendMessage(currentTab.id, {action: "checkJobPage"}, function(response) {
          if (response && response.isJobPage) {
            // We're on a job page
            jobTitleEl.textContent = response.jobTitle || "Job Posting";
            companyNameEl.textContent = response.companyName || "";
            
            noJobEl.classList.add('hidden');
            resultsEl.classList.remove('hidden');
            
            // Update "View Details" link
            detailsBtn.href = `https://your-robin-website.com/analyze?url=${encodeURIComponent(currentTab.url)}`;
          } else {
            // Not on a job page
            jobTitleEl.textContent = "No job posting detected";
            companyNameEl.textContent = "";
            
            noJobEl.classList.remove('hidden');
            resultsEl.classList.add('hidden');
          }
        });
      }
    });
  });

  // Analyze button click handler
  analyzeBtn.addEventListener('click', function() {
    // Show loading state
    loadingEl.classList.remove('hidden');
    resultsEl.classList.add('hidden');
    
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      const currentTab = tabs[0];
      
      // Send message to content script to analyze the job
      chrome.tabs.sendMessage(currentTab.id, {action: "analyzeJob"}, function(response) {
        loadingEl.classList.add('hidden');
        
        if (response && response.success) {
          // Save the result
          chrome.storage.local.set({
            'lastAnalyzedUrl': currentTab.url,
            'lastResult': response.result
          });
          
          // Display the results
          displayResults(response.result);
        } else {
          // Error analyzing job
          alert('Error analyzing job posting. Please try again.');
          resultsEl.classList.remove('hidden');
        }
      });
    });
  });

  // Function to display results
  function displayResults(result) {
    // Show results section
    noJobEl.classList.add('hidden');
    loadingEl.classList.add('hidden');
    resultsEl.classList.remove('hidden');
    
    // Update fraud score
    fraudScoreEl.textContent = `${Math.round(result.fraudScore)}%`;
    
    // Update score meter
    scoreMeterEl.style.width = `${result.fraudScore}%`;
    
    // Set color based on score
    if (result.fraudScore < 30) {
      scoreMeterEl.style.backgroundColor = 'var(--safe-color)';
      verdictIconEl.textContent = '✅';
      verdictTextEl.textContent = 'Likely Legitimate';
    } else if (result.fraudScore < 70) {
      scoreMeterEl.style.backgroundColor = 'var(--warning-color)';
      verdictIconEl.textContent = '⚠️';
      verdictTextEl.textContent = 'Suspicious - Use Caution';
    } else {
      scoreMeterEl.style.backgroundColor = 'var(--danger-color)';
      verdictIconEl.textContent = '🚫';
      verdictTextEl.textContent = 'Likely Fraudulent';
    }
    
    // Update "View Details" link with result ID if available
    if (result.resultId) {
      detailsBtn.href = `https://your-robin-website.com/results/${result.resultId}`;
    }
  }
});