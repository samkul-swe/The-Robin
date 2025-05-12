// Variables to store job information
let jobData = null;
let jobBadge = null;

// Initialize content script
function init() {
  // Detect what job site we're on and extract job data
  const hostname = window.location.hostname;
  
  if (hostname.includes('indeed.com')) {
    jobData = extractIndeedJobData();
  } else if (hostname.includes('linkedin.com')) {
    jobData = extractLinkedInJobData();
  } else if (hostname.includes('glassdoor.com')) {
    jobData = extractGlassdoorJobData();
  } else if (hostname.includes('monster.com')) {
    jobData = extractMonsterJobData();
  } else if (hostname.includes('ziprecruiter.com')) {
    jobData = extractZipRecruiterJobData();
  }
  
  // Add message listener
  chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === "checkJobPage") {
      // Check if we detected a job posting
      sendResponse({
        isJobPage: jobData !== null,
        jobTitle: jobData ? jobData.title : null,
        companyName: jobData ? jobData.company : null
      });
    } else if (request.action === "analyzeJob") {
      // Analyze the current job
      analyzeJob().then(result => {
        sendResponse(result);
      });
      
      // Return true to indicate we will send a response asynchronously
      return true;
    } else if (request.action === "showBadge" && request.result) {
      // Show badge with results
      showJobBadge(request.result);
      sendResponse({success: true});
    }
  });
  
  // Check if we should auto-analyze
  chrome.storage.local.get(['autoAnalyze'], function(data) {
    if (data.autoAnalyze && jobData) {
      // Auto-analyze after a short delay
      setTimeout(() => {
        analyzeJob().then(response => {
          if (response.success) {
            showJobBadge(response.result);
          }
        });
      }, 1500);
    }
  });
}

// Extract job data from Indeed
function extractIndeedJobData() {
  const titleEl = document.querySelector('.jobsearch-JobInfoHeader-title');
  const companyEl = document.querySelector('.jobsearch-InlineCompanyRating-companyName');
  const descriptionEl = document.querySelector('#jobDescriptionText');
  
  if (!titleEl || !descriptionEl) return null;
  
  return {
    title: titleEl.textContent.trim(),
    company: companyEl ? companyEl.textContent.trim() : '',
    description: descriptionEl.textContent.trim()
  };
}

// Extract job data from LinkedIn
function extractLinkedInJobData() {
  const titleEl = document.querySelector('.top-card-layout__title');
  const companyEl = document.querySelector('.topcard__org-name-link');
  const descriptionEl = document.querySelector('.description__text');
  
  if (!titleEl || !descriptionEl) return null;
  
  return {
    title: titleEl.textContent.trim(),
    company: companyEl ? companyEl.textContent.trim() : '',
    description: descriptionEl.textContent.trim()
  };
}

// Extract job data from Glassdoor
function extractGlassdoorJobData() {
  const titleEl = document.querySelector('[data-test="job-title"]');
  const companyEl = document.querySelector('[data-test="employer-name"]');
  const descriptionEl = document.querySelector('[data-test="description"]');
  
  if (!titleEl || !descriptionEl) return null;
  
  return {
    title: titleEl.textContent.trim(),
    company: companyEl ? companyEl.textContent.trim() : '',
    description: descriptionEl.textContent.trim()
  };
}

// Extract job data from Monster
function extractMonsterJobData() {
  const titleEl = document.querySelector('.job-title');
  const companyEl = document.querySelector('.company-name');
  const descriptionEl = document.querySelector('.job-description');
  
  if (!titleEl || !descriptionEl) return null;
  
  return {
    title: titleEl.textContent.trim(),
    company: companyEl ? companyEl.textContent.trim() : '',
    description: descriptionEl.textContent.trim()
  };
}

// Extract job data from ZipRecruiter
function extractZipRecruiterJobData() {
  const titleEl = document.querySelector('.job_title');
  const companyEl = document.querySelector('.hiring_company_text');
  const descriptionEl = document.querySelector('#job_description');
  
  if (!titleEl || !descriptionEl) return null;
  
  return {
    title: titleEl.textContent.trim(),
    company: companyEl ? companyEl.textContent.trim() : '',
    description: descriptionEl.textContent.trim()
  };
}

// Analyze the current job
async function analyzeJob() {
  if (!jobData) {
    return { success: false, error: 'No job data found' };
  }
  
  try {
    // In a real extension, we would send the job data to our server for analysis
    // For this example, we'll use a simplified local evaluation
    
    // Simulate API call to The-ROBIN server
    // In a real implementation, this would be an actual fetch request to your API
    // const response = await fetch('https://your-robin-api.com/analyze', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(jobData)
    // });
    // const result = await response.json();
    
    // For this example, we'll simulate the analysis
    const result = simulateJobAnalysis(jobData);
    
    return { success: true, result: result };
  } catch (error) {
    console.error('Error analyzing job:', error);
    return { success: false, error: 'Error analyzing job' };
  }
}

// Simulate job analysis for the example
function simulateJobAnalysis(jobData) {
  // Check for suspicious keywords in title and description
  const suspiciousWords = [
    'unlimited income', 'work from home millionaire', 'be your own boss',
    'opportunity of a lifetime', 'no experience necessary', 'payment required',
    'training fee', 'immediate start', 'urgent hiring'
  ];
  
  // Count suspicious words
  let suspiciousWordCount = 0;
  const combinedText = (jobData.title + ' ' + jobData.description).toLowerCase();
  
  suspiciousWords.forEach(word => {
    if (combinedText.includes(word)) {
      suspiciousWordCount++;
    }
  });
  
  // Calculate fraud score (0-100)
  let fraudScore = 0;
  
  if (suspiciousWordCount >= 3) {
    fraudScore = 75 + Math.random() * 25; // 75-100%
  } else if (suspiciousWordCount >= 1) {
    fraudScore = 30 + Math.random() * 45; // 30-75%
  } else {
    fraudScore = Math.random() * 30; // 0-30%
  }
  
  // Generate fake resultId (in a real implementation, this would come from your backend)
  const resultId = 'result_' + Math.random().toString(36).substring(2, 15);
  
  return {
    fraudScore: fraudScore,
    resultId: resultId,
    jobTitle: jobData.title,
    companyName: jobData.company
  };
}

// Show job badge with fraud score
function showJobBadge(result) {
  // Remove existing badge if any
  if (jobBadge) {
    jobBadge.remove();
  }
  
  // Create badge
  jobBadge = document.createElement('div');
  jobBadge.className = 'robin-job-badge';
  
  // Set badge content
  let badgeColor, badgeIcon, badgeText;
  
  if (result.fraudScore < 30) {
    badgeColor = 'var(--safe-color)';
    badgeIcon = '✅';
    badgeText = 'Likely Legitimate';
  } else if (result.fraudScore < 70) {
    badgeColor = 'var(--warning-color)';
    badgeIcon = '⚠️';
    badgeText = 'Suspicious';
  } else {
    badgeColor = 'var(--danger-color)';
    badgeIcon = '🚫';
    badgeText = 'Likely Fraudulent';
  }
  
  // Set badge HTML
  jobBadge.innerHTML = `
    <div class="robin-badge-header" style="background-color: ${badgeColor}">
      <img src="${chrome.runtime.getURL('icons/icon-16.png')}" alt="ROBIN">
      <span>The-ROBIN</span>
    </div>
    <div class="robin-badge-content">
      <div class="robin-badge-score">
        <span class="robin-score-label">Fraud Score:</span>
        <span class="robin-score-value">${Math.round(result.fraudScore)}%</span>
      </div>
      <div class="robin-badge-verdict">
        <span class="robin-verdict-icon">${badgeIcon}</span>
        <span class="robin-verdict-text">${badgeText}</span>
      </div>
      <a href="https://your-robin-website.com/results/${result.resultId}" target="_blank" class="robin-badge-details">
        View Details
      </a>
    </div>
  `;
  
  // Find insertion point (depends on job site)
  let insertionPoint;
  const hostname = window.location.hostname;
  
  if (hostname.includes('indeed.com')) {
    insertionPoint = document.querySelector('.jobsearch-JobInfoHeader-title-container');
  } else if (hostname.includes('linkedin.com')) {
    insertionPoint = document.querySelector('.top-card-layout__card');
  } else if (hostname.includes('glassdoor.com')) {
    insertionPoint = document.querySelector('[data-test="job-header"]');
  } else if (hostname.includes('monster.com')) {
    insertionPoint = document.querySelector('.job-header');
  } else if (hostname.includes('ziprecruiter.com')) {
    insertionPoint = document.querySelector('.job_header');
  }
  
  // Insert badge
  if (insertionPoint) {
    insertionPoint.appendChild(jobBadge);
  } else {
    // Fallback - insert at beginning of body
    document.body.insertBefore(jobBadge, document.body.firstChild);
  }
}

// Initialize on page load
window.addEventListener('load', init);