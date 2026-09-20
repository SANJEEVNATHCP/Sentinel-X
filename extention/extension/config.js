/**
 * ScamShield AI Extension - Central Configuration
 * Configurable endpoints and navigation targets
 */

export const DEFAULT_CONFIG = {
  // Base web application URL for user navigation
  SCAMSHIELD_WEB_URL: "http://127.0.0.1:8000",
  // Backend API endpoint for dataset checking
  SCAMSHIELD_API_URL: "http://127.0.0.1:8000/api/check-url",
};

/**
 * Retrieve current configuration, checking chrome.storage.local first
 * for runtime overrides, falling back to defaults.
 */
export async function getEffectiveConfig() {
  try {
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      const stored = await chrome.storage.local.get(["SCAMSHIELD_WEB_URL", "SCAMSHIELD_API_URL"]);
      let web = (stored.SCAMSHIELD_WEB_URL || DEFAULT_CONFIG.SCAMSHIELD_WEB_URL).trim().replace(/\/+$/, "");
      let api = (stored.SCAMSHIELD_API_URL || DEFAULT_CONFIG.SCAMSHIELD_API_URL).trim();
      if (!api.includes("/api/check-url")) {
        api = api.replace(/\/+$/, "") + "/api/check-url";
      }
      return {
        SCAMSHIELD_WEB_URL: web,
        SCAMSHIELD_API_URL: api,
      };
    }
  } catch (err) {
    console.warn("Storage access error, using default config:", err);
  }
  return { ...DEFAULT_CONFIG };
}

/**
 * Update custom configuration in chrome.storage.local
 */
export async function saveCustomConfig(customWebUrl, customApiUrl) {
  if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
    await chrome.storage.local.set({
      SCAMSHIELD_WEB_URL: (customWebUrl || DEFAULT_CONFIG.SCAMSHIELD_WEB_URL).trim().replace(/\/+$/, ""),
      SCAMSHIELD_API_URL: (customApiUrl || DEFAULT_CONFIG.SCAMSHIELD_API_URL).trim(),
    });
  }
}

/**
 * Extract and normalize domain from a full URL.
 * Removes leading 'www.', ports, and validates against non-web schemes.
 */
export function normalizeDomain(rawUrl) {
  if (!rawUrl || typeof rawUrl !== "string") {
    return "";
  }

  const trimmed = rawUrl.trim();

  // Ignore browser internal schemes
  if (
    trimmed.startsWith("chrome://") ||
    trimmed.startsWith("chrome-extension://") ||
    trimmed.startsWith("edge://") ||
    trimmed.startsWith("about:") ||
    trimmed.startsWith("file://") ||
    trimmed.startsWith("view-source:")
  ) {
    return "";
  }

  try {
    const parsed = new URL(trimmed);
    let hostname = parsed.hostname.toLowerCase();

    // Strip leading 'www.'
    if (hostname.startsWith("www.")) {
      hostname = hostname.slice(4);
    }

    return hostname;
  } catch {
    // If URL lacks scheme, try parsing with http://
    try {
      const parsed = new URL(`http://${trimmed}`);
      let hostname = parsed.hostname.toLowerCase();
      if (hostname.startsWith("www.")) {
        hostname = hostname.slice(4);
      }
      return hostname;
    } catch {
      return "";
    }
  }
}
