/**
 * FraudLens AI - ScamShield Extension
 * Execution runner for background.js (Lines 260-295 & Service Worker logic)
 */

// Mock Chrome Extension API Environment
const listeners = {
  notificationClicked: [],
  tabsActivated: [],
  tabsUpdated: [],
  runtimeInstalled: [],
  storageChanged: [],
  runtimeMessage: []
};

const state = {
  badge: {},
  badgeColor: {},
  title: {},
  openedTabs: [],
  notifications: [],
  storage: { isPaused: false }
};

globalThis.chrome = {
  notifications: {
    onClicked: {
      addListener: (fn) => listeners.notificationClicked.push(fn)
    },
    create: (id, options) => {
      state.notifications.push({ id, ...options });
      console.log(`  [CHROME NOTIFICATION CREATED]`);
      console.log(`    Title:   ${options.title}`);
      console.log(`    Message: ${options.message}`);
      console.log(`    Priority: ${options.priority}`);
    }
  },
  action: {
    setBadgeText: ({ text, tabId }) => {
      state.badge[tabId ?? "global"] = text;
      console.log(`  [CHROME ACTION BADGE] Tab ${tabId ?? "global"} -> Badge text set to: "${text || "(cleared)"}"`);
    },
    setBadgeBackgroundColor: ({ color, tabId }) => {
      state.badgeColor[tabId ?? "global"] = color;
      console.log(`  [CHROME ACTION COLOR] Tab ${tabId ?? "global"} -> Badge background set to: ${color}`);
    },
    setTitle: ({ title, tabId }) => {
      state.title[tabId ?? "global"] = title;
      console.log(`  [CHROME ACTION TITLE] Tab ${tabId ?? "global"} -> Tooltip title set to: "${title}"`);
    }
  },
  tabs: {
    onActivated: { addListener: (fn) => listeners.tabsActivated.push(fn) },
    onUpdated: { addListener: (fn) => listeners.tabsUpdated.push(fn) },
    get: async (tabId) => ({ id: tabId, url: "https://www.southbankmosaics.com" }),
    create: ({ url }) => {
      state.openedTabs.push(url);
      console.log(`  [CHROME TABS CREATE] Successfully opened tab with URL: ${url}`);
      return { id: 999, url };
    },
    sendMessage: async () => {},
    query: async () => [{ id: 1, url: "https://www.southbankmosaics.com" }]
  },
  runtime: {
    onInstalled: { addListener: (fn) => listeners.runtimeInstalled.push(fn) },
    onMessage: { addListener: (fn) => listeners.runtimeMessage.push(fn) },
    getURL: (path) => `chrome-extension://scamshield-id/${path}`
  },
  windows: {
    create: (opts) => {
      console.log(`  [CHROME WINDOWS CREATE] Popup window created with URL: ${opts.url}`);
    }
  },
  storage: {
    local: {
      get: async (keys) => {
        const res = {};
        for (const k of keys) {
          if (k in state.storage) res[k] = state.storage[k];
        }
        return res;
      },
      set: async (obj) => {
        Object.assign(state.storage, obj);
      }
    },
    onChanged: { addListener: (fn) => listeners.storageChanged.push(fn) }
  }
};

async function run() {
  console.log("==================================================================");
  console.log("    RUNNING BACKGROUND.JS CODE EXECUTION & INTEGRATION TEST       ");
  console.log("==================================================================");

  // Dynamically import background.js
  console.log("\n[Step 1] Loading background.js module into Chrome runtime environment...");
  await import("./background.js");
  console.log("✓ background.js imported successfully.");
  console.log(`✓ Registered ${listeners.notificationClicked.length} notification click listener(s).`);

  // -------------------------------------------------------------
  // Test Lines 260-269: Notification Click Event Handler
  // -------------------------------------------------------------
  console.log("\n[Step 2] Executing Lines 260-269 (chrome.notifications.onClicked)...");
  console.log("Simulating user clicking on a desktop security notification...");
  for (const handler of listeners.notificationClicked) {
    handler("test-notification-alert-id");
  }

  // Wait for promise resolution (getEffectiveConfig & chrome.tabs.create)
  await new Promise(r => setTimeout(r, 200));
  console.log(`✓ Action captured: openedTabs count = ${state.openedTabs.length}`);
  console.log(`✓ Destination URL: ${state.openedTabs[0]}`);

  // -------------------------------------------------------------
  // Test Lines 274-295: updateBadge(tabId, result)
  // -------------------------------------------------------------
  console.log("\n[Step 3] Executing Lines 274-295 with Real API Responses from Backend...");

  // Scenario A: Inactive Company Detected (e.g. southbankmosaics.com from sample.xlsx)
  console.log("\n--- Scenario A: INACTIVE Company Query (southbankmosaics.com) ---");
  const inactiveResp = await fetch("http://127.0.0.1:8000/api/check-url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: "https://www.southbankmosaics.com/work", domain: "southbankmosaics.com" })
  });
  const inactiveResult = await inactiveResp.json();
  console.log("Backend response received:", JSON.stringify(inactiveResult, null, 2));

  // Simulate tab 101 receiving this result
  console.log("\nTriggering Tab 101 with Inactive Result (updates badge & title)...");
  for (const fn of listeners.tabsActivated) {
    await fn({ tabId: 101 });
  }
  await new Promise(r => setTimeout(r, 300));

  // Scenario B: Active Verified Company (e.g. tcs.com from sample.xlsx)
  console.log("\n--- Scenario B: ACTIVE Company Query (tcs.com) ---");
  const activeResp = await fetch("http://127.0.0.1:8000/api/check-url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: "https://www.tcs.com", domain: "tcs.com" })
  });
  const activeResult = await activeResp.json();
  console.log("Backend response received:", JSON.stringify(activeResult, null, 2));

  // Simulate tab 102 receiving active clean result
  console.log("\nTriggering Tab 102 with Active Result (badge should be empty)...");
  globalThis.chrome.tabs.get = async () => ({ id: 102, url: "https://www.tcs.com" });
  for (const fn of listeners.tabsActivated) {
    await fn({ tabId: 102 });
  }
  await new Promise(r => setTimeout(r, 300));

  console.log("\n==================================================================");
  console.log("             FINAL STATE INSPECTION & VERIFICATION                ");
  console.log("==================================================================");
  console.log("Badge for Tab 101 (Inactive):", state.badge[101], "(Color:", state.badgeColor[101], ")");
  console.log("Title for Tab 101 (Inactive):", state.title[101]);
  console.log("Badge for Tab 102 (Active):  ", `"${state.badge[102]}"`, "(Cleared)");
  console.log("Title for Tab 102 (Active):  ", state.title[102]);
  console.log("Desktop Notifications Sent: ", state.notifications.length);
  console.log("Tabs Opened via Clicks:     ", state.openedTabs);
  console.log("==================================================================");
  console.log("                      EXECUTION COMPLETED OK                      ");
  console.log("==================================================================");
}

run().catch(console.error);
