// Registered dynamically (see background/service-worker.js) only for sites
// the user has added under Options > Protected Sites — never runs on <all_urls>.
chrome.runtime.sendMessage({ type: "PAGE_RISK_CHECK", url: window.location.href });
