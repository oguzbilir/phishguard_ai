/**
 * PhishGuard AI - Background Script (Service Worker)
 * This script handles the extension's core logic, including listening for events,
 * managing content scripts, and coordinating the analysis.
 */

// Import the analysis engine
try {
    importScripts('analysis.js');
} catch (e) {
    console.error(e);
}


// Listener for when a tab is updated (e.g., user navigates to a new URL)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // Check if the tab has finished loading and has a valid URL
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {
        // Inject the content script to extract page data
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: ['content.js']
        }).catch(err => console.error("Failed to inject content script:", err));
    }
});

// Listener for messages from the content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "PAGE_DATA") {
        if (sender.tab && sender.tab.id) {
            console.log(`Received page data from tab ${sender.tab.id}:`, message.data);

            // Analyze the received data
            const analysisResult = analyzePage(message.data);
            console.log(`Analysis result for tab ${sender.tab.id}:`, analysisResult);

            // Store the result using the tab ID as the key
            // This ensures the popup gets the correct data for the active tab
            chrome.storage.local.set({ [sender.tab.id]: analysisResult }, () => {
                console.log(`Analysis result for tab ${sender.tab.id} has been stored.`);

                // Update the extension icon based on the risk score
                updateIcon(sender.tab.id, analysisResult.risk_score);
            });
        }
    }
    // Return true to indicate that we will send a response asynchronously (optional)
    return true;
});

// Function to update the extension icon based on the risk score
function updateIcon(tabId, riskScore) {
    let iconPath;
    if (riskScore > 85) {
        iconPath = 'icons/icon_critical.png'; // Red for critical risk
    } else if (riskScore > 60) {
        iconPath = 'icons/icon_high.png'; // Orange for high risk
    } else if (riskScore > 30) {
        iconPath = 'icons/icon_medium.png'; // Yellow for medium risk
    } else {
        iconPath = 'icons/icon128.png'; // Default green/safe icon
    }

    chrome.action.setIcon({
        tabId: tabId,
        path: {
            "16": iconPath.replace('128', '16'),
            "48": iconPath.replace('128', '48'),
            "128": iconPath
        }
    }).catch(err => console.error("Failed to set icon:", err));;
}

// Clean up storage when a tab is closed
chrome.tabs.onRemoved.addListener((tabId) => {
    chrome.storage.local.remove(String(tabId), () => {
        console.log(`Cleared storage for closed tab ${tabId}`);
    });
});
