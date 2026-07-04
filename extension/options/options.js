const $ = (id) => document.getElementById(id);

function setStatus(text) {
  $("status").textContent = text;
  if (text) setTimeout(() => ($("status").textContent = ""), 2000);
}

function renderSites(sites) {
  const list = $("site-list");
  list.innerHTML = "";
  for (const origin of sites) {
    const li = document.createElement("li");
    const span = document.createElement("span");
    span.textContent = origin;
    const removeBtn = document.createElement("button");
    removeBtn.textContent = "Remove";
    removeBtn.addEventListener("click", () => removeSite(origin));
    li.append(span, removeBtn);
    list.appendChild(li);
  }
}

async function loadState() {
  const { state, settings } = await chrome.runtime.sendMessage({ type: "GET_STATE" });
  $("interval").value = settings.reverifyIntervalMinutes;
  renderSites(settings.protectedSites);
  $("session-info").textContent = state.sessionId
    ? `Card ${state.cardId} — session ${state.sessionId} — trust score ${state.trustScore ?? "--"}`
    : "No active session.";
}

async function saveInterval() {
  const minutes = Number($("interval").value) || 2;
  await chrome.runtime.sendMessage({
    type: "UPDATE_SETTINGS",
    settings: { reverifyIntervalMinutes: minutes },
  });
  setStatus("Saved");
}

async function addSite() {
  const input = $("new-site");
  let origin = input.value.trim();
  if (!origin) return;
  if (!origin.includes("://")) origin = `https://${origin}`;
  origin = new URL(origin).origin;

  const granted = await chrome.permissions.request({ origins: [`${origin}/*`] });
  if (!granted) {
    setStatus("Permission denied");
    return;
  }

  const { settings } = await chrome.runtime.sendMessage({ type: "GET_STATE" });
  const protectedSites = Array.from(new Set([...settings.protectedSites, origin]));
  await chrome.runtime.sendMessage({ type: "UPDATE_SETTINGS", settings: { protectedSites } });
  input.value = "";
  await loadState();
  setStatus("Site added");
}

async function removeSite(origin) {
  const { settings } = await chrome.runtime.sendMessage({ type: "GET_STATE" });
  const protectedSites = settings.protectedSites.filter((s) => s !== origin);
  await chrome.runtime.sendMessage({ type: "UPDATE_SETTINGS", settings: { protectedSites } });
  await chrome.permissions.remove({ origins: [`${origin}/*`] });
  await loadState();
  setStatus("Site removed");
}

async function revokeSession() {
  await chrome.runtime.sendMessage({ type: "STOP_SESSION" });
  await loadState();
  setStatus("Session revoked");
}

document.addEventListener("DOMContentLoaded", async () => {
  await loadState();
  $("interval").addEventListener("change", saveInterval);
  $("add-site-btn").addEventListener("click", addSite);
  $("revoke-btn").addEventListener("click", revokeSession);
});
