/**
 * ScamShield AI - Background Service Worker (Manifest V3)
 * Automatically monitors active tabs, queries the dataset backend,
 * triggers native desktop notifications and auto-popups in front of user
 * whenever an inactive company or suspicious website is visited.
 */

import { getEffectiveConfig, normalizeDomain } from './config.js';

// In-memory debounce / cooldown caches
const recentChecks = new Map();
const recentPopups = new Map();
const CHECK_COOLDOWN_MS = 6000;
const POPUP_COOLDOWN_MS = 12000; // 12 seconds cooldown per domain for window auto-popup

/**
 * Handle tab activation (user switches tabs)
 */
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    if (tab && tab.url) {
      await processTabUrl(activeInfo.tabId, tab.url);
    }
  } catch (err) {
    console.debug("onActivated tab get error:", err);
  }
});

/**
 * Handle tab updates (page load completes)
 */
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    await processTabUrl(tabId, tab.url);
  }
});

/**
 * Handle extension installation/update
 */
chrome.runtime.onInstalled.addListener(async () => {
  console.log("ScamShield AI extension installed.");
  const data = await chrome.storage.local.get(["isPaused"]);
  if (data.isPaused === undefined) {
    await chrome.storage.local.set({ isPaused: false });
  }
});

/**
 * Listen for storage changes (e.g. pause/resume toggles)
 */
chrome.storage.onChanged.addListener((changes, areaName) => {
  if (areaName === "local" && changes.isPaused) {
    const paused = Boolean(changes.isPaused.newValue);
    if (paused) {
      chrome.action.setBadgeText({ text: "⏸" });
      chrome.action.setBadgeBackgroundColor({ color: "#f59e0b" });
    } else {
      chrome.action.setBadgeText({ text: "" });
      chrome.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
        if (tabs[0] && tabs[0].url) {
          processTabUrl(tabs[0].id, tabs[0].url, true);
        }
      });
    }
  }
});

/**
 * Listen for messages from content scripts (in-page checking)
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "CHECK_CURRENT_PAGE") {
    handlePageCheck(request.url, request.domain).then((res) => {
      sendResponse(res);
      if (res && res.found && sender.tab && sender.tab.id) {
        triggerAutomaticWarning(request.domain, request.url, res);
      }
    });
    return true; // Keep channel open for async response
  }
});

/**
 * Process a Tab URL: Normalize, Check Backend, Cache Result, Update Badge, Trigger Auto Popup
 */
async function processTabUrl(tabId, rawUrl, force = false) {
  const storageData = await chrome.storage.local.get(["isPaused"]);
  if (storageData.isPaused) {
    chrome.action.setBadgeText({ text: "⏸", tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#f59e0b", tabId });
    chrome.action.setTitle({ title: "ScamShield AI: Checking Paused", tabId });
    return;
  }

  const domain = normalizeDomain(rawUrl);

  // Skip internal system schemes
  if (!domain) {
    chrome.action.setBadgeText({ text: "", tabId });
    chrome.action.setTitle({ title: "ScamShield AI: Non-web page", tabId });
    return;
  }

  const result = await handlePageCheck(rawUrl, domain, force);

  if (result) {
    updateBadge(tabId, result);

    // If website is INACTIVE or SUSPICIOUS -> AUTOMATICALLY POP UP IN FRONT OF USER!
    if (result.found === true) {
      // 1. Notify in-page content script
      notifyTabToShowWarning(tabId, result);

      // 2. Automatically launch native Desktop Notification and front-most popup window!
      triggerAutomaticWarning(domain, rawUrl, result);
    }
  }
}

/**
 * Query Backend or Cache for a given Domain / URL
 */
async function handlePageCheck(rawUrl, domain, force = false) {
  if (!domain) {
    domain = normalizeDomain(rawUrl);
  }
  if (!domain) return null;

  const storageData = await chrome.storage.local.get(["isPaused"]);
  if (storageData.isPaused) return null;

  const now = Date.now();
  const lastCheck = recentChecks.get(domain);
  if (!force && lastCheck && (now - lastCheck.timestamp < CHECK_COOLDOWN_MS)) {
    return lastCheck.result;
  }

  try {
    const config = await getEffectiveConfig();
    const payload = {
      url: rawUrl || `https://${domain}`,
      domain: domain
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
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    data.web_url = config.SCAMSHIELD_WEB_URL;

    // Cache in memory & storage
    recentChecks.set(domain, { timestamp: now, result: data });
    const cacheKey = `result_${domain}`;
    await chrome.storage.local.set({
      [cacheKey]: data,
      latest_active_domain: domain,
      latest_active_result: data
    });

    return data;
  } catch (err) {
    console.warn(`ScamShield background check failed for ${domain}:`, err);
    return null;
  }
}

/**
 * Automatically pop up warning in front of user:
 * 1. Native Desktop Notification (in Windows notification area)
 * 2. Focused Chrome popup window (in front of all browser tabs)
 */
function triggerAutomaticWarning(domain, rawUrl, result) {
  const now = Date.now();
  const lastPopup = recentPopups.get(domain);
  if (lastPopup && (now - lastPopup < POPUP_COOLDOWN_MS)) {
    return;
  }
  recentPopups.set(domain, now);

  const isInactive = result.company_status === "Inactive";

  // 1. Native Desktop Notification (pops up in Windows bottom-right)
  try {
    if (chrome.notifications && chrome.notifications.create) {
      const titleText = isInactive
        ? "⚠ SCAMSHIELD: INACTIVE WEBSITE DETECTED!"
        : "⚠ SCAMSHIELD WARNING: SUSPICIOUS WEBSITE!";

      const bodyText = isInactive
        ? `Domain ${domain} is marked as INACTIVE in dataset (sample.xlsx). Do NOT enter sensitive credentials or payments!`
        : `Domain ${domain} is flagged as high-risk in ScamShield threat dataset.`;

      chrome.notifications.create(`scamshield_alert_${domain}_${now}`, {
        type: "basic",
        iconUrl: "icons/icon128.png",
        title: titleText,
        message: bodyText,
        priority: 2,
        requireInteraction: true // Stays on screen until user dismisses or clicks
      });
    }
  } catch (err) {
    console.debug("Notification creation error:", err);
  }

  // 2. Focused popup window right in front of user
  try {
    if (chrome.windows && chrome.windows.create) {
      const popupUrl = chrome.runtime.getURL(
        `popup.html?auto=1&testUrl=${encodeURIComponent(rawUrl || `https://${domain}`)}`
      );
      chrome.windows.create({
        url: popupUrl,
        type: "popup",
        width: 360,
        height: 520,
        focused: true,
        top: 60,
        left: 60
      });
    }
  } catch (err) {
    console.debug("Window create error:", err);
  }
}

/**
 * Send message to tab content script to display in-page warning modal
 */
function notifyTabToShowWarning(tabId, result) {
  try {
    chrome.tabs.sendMessage(tabId, {
      type: "SCAMSHIELD_SHOW_WARNING",
      result: result
    }).catch(() => {
      // Content script may not be loaded yet or page restricted
    });
  } catch (err) {
    console.debug("Error sending warning message to tab:", err);
  }
}

/**
 * Handle notification clicks: open ScamShield Web Analysis
 */
chrome.notifications.onClicked.addListener((notificationId) => {
  getEffectiveConfig().then((config) => {
    let base = (config.SCAMSHIELD_WEB_URL || "http://127.0.0.1:8000").trim().replace(/\/+$/, "");
    const target = base.includes("#") ? base : `${base}/#/dashboard`;
    chrome.tabs.create({ url: target });
  });
});

/**
 * Update Action Badge and Title according to dataset verdict
 */
function updateBadge(tabId, result) {
  if (!result) {
    chrome.action.setBadgeText({ text: "", tabId });
    return;
  }

  if (result.found === true) {
    chrome.action.setBadgeText({ text: "WARN", tabId });
    chrome.action.setBadgeBackgroundColor({ color: "#dc2626", tabId });
    const risk = result.company_status === "Inactive" ? "INACTIVE" : (result.risk_level || "HIGH");
    chrome.action.setTitle({
      title: `⚠ SCAMSHIELD WARNING: ${risk} website detected`,
      tabId
    });
  } else {
    chrome.action.setBadgeText({ text: "", tabId });
    chrome.action.setTitle({
      title: "ScamShield AI: No threat match in dataset",
      tabId
    });
  }
}
