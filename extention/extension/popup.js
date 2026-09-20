/**
 * ScamShield AI - Popup Controller
 * Implements tab domain checking, pause/resume state,
 * error handling, and web navigation.
 */

import { getEffectiveConfig, saveCustomConfig, normalizeDomain, DEFAULT_CONFIG } from './config.js';

// Application State
let currentTab = null;
let currentDomain = "";
let currentFullUrl = "";
let isPaused = false;
let config = { ...DEFAULT_CONFIG };

// DOM Elements
const elements = {
  // Status Bar
  statusBar: document.getElementById("statusBar"),
  statusText: document.getElementById("statusText"),
  pauseBtn: document.getElementById("pauseToggleBtn"),

  // Website Card
  domainDisplay: document.getElementById("domainDisplay"),
  urlDisplay: document.getElementById("urlDisplay"),
  copyUrlBtn: document.getElementById("copyUrlBtn"),

  // State Containers
  stateChecking: document.getElementById("stateChecking"),
  stateWarning: document.getElementById("stateWarning"),
  stateNoMatch: document.getElementById("stateNoMatch"),
  stateError: document.getElementById("stateError"),
  statePaused: document.getElementById("statePaused"),
  stateNonWeb: document.getElementById("stateNonWeb"),

  // Warning Elements
  warningDomain: document.getElementById("warningDomain"),
  warningMatch: document.getElementById("warningMatch"),
  warningRiskLevel: document.getElementById("warningRiskLevel"),
  warningScoreRow: document.getElementById("warningScoreRow"),
  warningRiskScore: document.getElementById("warningRiskScore"),
  warningReason: document.getElementById("warningReason"),

  // Buttons
  viewAnalysisBtn: document.getElementById("viewAnalysisBtn"),
  scanCurrentBtn: document.getElementById("scanCurrentBtn"),
  retryScanBtn: document.getElementById("retryScanBtn"),
  openWebBtn: document.getElementById("openWebBtn"),

  // Settings Panel
  configToggleBtn: document.getElementById("configToggleBtn"),
  settingsPanel: document.getElementById("settingsPanel"),
  closeSettingsBtn: document.getElementById("closeSettingsBtn"),
  webUrlInput: document.getElementById("webUrlInput"),
  apiUrlInput: document.getElementById("apiUrlInput"),
  saveSettingsBtn: document.getElementById("saveSettingsBtn"),
  resetSettingsBtn: document.getElementById("resetSettingsBtn"),
};

/**
 * Initialize popup on load
 */
async function init() {
  // Load configuration
  config = await getEffectiveConfig();
  elements.webUrlInput.value = config.SCAMSHIELD_WEB_URL;
  elements.apiUrlInput.value = config.SCAMSHIELD_API_URL;

  // Load pause state from storage
  await loadPauseState();

  // Setup event listeners
  setupEventListeners();

  // Get active tab and run check
  await identifyCurrentTab();
}

/**
 * Setup UI Event Listeners
 */
function setupEventListeners() {
  // Pause / Resume Toggle
  elements.pauseBtn.addEventListener("click", togglePauseState);

  // Copy URL Button
  elements.copyUrlBtn.addEventListener("click", copyFullUrlToClipboard);

  // Manual Scan
  elements.scanCurrentBtn.addEventListener("click", () => {
    checkDomainAgainstBackend(true);
  });

  // Retry Button
  elements.retryScanBtn.addEventListener("click", () => {
    checkDomainAgainstBackend(true);
  });

  // Open ScamShield Web Application
  elements.openWebBtn.addEventListener("click", () => {
    let base = (config.SCAMSHIELD_WEB_URL || "http://127.0.0.1:8000").trim().replace(/\/+$/, "");
    const target = base.includes("#") ? base : `${base}/#/dashboard`;
    openUrlInNewTab(target);
  });

  // View Full Analysis Button
  elements.viewAnalysisBtn.addEventListener("click", () => {
    if (!currentFullUrl) return;
    const targetUrl = `${config.SCAMSHIELD_WEB_URL}/analyze?url=${encodeURIComponent(currentFullUrl)}`;
    openUrlInNewTab(targetUrl);
  });

  // Settings Panel Toggle
  elements.configToggleBtn.addEventListener("click", () => {
    elements.settingsPanel.classList.toggle("hidden");
  });

  elements.closeSettingsBtn.addEventListener("click", () => {
    elements.settingsPanel.classList.add("hidden");
  });

  elements.saveSettingsBtn.addEventListener("click", async () => {
    const web = elements.webUrlInput.value.trim() || DEFAULT_CONFIG.SCAMSHIELD_WEB_URL;
    const api = elements.apiUrlInput.value.trim() || DEFAULT_CONFIG.SCAMSHIELD_API_URL;
    await saveCustomConfig(web, api);
    config = { SCAMSHIELD_WEB_URL: web, SCAMSHIELD_API_URL: api };
    elements.settingsPanel.classList.add("hidden");
    // Re-check with new settings
    checkDomainAgainstBackend(true);
  });

  elements.resetSettingsBtn.addEventListener("click", async () => {
    await saveCustomConfig(DEFAULT_CONFIG.SCAMSHIELD_WEB_URL, DEFAULT_CONFIG.SCAMSHIELD_API_URL);
    config = { ...DEFAULT_CONFIG };
    elements.webUrlInput.value = config.SCAMSHIELD_WEB_URL;
    elements.apiUrlInput.value = config.SCAMSHIELD_API_URL;
    elements.settingsPanel.classList.add("hidden");
    checkDomainAgainstBackend(true);
  });
}

/**
 * Load Pause State from chrome.storage.local
 */
async function loadPauseState() {
  try {
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      const data = await chrome.storage.local.get(["isPaused"]);
      isPaused = Boolean(data.isPaused);
    }
  } catch (err) {
    console.warn("Could not read pause state:", err);
  }
  updatePauseUI();
}

/**
 * Toggle Pause/Resume and persist
 */
async function togglePauseState() {
  isPaused = !isPaused;
  try {
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      await chrome.storage.local.set({ isPaused });
    }
  } catch (err) {
    console.error("Failed to save pause state:", err);
  }
  updatePauseUI();

  if (!isPaused) {
    // If resumed, immediately verify current website
    checkDomainAgainstBackend();
  } else {
    showState("paused");
  }
}

/**
 * Update Pause button and status badge UI
 */
function updatePauseUI() {
  if (isPaused) {
    if (elements.statusBar) elements.statusBar.classList.add("paused");
    if (elements.statusText) elements.statusText.textContent = "Paused";
    if (elements.pauseBtn) elements.pauseBtn.textContent = "Resume";
  } else {
    if (elements.statusBar) elements.statusBar.classList.remove("paused");
    if (elements.statusText) elements.statusText.textContent = "Active";
    if (elements.pauseBtn) elements.pauseBtn.textContent = "Pause";
  }
}

/**
 * Identify Active Browser Tab
 */
async function identifyCurrentTab() {
  const urlParams = new URLSearchParams(window.location.search);
  const paramUrl = urlParams.get("testUrl");
  if (paramUrl) {
    currentFullUrl = paramUrl;
    currentDomain = normalizeDomain(paramUrl);
    displayTabInfo(currentFullUrl, currentDomain);
    if (!currentDomain) {
      showState("nonweb");
      return;
    }
    if (!isPaused) {
      await checkDomainAgainstBackend();
    } else {
      showState("paused");
    }
    return;
  }

  if (typeof chrome !== "undefined" && chrome.tabs && chrome.tabs.query) {
    try {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tabs && tabs.length > 0) {
        currentTab = tabs[0];
        currentFullUrl = currentTab.url || "";
        currentDomain = normalizeDomain(currentFullUrl);

        displayTabInfo(currentFullUrl, currentDomain);

        if (!currentDomain) {
          showState("nonweb");
          return;
        }

        // If paused, show paused state unless cached result is available
        if (isPaused) {
          showState("paused");
          return;
        }

        // Check cache first or check backend
        await checkDomainAgainstBackend();
        return;
      }
    } catch (err) {
      console.error("Error querying active tab:", err);
    }
  }

  // Fallback for demo or non-extension context
  handleLocalPreviewFallback();
}

/**
 * Fallback display for local preview/development
 */
function handleLocalPreviewFallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const testUrl = urlParams.get("testUrl");
  
  if (testUrl) {
    currentFullUrl = testUrl;
    currentDomain = normalizeDomain(testUrl);
  } else {
    currentFullUrl = "https://google-careers-example.xyz/internship/apply";
    currentDomain = "google-careers-example.xyz";
  }

  displayTabInfo(currentFullUrl, currentDomain);

  if (!currentDomain) {
    showState("nonweb");
    return;
  }

  if (!isPaused) {
    checkDomainAgainstBackend();
  } else {
    showState("paused");
  }
}

// Allow test harness to simulate tab changes via postMessage
window.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SIMULATE_TAB") {
    currentFullUrl = event.data.url || "";
    currentDomain = normalizeDomain(currentFullUrl);
    displayTabInfo(currentFullUrl, currentDomain);
    if (!currentDomain) {
      showState("nonweb");
    } else if (!isPaused) {
      checkDomainAgainstBackend(true);
    } else {
      showState("paused");
    }
  }
});

/**
 * Display Tab Info in Website Card
 */
function displayTabInfo(url, domain) {
  if (!domain) {
    elements.domainDisplay.textContent = "Internal / Local Page";
    elements.urlDisplay.textContent = url || "chrome://...";
    elements.copyUrlBtn.disabled = !url;
    return;
  }

  elements.domainDisplay.textContent = domain;
  elements.urlDisplay.textContent = url;
  elements.copyUrlBtn.disabled = false;
}

/**
 * Copy Full URL to Clipboard
 */
async function copyFullUrlToClipboard() {
  if (!currentFullUrl) return;
  try {
    await navigator.clipboard.writeText(currentFullUrl);
    const originalText = elements.copyUrlBtn.textContent;
    elements.copyUrlBtn.textContent = "Copied!";
    elements.copyUrlBtn.style.color = "#38bdf8";
    setTimeout(() => {
      elements.copyUrlBtn.textContent = originalText;
      elements.copyUrlBtn.style.color = "";
    }, 1500);
  } catch (err) {
    console.error("Failed to copy URL:", err);
  }
}

/**
 * Send Domain/URL to Backend API
 */
async function checkDomainAgainstBackend(isManual = false) {
  if (!currentDomain) {
    showState("nonweb");
    return;
  }

  // Check background cached result first if not a manual re-scan
  if (!isManual && typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    try {
      const cacheKey = `result_${currentDomain}`;
      const cachedData = await chrome.storage.local.get([cacheKey]);
      if (cachedData && cachedData[cacheKey]) {
        renderResult(cachedData[cacheKey]);
        return;
      }
    } catch (err) {
      console.warn("Cache lookup error:", err);
    }
  }

  showState("checking");

  try {
    const payload = {
      url: currentFullUrl,
      domain: currentDomain
    };

    let apiUrl = (config.SCAMSHIELD_API_URL || "http://127.0.0.1:8000/api/check-url").trim();
    if (!apiUrl.includes("/api/check-url")) {
      apiUrl = apiUrl.replace(/\/+$/, "") + "/api/check-url";
    }

    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Backend returned HTTP status ${response.status}`);
    }

    const data = await response.json();

    // Cache the result in storage for tab
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      const cacheKey = `result_${currentDomain}`;
      await chrome.storage.local.set({ [cacheKey]: data });
    }

    renderResult(data);
  } catch (err) {
    console.error("ScamShield backend check error:", err);
    showState("error");
  }
}

/**
 * Render Dataset Check Result
 */
function renderResult(result) {
  if (!result) {
    showState("error");
    return;
  }

  if (result.found === true) {
    // 1. Known Suspicious Match or INACTIVE Company in sample.xlsx
    elements.warningDomain.textContent = result.domain || currentDomain;

    if (result.company_status === "Inactive") {
      elements.warningMatch.textContent = "Inactive Company (sample.xlsx)";
      elements.warningRiskLevel.textContent = "HIGH (INACTIVE)";
    } else {
      elements.warningMatch.textContent = "Known suspicious domain";
      elements.warningRiskLevel.textContent = result.risk_level || "HIGH";
    }

    if (result.risk_score !== undefined && result.risk_score !== null) {
      elements.warningScoreRow.classList.remove("hidden");
      elements.warningRiskScore.textContent = `${result.risk_score}/100`;
    } else {
      elements.warningScoreRow.classList.add("hidden");
    }

    elements.warningReason.textContent = result.reason || "Domain found in ScamShield dataset.";
    showState("warning");
  } else {
    // 2. Verified Active or No Known Match
    const titleEl = document.querySelector("#stateNoMatch .neutral-title");
    const descEl = document.querySelector("#stateNoMatch .neutral-desc");
    const discEl = document.querySelector("#stateNoMatch .neutral-disclaimer");

    if (result.verified_active && result.company_name) {
      if (titleEl) titleEl.textContent = "VERIFIED ACTIVE COMPANY";
      if (descEl) descEl.textContent = `${result.company_name} is listed as ACTIVE in sample.xlsx.`;
      if (discEl) discEl.textContent = `CIN: ${result.cin || "N/A"}. Always verify site authenticity before providing credentials.`;
    } else {
      if (titleEl) titleEl.textContent = "NO KNOWN MATCH";
      if (descEl) descEl.textContent = "This domain was not found in the ScamShield dataset.";
      if (discEl) discEl.textContent = "No known match found. Always verify site authenticity before entering sensitive credentials.";
    }

    showState("nomatch");
  }
}

/**
 * Switch Active Display State
 */
function showState(state) {
  // Hide all state containers
  elements.stateChecking.classList.add("hidden");
  elements.stateWarning.classList.add("hidden");
  elements.stateNoMatch.classList.add("hidden");
  elements.stateError.classList.add("hidden");
  elements.statePaused.classList.add("hidden");
  elements.stateNonWeb.classList.add("hidden");

  // Reset conditional buttons
  elements.viewAnalysisBtn.classList.add("hidden");
  elements.retryScanBtn.classList.add("hidden");
  elements.scanCurrentBtn.classList.remove("hidden");

  switch (state) {
    case "checking":
      elements.stateChecking.classList.remove("hidden");
      elements.scanCurrentBtn.disabled = true;
      break;

    case "warning":
      elements.stateWarning.classList.remove("hidden");
      elements.viewAnalysisBtn.classList.remove("hidden");
      elements.scanCurrentBtn.disabled = false;
      break;

    case "nomatch":
      elements.stateNoMatch.classList.remove("hidden");
      elements.scanCurrentBtn.disabled = false;
      break;

    case "error":
      elements.stateError.classList.remove("hidden");
      elements.retryScanBtn.classList.remove("hidden");
      elements.scanCurrentBtn.classList.add("hidden");
      elements.scanCurrentBtn.disabled = false;
      break;

    case "paused":
      elements.statePaused.classList.remove("hidden");
      elements.scanCurrentBtn.disabled = false;
      break;

    case "nonweb":
      elements.stateNonWeb.classList.remove("hidden");
      elements.scanCurrentBtn.disabled = true;
      break;
  }
}

/**
 * Open external URL in a new tab
 */
function openUrlInNewTab(url) {
  if (!url) return;
  if (typeof chrome !== "undefined" && chrome.tabs && chrome.tabs.create) {
    chrome.tabs.create({ url });
  } else {
    window.open(url, "_blank");
  }
}

// Kick off initialization
document.addEventListener("DOMContentLoaded", init);
