// No camera code lives here anymore — see capture/capture.js and the comment
// at the top of that file for why (the action popup cannot reliably host
// getUserMedia). This file only launches that window and renders session state.

import { riskCheck } from "../src/api.js";

const $ = (id) => document.getElementById(id);

const CAPTURE_URL = chrome.runtime.getURL("capture/capture.html");

function setStatus(text, isError = false) {
  const el = $("status-message");
  el.textContent = text;
  el.style.color = isError ? "#dc2626" : "#111827";
}

function scoreClass(score) {
  if (score >= 60) return "green";
  if (score >= 35) return "amber";
  return "red";
}

function renderState(state) {
  const hasSession = Boolean(state.sessionId);
  $("active-session").classList.toggle("hidden", !hasSession);
  $("no-session").classList.toggle("hidden", hasSession);

  if (!hasSession) return;

  $("active-card-id").textContent = state.cardId;
  const badge = $("score-badge");
  const score = state.trustScore ?? 0;
  badge.textContent = Math.round(score);
  badge.className = `score-badge ${scoreClass(score)}`;
  $("flag-text").textContent = state.flag === "none" ? "Healthy" : state.flag;

  const banner = $("warning-banner");
  if (state.flag !== "none") {
    banner.textContent =
      state.flag === "reverify"
        ? "Trust score dropped — re-verification in progress."
        : "Trust score is low. Increased checks are active.";
    banner.classList.remove("hidden");
  } else {
    banner.classList.add("hidden");
  }
}

async function refreshState() {
  const { state } = await chrome.runtime.sendMessage({ type: "GET_STATE" });
  renderState(state);
}

/** Opens capture.html in a real top-level window (not the action popup), or
 * focuses it if one is already open — chrome.windows.create with
 * type:"popup" is a normal window as far as getUserMedia is concerned, it
 * just has no tab strip/toolbar chrome. */
async function openCaptureWindow(mode) {
  const existingWindows = await chrome.windows.getAll({ populate: true });
  for (const win of existingWindows) {
    const match = win.tabs?.find((t) => t.url?.startsWith(CAPTURE_URL));
    if (match) {
      await chrome.windows.update(win.id, { focused: true });
      return;
    }
  }

  await chrome.windows.create({
    url: `${CAPTURE_URL}?mode=${mode}`,
    type: "popup",
    width: 420,
    height: 680,
    focused: true,
  });
}

function setLauncherButtonsEnabled(enabled) {
  $("open-login-btn").disabled = !enabled;
  $("open-enroll-btn").disabled = !enabled;
}

async function getActiveTabUrl() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab?.url || null;
}

function showRiskDialog(url, result) {
  $("risk-dialog-score").textContent = Math.round(result.risk_score);
  $("risk-dialog-reason").textContent = result.explanation;
  $("risk-dialog-overlay").classList.remove("hidden");

  return new Promise((resolve) => {
    const cancelBtn = $("risk-cancel-btn");
    const proceedBtn = $("risk-proceed-btn");

    function cleanup() {
      cancelBtn.removeEventListener("click", onCancel);
      proceedBtn.removeEventListener("click", onProceed);
      $("risk-dialog-overlay").classList.add("hidden");
    }

    async function onCancel() {
      cleanup();
      try {
        await riskCheck(url, false);
      } catch (err) {
        // Logging the decision is best-effort — the user's choice to cancel
        // still applies locally even if this particular call fails.
      }
      resolve(false);
    }

    async function onProceed() {
      cleanup();
      try {
        await riskCheck(url, true);
      } catch (err) {
        // Same as above — proceed locally regardless of logging success.
      }
      resolve(true);
    }

    cancelBtn.addEventListener("click", onCancel);
    proceedBtn.addEventListener("click", onProceed);
  });
}

/** Runs on every popup open: checks the active tab's site risk before the
 * user can start a login/enroll flow at all. Low-risk sites are unaffected
 * (buttons just enable immediately, no dialog) — this only ever adds a step
 * for sites that are actually flagged, and even then it's a confirmation,
 * never a hard block. */
async function runSiteRiskGate() {
  const url = await getActiveTabUrl();
  if (!url || !url.startsWith("http")) {
    setLauncherButtonsEnabled(true);
    return;
  }

  let result;
  try {
    result = await riskCheck(url);
  } catch (err) {
    // Backend unreachable or check failed — don't lock the user out over a
    // check we couldn't even complete.
    setLauncherButtonsEnabled(true);
    return;
  }

  if (!result.is_high_risk) {
    setLauncherButtonsEnabled(true);
    return;
  }

  setStatus("");
  const proceeded = await showRiskDialog(url, result);
  if (proceeded) {
    setLauncherButtonsEnabled(true);
  } else {
    setLauncherButtonsEnabled(false);
    setStatus("Login is disabled for this site. Reopen the popup to re-check.", true);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  $("open-login-btn").addEventListener("click", () => openCaptureWindow("login"));
  $("open-enroll-btn").addEventListener("click", () => openCaptureWindow("enroll"));
  $("end-session-btn").addEventListener("click", async () => {
    const { state } = await chrome.runtime.sendMessage({ type: "STOP_SESSION" });
    renderState(state);
  });
  $("options-btn").addEventListener("click", () => chrome.runtime.openOptionsPage());

  try {
    await refreshState();
  } catch (err) {
    setStatus("Could not load session state.", true);
  }

  const { state } = await chrome.runtime.sendMessage({ type: "GET_STATE" });
  if (!state.sessionId) {
    await runSiteRiskGate();
  }
});
