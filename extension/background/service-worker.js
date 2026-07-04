import { riskCheck, sessionHeartbeat, sessionStart, verify } from "../src/api.js";

const HEARTBEAT_ALARM = "trustpulse-heartbeat";
const REVERIFY_ALARM = "trustpulse-reverify";
// ~24s, comfortably under the backend's 60s idle window (IDLE_MAX_SECONDS in
// trust_engine.py). Chrome clamps chrome.alarms to a 1-minute floor for
// *packed* extensions, but relaxes that for unpacked/dev-mode ones, which is
// how this extension is loaded per the project's setup instructions.
const HEARTBEAT_PERIOD_MINUTES = 0.4;

const DEFAULT_SETTINGS = {
  reverifyIntervalMinutes: 2,
  protectedSites: [],
};

async function getState() {
  const { state } = await chrome.storage.local.get("state");
  return state || { cardId: null, sessionId: null, trustScore: null, flag: "none", lastReason: null };
}

async function setState(patch) {
  const state = await getState();
  const next = { ...state, ...patch };
  await chrome.storage.local.set({ state: next });
  await updateBadge(next);
  return next;
}

async function getSettings() {
  const { settings } = await chrome.storage.local.get("settings");
  return { ...DEFAULT_SETTINGS, ...(settings || {}) };
}

async function setSettings(patch) {
  const settings = await getSettings();
  const next = { ...settings, ...patch };
  await chrome.storage.local.set({ settings: next });
  await syncProtectedSiteContentScripts(next.protectedSites);
  return next;
}

async function updateBadge(state) {
  if (state.trustScore == null) {
    chrome.action.setBadgeText({ text: "" });
    return;
  }
  const score = state.trustScore;
  const color = score >= 60 ? "#16a34a" : score >= 35 ? "#d97706" : "#dc2626";
  chrome.action.setBadgeBackgroundColor({ color });
  chrome.action.setBadgeText({ text: String(Math.round(score)) });
}

async function syncProtectedSiteContentScripts(protectedSites) {
  const existing = await chrome.scripting.getRegisteredContentScripts({ ids: ["site-monitor"] });
  if (existing.length) {
    await chrome.scripting.unregisterContentScripts({ ids: ["site-monitor"] });
  }
  if (!protectedSites || protectedSites.length === 0) return;

  await chrome.scripting.registerContentScripts([
    {
      id: "site-monitor",
      matches: protectedSites.map((origin) => `${origin.replace(/\/$/, "")}/*`),
      js: ["content-scripts/site-monitor.js"],
      runAt: "document_idle",
    },
  ]);
}

async function captureFromOffscreen() {
  const existing = await chrome.offscreen.hasDocument();
  if (!existing) {
    await chrome.offscreen.createDocument({
      url: "offscreen/offscreen.html",
      reasons: ["USER_MEDIA"],
      justification: "Periodic webcam capture for continuous face re-verification.",
    });
  }
  return chrome.runtime.sendMessage({ type: "OFFSCREEN_CAPTURE" });
}

/** ensureStream() in offscreen.js deliberately keeps the camera stream alive
 * across reverify cycles rather than reopening it every time — but that
 * means it has to be torn down explicitly when a session ends, or the
 * camera indicator stays on indefinitely with nothing left needing it. */
async function releaseOffscreenCamera() {
  const existing = await chrome.offscreen.hasDocument();
  if (!existing) return;
  try {
    await chrome.runtime.sendMessage({ type: "OFFSCREEN_STOP" });
  } catch (err) {
    // Document may already be gone/unresponsive — closeDocument below still
    // releases any tracks it held, since that destroys its whole context.
  }
  await chrome.offscreen.closeDocument();
}

async function runHeartbeat() {
  const state = await getState();
  if (!state.sessionId) return;
  try {
    const result = await sessionHeartbeat(state.sessionId);
    await setState({ trustScore: result.trust_score, flag: result.flag, lastReason: result.latest_reason });
    if (result.flag === "reverify") {
      await runReverify();
    }
  } catch (err) {
    chrome.alarms.clear(HEARTBEAT_ALARM);
    chrome.alarms.clear(REVERIFY_ALARM);
    await releaseOffscreenCamera();
    await setState({ cardId: null, sessionId: null, trustScore: null, flag: "none", lastReason: "session_expired" });
  }
}

async function runReverify() {
  const state = await getState();
  if (!state.cardId) return;
  try {
    const capture = await captureFromOffscreen();
    if (!capture?.blob) return;
    const result = await verify(state.cardId, capture.blob);
    if (result.result !== "success") {
      await setState({ lastReason: result.reason || "reverify_failed" });
    }
  } catch (err) {
    // Camera unavailable or verify failed — heartbeat continues to reflect risk.
  }
}

chrome.runtime.onInstalled.addListener(async () => {
  await setSettings({});
  chrome.alarms.create(HEARTBEAT_ALARM, { periodInMinutes: HEARTBEAT_PERIOD_MINUTES });
});

chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === HEARTBEAT_ALARM) await runHeartbeat();
  if (alarm.name === REVERIFY_ALARM) await runReverify();
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    switch (message.type) {
      case "GET_STATE":
        sendResponse({ state: await getState(), settings: await getSettings() });
        return;

      case "START_SESSION": {
        const result = await sessionStart(message.cardId);
        const next = await setState({
          cardId: message.cardId,
          sessionId: result.session_id,
          trustScore: result.trust_score,
          flag: "none",
          lastReason: "session_start",
        });
        chrome.alarms.create(HEARTBEAT_ALARM, { periodInMinutes: HEARTBEAT_PERIOD_MINUTES });
        sendResponse({ state: next });
        return;
      }

      case "STOP_SESSION": {
        chrome.alarms.clear(HEARTBEAT_ALARM);
        chrome.alarms.clear(REVERIFY_ALARM);
        await releaseOffscreenCamera();
        const next = await setState({ cardId: null, sessionId: null, trustScore: null, flag: "none", lastReason: null });
        sendResponse({ state: next });
        return;
      }

      case "UPDATE_SETTINGS": {
        const settings = await setSettings(message.settings);
        chrome.alarms.create(REVERIFY_ALARM, { periodInMinutes: settings.reverifyIntervalMinutes });
        sendResponse({ settings });
        return;
      }

      case "PAGE_RISK_CHECK": {
        try {
          const result = await riskCheck(message.url);
          sendResponse({ result });
        } catch (err) {
          sendResponse({ error: String(err) });
        }
        return;
      }

      default:
        sendResponse({ error: "unknown_message_type" });
    }
  })();
  return true; // keep the message channel open for the async response
});
