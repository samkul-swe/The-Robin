document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const notJobPagePanel = document.getElementById('not-job-page');
  const jobPagePanel = document.getElementById('job-page');
  const jobTitleEl = document.getElementById('job-title');
  const companyNameEl = document.getElementById('company-name');
  const unanalyzedPanel = document.getElementById('unanalyzed');
  const analyzingPanel = document.getElementById('analyzing');
  const resultsPanel = document.getElementById('results');
  const analyzeBtn = document.getElementById('analyze-btn');
  const reanalyzeBtn = document.getElementById('reanalyze-btn');
  const detailsBtn = document.getElementById('details-btn');
  const fraudScoreEl = document.getElementById('fraud-score');
  const scoreMeterEl = document.getElementById('score-meter');
  const verdictIconEl = document.getElementById('verdict-icon');
  const verdictTextEl = document.getElementById('verdict-text');
  const autoAnalyzeToggle = document.getElementById('auto-analyze');
  const serverSelect = document.getElementById('server-select');
  const saveServerBtn = document.getElementById('save-server-btn');

  // Load settings
  chrome.storage.local.get(['apiUrl', 'autoAnalyze'], function(data) {
    if (data.apiUrl) {
      serverSelect.value = data.apiUrl;
    }
    
    if (data.autoAnalyze !== undefined) {
      autoAnalyzeToggle.checked = data.autoAnalyze;
    } else {
      // Default to true if not set
      autoAnalyzeToggle.checked = true;
      chrome.storage.local.set({ 'autoAnalyze': true });
    }
  });

  // Save settings
  saveServerBtn.addEventListener('click', function() {
    const apiUrl = serverSelect.value;
    chrome.storage.local.set({ 'apiUrl': apiUrl }, function() {
      // Show saved confirmation
      saveServerBtn.textContent = 'Saved!';
      setTimeout(() => { saveServerBtn.textContent = 'Save'; }, 1500);
      
      // Check server connectivity
      checkServerConnectivity(apiUrl);
    });
  });

  // Auto-analyze toggle
  autoAnalyzeToggle.addEventListener('change', function() {
    chrome.storage.local.set({ 'autoAnalyze': this.checked });
  });

  // Check if we're on a job page
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    const currentTab = tabs[0];
    
    // Check if we're on a supported job site
    const supportedSites = [
      'indeed.com',
      'linkedin.com/jobs',
      'glassdoor.com',
      'monster.com',
      'ziprecruiter.com'
    ];
    
    const isJobSite = supportedSites.some(site => currentTab.url.includes(site));
    
    if (!isJobSite) {
      // Not on a job site
      notJobPagePanel.classList.remove('hidden');
      jobPagePanel.classList.add('hidden');
      return;
    }
    
    // We're on a job site
    notJobPagePanel.classList.add('hidden');
    jobPagePanel.classList.remove('hidden');
    
    // Get the API URL from storage
    chrome.storage.local.get(['apiUrl', 'lastAnalyzedUrl', 'lastResult'], function(data) {
      const apiUrl = data.apiUrl || 'http://localhost:5000';
      
      // Check server connectivity
      checkServerConnectivity(apiUrl);
      
      // Try to get job info from content script
      try {
        chrome.tabs.sendMessage(currentTab.id, {action: "checkJobPage"}, function(response) {
          if (chrome.runtime.lastError) {
            console.log("Error:", chrome.runtime.lastError.message);
            jobTitleEl.textContent = "Error detecting job";
            unanalyzedPanel.classList.remove('hidden');
            analyzeBtn.disabled = true;
            return;
          }
          
          if (response && response.isJobPage) {
            // We have job data
            jobTitleEl.textContent = response.jobTitle || "Job Posting";
            companyNameEl.textContent = response.companyName || "";
            
            // Check if we have previously analyzed this URL
            if (data.lastAnalyzedUrl === currentTab.url && data.lastResult) {
              displayResults(data.lastResult, apiUrl);
            } else {
              // Show unanalyzed panel
              unanalyzedPanel.classList.remove('hidden');
              analyzingPanel.classList.add('hidden');
              resultsPanel.classList.add('hidden');
              
              // Check if we should auto-analyze
              if (data.autoAnalyze) {
                analyzeJob(currentTab.id, apiUrl);
              }
            }
          } else {
            // No job data found
            jobTitleEl.textContent = "Job data not found";
            unanalyzedPanel.classList.remove('hidden');
            analyzeBtn.disabled = true;
          }
        });
      } catch (e) {
        console.error("Exception:", e);
        jobTitleEl.textContent = "Error detecting job";
        unanalyzedPanel.classList.remove('hidden');
        analyzeBtn.disabled = true;
      }
    });
  });

  // Analyze button click handler
  analyzeBtn.addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.storage.local.get(['apiUrl'], function(data) {
        const apiUrl = data.apiUrl || 'http://localhost:5000';
        analyzeJob(tabs[0].id, apiUrl);
      });
    });
  });

  // Reanalyze button click handler
  reanalyzeBtn.addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.storage.local.get(['apiUrl'], function(data) {
        const apiUrl = data.apiUrl || 'http://localhost:5000';
        analyzeJob(tabs[0].id, apiUrl);
      });
    });
  });

  // Function to check if server is reachable
  function checkServerConnectivity(apiUrl) {
    unanalyzedPanel.querySelector('p').textContent = "Checking server connectivity...";
    analyzeBtn.disabled = true;
    
    fetch(`${apiUrl}/health`, { 
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      mode: 'cors'
    })
    .then(response => {
      if (response.ok) {
        // Server is reachable
        unanalyzedPanel.querySelector('p').textContent = "This job posting has not been analyzed yet.";
        analyzeBtn.disabled = false;
      } else {
        // Server returned an error
        unanalyzedPanel.querySelector('p').textContent = "Cannot connect to analysis server.";
        analyzeBtn.disabled = true;
      }
    })
    .catch(error => {
      // Server is not reachable
      console.error("Server connectivity error:", error);
      unanalyzedPanel.querySelector('p').textContent = "Cannot connect to analysis server. Please check your server settings.";
      analyzeBtn.disabled = true;
    });
  }

  // Function to analyze the job
  function analyzeJob(tabId, apiUrl) {
    // Show analyzing state
    unanalyzedPanel.classList.add('hidden');
    analyzingPanel.classList.remove('hidden');
    resultsPanel.classList.add('hidden');
    
    // Send message to content script to analyze job
    chrome.tabs.sendMessage(tabId, {action: "analyzeJob", apiUrl: apiUrl}, function(response) {
      // Hide analyzing state
      analyzingPanel.classList.add('hidden');
      
      if (chrome.runtime.lastError) {
        console.error("Error:", chrome.runtime.lastError.message);
        unanalyzedPanel.classList.remove('hidden');
        unanalyzedPanel.querySelector('p').textContent = "Error analyzing job. Please try again.";
        return;
      }
      
      if (response && response.success) {
        // Save the result
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
          chrome.storage.local.set({
            'lastAnalyzedUrl': tabs[0].url,
            'lastResult': response.result
          });
        });
        
        // Display the results
        displayResults(response.result, apiUrl);
        
        // Show badge on the page
        chrome.tabs.sendMessage(tabId, {
          action: "showBadge", 
          result: response.result
        });
      } else {
        // Error analyzing job
        unanalyzedPanel.classList.remove('hidden');
        unanalyzedPanel.querySelector('p').textContent = response?.error || "Error analyzing job. Please try again.";
      }
    });
  }

  // Function to display results
  function displayResults(result, apiUrl) {
    // Show results panel
    unanalyzedPanel.classList.add('hidden');
    analyzingPanel.classList.add('hidden');
    resultsPanel.classList.remove('hidden');
    
    // Update fraud score
    const fraudScore = result.fraudScore || result.confidence_score || 0;
    fraudScoreEl.textContent = `${Math.round(fraudScore)}%`;
    
    // Update score meter
    scoreMeterEl.style.width = `${fraudScore}%`;
    
    // Set color and verdict based on score
    if (fraudScore < 30) {
      scoreMeterEl.style.backgroundColor = 'var(--safe-color)';
      verdictIconEl.textContent = '✅';
      verdictTextEl.textContent = 'Likely Legitimate';
      document.getElementById('verdict').className = 'verdict safe';
    } else if (fraudScore < 70) {
      scoreMeterEl.style.backgroundColor = 'var(--warning-color)';
      verdictIconEl.textContent = '⚠️';
      verdictTextEl.textContent = 'Suspicious - Use Caution';
      document.getElementById('verdict').className = 'verdict warning';
    } else {
      scoreMeterEl.style.backgroundColor = 'var(--danger-color)';
      verdictIconEl.textContent = '🚫';
      verdictTextEl.textContent = 'Likely Fraudulent';
      document.getElementById('verdict').className = 'verdict danger';
    }
    
    // Update "View Details" link with result ID if available
    if (result.resultId) {
      detailsBtn.href = `${apiUrl}/results/${result.resultId}`;
    } else {
      // Fallback to using URL
      chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        detailsBtn.href = `${apiUrl}/analyze?url=${encodeURIComponent(tabs[0].url)}`;
      });
    }
  }
});