/**
 * ScamShield AI - In-Page Content Script
 * Displays a visible warning popup message directly in the browser
 * when visiting an inactive company or suspicious website.
 */

// Track if warning is already displayed on current page
let activeWarningOverlay = null;

/**
 * Listen for messages from background service worker
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message && message.type === "SCAMSHIELD_SHOW_WARNING") {
    displayInBrowserWarningPopup(message.result);
    sendResponse({ received: true });
  }
});

/**
 * On page load, ask background worker to verify the current page
 */
try {
  chrome.runtime.sendMessage(
    {
      type: "CHECK_CURRENT_PAGE",
      url: window.location.href,
      domain: window.location.hostname
    },
    (response) => {
      if (chrome.runtime.lastError) {
        // Background worker might be sleeping or reloading
        return;
      }
      if (response && response.found === true) {
        displayInBrowserWarningPopup(response);
      }
    }
  );
} catch (err) {
  console.debug("ScamShield content script init error:", err);
}

/**
 * Render the in-browser floating warning popup message
 */
function displayInBrowserWarningPopup(result) {
  if (!result || !result.found) return;

  // Prevent multiple overlays
  if (document.getElementById("scamshield-warning-overlay")) {
    return;
  }

  const overlay = document.createElement("div");
  overlay.id = "scamshield-warning-overlay";

  // 1. Header Bar (Red)
  const header = document.createElement("div");
  header.className = "scamshield-header";

  const title = document.createElement("div");
  title.className = "scamshield-header-title";
  title.textContent = "⚠ SCAMSHIELD WARNING";

  const closeBtn = document.createElement("button");
  closeBtn.className = "scamshield-close-btn";
  closeBtn.textContent = "✕";
  closeBtn.title = "Dismiss Warning";
  closeBtn.addEventListener("click", () => {
    overlay.remove();
  });

  header.appendChild(title);
  header.appendChild(closeBtn);

  // 2. Body
  const body = document.createElement("div");
  body.className = "scamshield-body";

  const alertBox = document.createElement("div");
  alertBox.className = "scamshield-alert-box";

  const domainEl = document.createElement("div");
  domainEl.className = "scamshield-domain-title";
  domainEl.textContent = result.domain || window.location.hostname;

  const reasonEl = document.createElement("div");
  reasonEl.className = "scamshield-reason";
  if (result.company_status === "Inactive") {
    reasonEl.textContent = result.reason || "This company is marked as INACTIVE in sample.xlsx. Website or entity may be defunct or unauthorized.";
  } else {
    reasonEl.textContent = result.reason || "Suspicious domain detected in ScamShield threat dataset.";
  }

  alertBox.appendChild(domainEl);
  alertBox.appendChild(reasonEl);

  const checklistEl = document.createElement("div");
  checklistEl.className = "scamshield-checklist";
  checklistEl.textContent = "Security Notice: Exercise extreme caution. Do not submit Passwords, OTPs, Banking info, or Payments on this website.";

  // 3. Actions Row
  const actionsRow = document.createElement("div");
  actionsRow.className = "scamshield-actions";

  const viewAnalysisBtn = document.createElement("button");
  viewAnalysisBtn.className = "scamshield-btn scamshield-btn-danger";
  viewAnalysisBtn.textContent = "View Full Analysis";
  viewAnalysisBtn.addEventListener("click", () => {
    const webUrl = result.web_url || "http://localhost:5000";
    const target = `${webUrl}/analyze?url=${encodeURIComponent(window.location.href)}`;
    window.open(target, "_blank");
  });

  const dismissBtn = document.createElement("button");
  dismissBtn.className = "scamshield-btn scamshield-btn-primary";
  dismissBtn.textContent = "Dismiss & Proceed";
  dismissBtn.addEventListener("click", () => {
    overlay.remove();
  });

  actionsRow.appendChild(viewAnalysisBtn);
  actionsRow.appendChild(dismissBtn);

  body.appendChild(alertBox);
  body.appendChild(checklistEl);
  body.appendChild(actionsRow);

  overlay.appendChild(header);
  overlay.appendChild(body);

  // Append safely to page DOM
  (document.body || document.documentElement).appendChild(overlay);
  activeWarningOverlay = overlay;
}
