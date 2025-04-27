// content.js for ScamSuit - Fake Job Detection Plugin

// Job site selectors for popular job platforms
const SITE_SELECTORS = {
    // LinkedIn
    linkedin: {
      title: '.job-details-jobs-unified-top-card__job-title',
      company: '.job-details-jobs-unified-top-card__company-name',
      description: '.jobs-description',
      requirements: '.jobs-box__html-content',
      location: '.job-details-jobs-unified-top-card__bullet',
      salary: '.job-details-jobs-unified-top-card__job-insight'
    },
    // Indeed
    indeed: {
      title: '.jobsearch-JobInfoHeader-title',
      company: '.jobsearch-InlineCompanyRating-companyName',
      description: '#jobDescriptionText',
      location: '.jobsearch-JobInfoHeader-subtitle',
      salary: '.salary-snippet-container'
    },
    // Monster
    monster: {
      title: '.job-title',
      company: '.name',
      description: '.details-content',
      location: '.location'
    },
    // Glassdoor
    glassdoor: {
      title: '.job-title',
      company: '.employer-name',
      description: '.jobDescriptionContent',
      salary: '.salary-estimate'
    },
    // General fallback selectors
    general: {
      title: 'h1, .job-title, .title',
      company: '.company, .company-name, [itemprop="hiringOrganization"]',
      description: '.job-description, .description, [itemprop="description"]',
      requirements: '.requirements, .qualifications',
      benefits: '.benefits, .perks',
      location: '.location, [itemprop="jobLocation"]',
      salary: '.salary, .compensation'
    }
  };
  
  /**
   * Determines which job site the user is currently on
   * @returns {string} Site identifier
   */
  function detectJobSite() {
    const url = window.location.hostname;
    
    if (url.includes('linkedin')) return 'linkedin';
    if (url.includes('indeed')) return 'indeed';
    if (url.includes('monster')) return 'monster';
    if (url.includes('glassdoor')) return 'glassdoor';
    
    return 'general';
  }
  
  /**
   * Gets the text content of an element safely
   * @param {string} selector - CSS selector for element
   * @param {Element} context - DOM context to search within
   * @returns {string} Text content or empty string
   */
  function getTextContent(selector, context = document) {
    const element = context.querySelector(selector);
    return element ? element.textContent.trim() : '';
  }
  
  /**
   * Extracts job details from the current page
   * @returns {Object} Job details
   */
  function getJobDetails() {
    const site = detectJobSite();
    const selectors = SITE_SELECTORS[site];
    
    // Extract job information using the appropriate selectors
    const jobData = {
      title: getTextContent(selectors.title),
      company: getTextContent(selectors.company),
      description: getTextContent(selectors.description),
      location: selectors.location ? getTextContent(selectors.location) : '',
      requirements: selectors.requirements ? getTextContent(selectors.requirements) : '',
      benefits: selectors.benefits ? getTextContent(selectors.benefits) : '',
      salary: selectors.salary ? getTextContent(selectors.salary) : '',
      url: window.location.href,
      extractedAt: new Date().toISOString()
    };
    
    // Log extraction results for debugging
    console.log('ScamSuit - Extracted job data:', jobData);
    
    // For fields that weren't found, try general selectors
    for (const [key, value] of Object.entries(jobData)) {
      if (!value && SITE_SELECTORS.general[key]) {
        jobData[key] = getTextContent(SITE_SELECTORS.general[key]);
      }
    }
    
    return jobData;
  }
  
  /**
   * Creates and shows the ScamSuit analysis UI
   * @param {Object} analysisResult - Analysis from the ML models
   */
  function showAnalysisUI(analysisResult) {
    // Remove any existing analysis display
    const existingDisplay = document.getElementById('scamsuit-result');
    if (existingDisplay) {
      existingDisplay.remove();
    }
    
    // Create elements
    const container = document.createElement('div');
    container.id = 'scamsuit-result';
    container.style = `
      position: fixed;
      top: 20px;
      right: 20px;
      width: 320px;
      padding: 15px;
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      z-index: 9999;
      font-family: Arial, sans-serif;
      max-height: 80vh;
      overflow-y: auto;
    `;
    
    // Header section
    const header = document.createElement('div');
    header.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <h2 style="margin: 0; font-size: 18px;">ScamSuit Analysis</h2>
        <button id="scamsuit-close" style="border: none; background: transparent; cursor: pointer; font-size: 18px;">×</button>
      </div>
      <div style="height: 5px; background-color: ${analysisResult.voting_result.color_indicator}; margin-bottom: 15px; border-radius: 2px;"></div>
    `;
    container.appendChild(header);
    
    // Risk level section
    const riskSection = document.createElement('div');
    riskSection.innerHTML = `
      <div style="display: flex; align-items: center; margin-bottom: 15px;">
        <div style="width: 20px; height: 20px; border-radius: 50%; background-color: ${analysisResult.voting_result.color_indicator}; margin-right: 10px;"></div>
        <div>
          <div style="font-weight: bold;">${analysisResult.voting_result.risk_level.toUpperCase()} RISK</div>
          <div style="font-size: 12px;">${analysisResult.voting_result.votes_for_fraud} out of ${analysisResult.voting_result.total_votes} models flagged this job</div>
        </div>
      </div>
      <div style="margin-bottom: 15px;">
        <div style="font-weight: bold;">Fraud probability: ${Math.round(analysisResult.voting_result.avg_probability * 100)}%</div>
        <div style="height: 10px; background: #eee; border-radius: 5px; margin-top: 5px;">
          <div style="height: 100%; width: ${Math.round(analysisResult.voting_result.avg_probability * 100)}%; background-color: ${analysisResult.voting_result.color_indicator}; border-radius: 5px;"></div>
        </div>
      </div>
    `;
    container.appendChild(riskSection);
    
    // If flagged as fraudulent, show explanation
    if (analysisResult.explanation && analysisResult.explanation.reasons) {
      const explanationSection = document.createElement('div');
      explanationSection.innerHTML = `
        <div style="margin-bottom: 15px;">
          <h3 style="margin: 0 0 10px 0; font-size: 16px;">Warning Signs</h3>
          <ul style="margin: 0; padding-left: 20px;">
            ${analysisResult.explanation.reasons.map(reason => `<li style="margin-bottom: 5px;">${reason}</li>`).join('')}
          </ul>
        </div>
      `;
      container.appendChild(explanationSection);
      
      // Add advice section
      const adviceSection = document.createElement('div');
      adviceSection.innerHTML = `
        <div style="background-color: #f8f8f8; padding: 10px; border-radius: 5px; margin-top: 10px;">
          <h3 style="margin: 0 0 5px 0; font-size: 14px;">Safety Advice</h3>
          <ul style="margin: 0; padding-left: 20px; font-size: 13px;">
            <li>Research the company thoroughly before applying</li>
            <li>Never pay money to apply for a job</li>
            <li>Avoid sharing personal financial information</li>
            <li>Be wary of jobs that seem too good to be true</li>
          </ul>
        </div>
      `;
      container.appendChild(adviceSection);
    }
    
    // Add close button functionality
    document.body.appendChild(container);
    document.getElementById('scamsuit-close').addEventListener('click', () => {
      container.remove();
    });
  }
  
  /**
   * Analyze the current job posting using the ML models
   */
  function analyzeCurrentJob() {
    const jobData = getJobDetails();
    
    // Send job data to background script for ML analysis
    chrome.runtime.sendMessage(
      {action: 'analyzeJob', jobData: jobData},
      function(response) {
        if (response.error) {
          console.error('ScamSuit analysis error:', response.error);
          return;
        }
        
        // If job is flagged as fraudulent, get explanation
        if (response.voting_result.is_fraudulent) {
          chrome.runtime.sendMessage(
            {action: 'explainAnalysis', jobData: jobData},
            function(explanation) {
              response.explanation = explanation;
              showAnalysisUI(response);
            }
          );
        } else {
          showAnalysisUI(response);
        }
      }
    );
  }
  
  // Listen for messages from popup or background
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getJobInfo') {
      const jobDetails = getJobDetails();
      sendResponse(jobDetails);
    }
    else if (request.action === 'analyzeCurrentJob') {
      analyzeCurrentJob();
      sendResponse({status: 'analysis_started'});
    }
    return true; // Required for async response
  });
  
  // Automatically analyze job when page loads on job sites
  if (window.location.href.includes('/job/') || 
      window.location.href.includes('/jobs/') ||
      window.location.href.includes('job-details') ||
      window.location.href.includes('job-listing')) {
    
    // Wait for page to fully load
    window.addEventListener('load', () => {
      // Small delay to ensure dynamic content is loaded
      setTimeout(() => {
        analyzeCurrentJob();
      }, 1500);
    });
  }
  
  // Add a context menu item for manual analysis
  document.addEventListener('contextmenu', function(event) {
    // Store target element for context menu
    window.scamsuitContextTarget = event.target;
  }, true);