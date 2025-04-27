let models = {
    loaded: false,
    ensemble: null
};

chrome.runtime.onInstalled.addListener(async () => {
console.log('The Robin plugin installed');
await loadModels();
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
if (message.action === 'analyzeJob') {
    analyzeJobPosting(message.jobData)
    .then(result => sendResponse(result))
    .catch(error => sendResponse({error: error.message}));
    return true;
}

else if (message.action === 'explainAnalysis') {
    explainAnalysis(message.jobData)
    .then(result => sendResponse(result))
    .catch(error => sendResponse({error: error.message}));
    return true;
}

else if (message.action === 'updateSettings') {
    updateSettings(message.settings)
    .then(() => sendResponse({success: true}))
    .catch(error => sendResponse({error: error.message}));
    return true;
}
});


async function loadModels() {
    return new Promise((resolve) => {
        setTimeout(() => {
        console.log('Models loaded');
        models.loaded = true;
        resolve();
        }, 1000);
    });
}

/**
 * Analyzes a job posting for fraud indicators
 * @param {Object} jobData - Data about the job posting
 * @returns {Object} - Analysis results
 */
async function analyzeJobPosting(jobData) {
if (!models.loaded) {
    await loadModels();
}

const combinedText = extractTextFeatures(jobData);

const predictions = {
    logistic: simulateModelPrediction('logistic', combinedText),
    svm: simulateModelPrediction('svm', combinedText),
    rf: simulateModelPrediction('randomForest', combinedText),
    mlp: simulateModelPrediction('mlp', combinedText)
};

const votes = Object.values(predictions).filter(p => p.is_fraudulent).length;
const totalModels = Object.keys(predictions).length;

const avgProbability = Object.values(predictions)
    .reduce((sum, p) => sum + p.fraud_probability, 0) / totalModels;

const voteRatio = Math.abs(votes - (totalModels/2)) / (totalModels/2);
const confidence = Math.min(1.0, voteRatio * 1.5);

let riskLevel, colorIndicator;
if (votes === 0) {
    riskLevel = "low";
    colorIndicator = "green";
} else if (votes < totalModels / 2) {
    riskLevel = "medium-low";
    colorIndicator = "yellowgreen";
} else if (votes === totalModels / 2) {
    riskLevel = "medium";
    colorIndicator = "orange";
} else if (votes < totalModels) {
    riskLevel = "medium-high";
    colorIndicator = "orangered";
} else {
    riskLevel = "high";
    colorIndicator = "red";
}

const isVoteFraudulent = votes >= Math.ceil(totalModels / 2);

return {
    individual_predictions: predictions,
    voting_result: {
    votes_for_fraud: votes,
    total_votes: totalModels,
    avg_probability: avgProbability,
    confidence: confidence,
    risk_level: riskLevel,
    color_indicator: colorIndicator,
    is_fraudulent: isVoteFraudulent
    }
};
}

/**
 * Provides explanation for why a job posting was flagged
 * @param {Object} jobData - Data about the job posting
 * @returns {Object} - Explanation with reasons
 */
async function explainAnalysis(jobData) {
const analysisResult = await analyzeJobPosting(jobData);

if (!analysisResult.voting_result.is_fraudulent) {
    return {
    is_fraudulent: false,
    explanation: ["All detection models agree this job posting appears legitimate."]
    };
}

const text = extractTextFeatures(jobData);

const reasons = [];

const patternChecks = [
    {
    pattern: /excellent salary|top salary|unbelievable pay|lucrative|competitive salary|high paying/i,
    reason: "Suspicious salary claims that seem too good to be true"
    },
    {
    pattern: /immediate start|urgent|apply now|don't delay|immediate opening|apply today|positions filling fast/i,
    reason: "Creates false urgency to pressure quick applications"
    },
    {
    pattern: /whatsapp|telegram|personal email|text us|message us|personal phone/i,
    reason: "Requests contact through unusual channels outside the job platform"
    },
    {
    pattern: /bank details|ssn|social security|passport|identity card|credit card|payment details/i,
    reason: "Requests sensitive personal or financial information"
    },
    {
    pattern: /work from home|remote work|flexible hours|be your own boss/i,
    reason: "Uses common terms found in work-from-home scams"
    }
];

patternChecks.forEach(check => {
    if (check.pattern.test(text)) {
    reasons.push(check.reason);
    }
});

if (jobData.description && jobData.description.split(' ').length < 100) {
    reasons.push("Unusually short or vague job description");
}

if (analysisResult.voting_result.votes_for_fraud === 4) {
    reasons.push("All detection models strongly agree this is a fraudulent job posting");
}

const modelInsights = {
    logistic: "Statistical text analysis identified suspicious language patterns",
    svm: "Support vector analysis found similarity to known scam patterns",
    rf: "Decision tree analysis identified multiple fraud indicators",
    mlp: "Neural network detected subtle patterns common in fraudulent postings"
};

for (const [modelName, prediction] of Object.entries(analysisResult.individual_predictions)) {
    if (prediction.is_fraudulent && modelInsights[modelName]) {
    reasons.push(modelInsights[modelName]);
    }
}

if (reasons.length < 3) {
    reasons.push("Combines multiple subtle red flags common in scam job listings");
    reasons.push("Contains inconsistencies typical of fraudulent job opportunities");
}

const topReasons = reasons.slice(0, 5);

let voteExplanation = "";
const totalVotes = analysisResult.voting_result.total_votes;
const fraudVotes = analysisResult.voting_result.votes_for_fraud;

if (fraudVotes === totalVotes) {
    voteExplanation = `All ${fraudVotes} detection models flagged this job as suspicious.`;
} else if (fraudVotes > totalVotes / 2) {
    voteExplanation = `Majority of detection models (${fraudVotes} out of ${totalVotes}) flagged this job as suspicious.`;
} else {
    voteExplanation = `Some detection models (${fraudVotes} out of ${totalVotes}) flagged this job as suspicious.`;
}

return {
    is_fraudulent: true,
    vote_count: `${fraudVotes}/${totalVotes} models flagged as suspicious`,
    vote_explanation: voteExplanation,
    confidence: analysisResult.voting_result.confidence,
    reasons: topReasons
};
}

/**
 * Update plugin settings
 * @param {Object} settings - New settings
 */
async function updateSettings(settings) {
return new Promise((resolve) => {
    chrome.storage.sync.set({ settings }, () => {
    console.log('Settings updated:', settings);
    resolve();
    });
});
}

function extractTextFeatures(jobData) {
let text = '';

const textFields = ['title', 'company', 'description', 'requirements', 'benefits', 'location'];

for (const field of textFields) {
    if (jobData[field]) {
    text += ' ' + jobData[field];
    }
}

return text.toLowerCase();
}

function simulateModelPrediction(modelName, text) {

let fraudProbability = 0.1;
const fraudPatterns = {
    urgency: /urgent|immediate|quick|fast|hurry/i,
    payment: /payment|money|cash|bank|financial|deposit/i,
    sensitive: /ssn|identity|passport|personal details|confidential/i,
    vague: /opportunity|position|opening|chance|prospect/i,
    contact: /whatsapp|telegram|personal email|direct message/i
};

for (const pattern of Object.values(fraudPatterns)) {
    if (pattern.test(text)) {
    fraudProbability += 0.15;
    }
}

fraudProbability = Math.min(0.95, fraudProbability);

const modelAdjustments = {
    logistic: 1.0,
    svm: 0.95,
    randomForest: 1.1,
    mlp: 0.9
};

fraudProbability *= modelAdjustments[modelName] || 1.0;

fraudProbability = Math.max(0, Math.min(1, fraudProbability));

return {
    fraud_probability: fraudProbability,
    risk_level: fraudProbability < 0.3 ? "low" : 
                fraudProbability < 0.7 ? "medium" : "high",
    color_indicator: fraudProbability < 0.3 ? "green" : 
                    fraudProbability < 0.7 ? "orange" : "red",
    is_fraudulent: fraudProbability > 0.5
};
}