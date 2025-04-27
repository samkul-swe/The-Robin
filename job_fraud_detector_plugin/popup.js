document.getElementById('checkJob').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs.length > 0) {
            chrome.tabs.sendMessage(tabs[0].id, { action: 'getJobInfo' }, (response) => {
                if (chrome.runtime.lastError) {
                    console.error(chrome.runtime.lastError); // Log any errors
                    alert('Error: Could not retrieve job information. Please ensure you are on a job listing page.');
                    return;
                }
                if (response) {
                    analyzeJob(response);
                } else {
                    displayResult(false, 0); // No job details found
                }
            });
        }
    });
});

const analyzeJob = async (jobDetails) => {
    const { jobTitle, description } = jobDetails;

    // Replace with your actual model endpoint or logic
    const response = await fetch('https://your-api-endpoint.com/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: jobTitle, description })
    });

    const result = await response.json();
    displayResult(result.isFraudulent, result.confidenceScore);
    
    // Save job details to a file
    saveJobDetails(jobTitle, description, result);
};

const displayResult = (isFraudulent, confidenceScore) => {
    const markElement = document.getElementById('mark');
    const confidenceElement = document.getElementById('confidence');

    if (isFraudulent) {
        markElement.innerText = '✗'; // Cross mark for fake
        markElement.style.color = 'red';
    } else {
        markElement.innerText = '✓'; // Check mark for real
        markElement.style.color = 'green';
    }

    confidenceElement.innerText = `Confidence: ${(confidenceScore * 100).toFixed(2)}%`;
    confidenceElement.style.display = 'block'; // Show confidence score
};

const saveJobDetails = (jobTitle, description, result) => {
    const content = `Job Title: ${jobTitle}\nDescription: ${description}\nFraudulent: ${result.isFraudulent}\nConfidence Score: ${(result.confidenceScore * 100).toFixed(2)}%`;

    console.log('Job Title:', jobTitle);
    console.log('Description:', description);
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'job_details.txt';
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};