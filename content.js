/**
 * PhishGuard AI - Content Script
 * This script is injected into the active web page to extract necessary data for analysis.
 */

(() => {
    // 1. Extract data from the DOM
    const pageData = {
        url: window.location.href,
        page_title: document.title,
        meta_description: document.querySelector('meta[name="description"]')?.content || '',
        visible_text: document.body.innerText || '',
        input_fields: [],
        brand_indicators: ''
    };

    // 2. Find all input fields and their types
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        // Add type if it's not a generic one like 'submit' or 'hidden'
        if (input.type && !['submit', 'hidden', 'button', 'checkbox', 'radio'].includes(input.type)) {
            pageData.input_fields.push(input.type.toLowerCase());
        } else if (input.name) { // Also check the name attribute for clues
             pageData.input_fields.push(input.name.toLowerCase());
        }
    });
    // Remove duplicates
    pageData.input_fields = [...new Set(pageData.input_fields)];


    // 3. Find brand indicators (simple heuristic)
    // Look for words like "logo" in image alt attributes
    const images = document.querySelectorAll('img');
    for (const img of images) {
        if (img.alt && img.alt.toLowerCase().includes('logo')) {
            pageData.brand_indicators = img.alt;
            break; // Found one, stop searching
        }
    }

    // If no logo found, check for a prominent brand name in the title
    if (!pageData.brand_indicators && document.title) {
        const commonBrands = ["Google", "Microsoft", "Apple", "PayPal", "Amazon", "Facebook"];
        for (const brand of commonBrands) {
            if (document.title.includes(brand)) {
                pageData.brand_indicators = brand;
                break;
            }
        }
    }


    // 4. Send the extracted data to the background script
    chrome.runtime.sendMessage({ type: "PAGE_DATA", data: pageData });

})();
