/**
 * PhishGuard AI - Popup Script
 * This script runs when the user clicks the extension icon.
 * It retrieves the analysis result for the active tab from storage and displays it.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Query for the active tab
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0];
        if (activeTab && activeTab.id) {
            const tabId = activeTab.id;

            // Retrieve the analysis result for this tab from local storage
            chrome.storage.local.get([String(tabId)], (result) => {
                const analysisResult = result[String(tabId)];

                if (analysisResult) {
                    // Update the UI with the analysis result
                    updateUI(analysisResult);
                } else {
                    // Data not found, display a waiting message
                    displayWaitingMessage();
                }
            });
        }
    });
});

function updateUI(result) {
    const riskScoreEl = document.getElementById('risk-score');
    const scoreCircleEl = document.getElementById('score-circle');
    const verdictEl = document.getElementById('verdict');
    const summaryEl = document.getElementById('analysis-summary');
    const breakdownListEl = document.getElementById('detailed-breakdown');
    const recommendationEl = document.getElementById('recommendation');
    const logoEl = document.getElementById('logo');

    // Update score and verdict
    riskScoreEl.textContent = result.risk_score;
    verdictEl.textContent = result.verdict;
    summaryEl.textContent = result.analysis_summary;
    recommendationEl.textContent = result.recommendation;

    // Update score circle color based on risk
    scoreCircleEl.className = 'score-circle'; // Reset classes
    if (result.risk_score > 85) {
        scoreCircleEl.classList.add('critical');
    } else if (result.risk_score > 60) {
        scoreCircleEl.classList.add('high');
    } else if (result.risk_score > 30) {
        scoreCircleEl.classList.add('medium');
    } else {
        scoreCircleEl.classList.add('low');
    }

    // Update detailed breakdown
    breakdownListEl.innerHTML = ''; // Clear previous entries
    for (const [key, value] of Object.entries(result.detailed_breakdown)) {
        const listItem = document.createElement('li');

        // Make the key more readable
        const readableKey = key.replace('_', ' ').replace('analysis', 'Analysis').replace(/\b\w/g, l => l.toUpperCase());

        listItem.innerHTML = `<strong>${readableKey}:</strong> (Score: ${value.score}) - <em>${value.reason}</em>`;
        breakdownListEl.appendChild(listItem);
    }

    // Also update the main logo based on risk
    logoEl.src = getIconPath(result.risk_score);
}

function displayWaitingMessage() {
    document.getElementById('verdict').textContent = 'Analiz bekleniyor...';
    document.getElementById('analysis-summary').textContent = 'Sayfa henüz tam olarak yüklenmemiş veya analiz edilmemiş olabilir. Lütfen bir an bekleyin.';
}

function getIconPath(riskScore) {
    if (riskScore > 85) return '../icons/icon_critical.png';
    if (riskScore > 60) return '../icons/icon_high.png';
    if (riskScore > 30) return '../icons/icon_medium.png';
    return '../icons/icon48.png'; // Default icon
}
