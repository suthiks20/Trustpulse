// Camera capture lives in this dedicated extension window instead of the
// action popup. Two reasons, both fatal to doing it in popup.html:
//
// 1. The action popup is a transient surface — when getUserMedia's permission
//    prompt appears, the popup loses activation and Chrome auto-dismisses the
//    request (NotAllowedError: "Permission dismissed"). A normal
//    chrome.windows.create({type:"popup"}) window is a real top-level window,
//    not the browserAction bubble, and does not have this problem.
// 2. Offscreen documents (used elsewhere in this extension for headless
//    periodic re-verify) cannot display a permission prompt at all — they can
//    only successfully call getUserMedia after permission was already granted
//    from a real page. This window is that first-grant surface.
//
// One camera stream is started once, on load, and reused across the
// Login/Enroll tabs (switching tabs only changes which form + capture action
// is active) — this avoids re-running getUserMedia repeatedly and the race
// conditions that come with it.

import { enroll, verify } from "../src/api.js";

const $ = (id) => document.getElementById(id);

let currentStream = null;
let cameraReady = false;

function log(...args) {
  console.log("[TrustPulse capture]", ...args);
}

function logError(context, err) {
  console.error(`[TrustPulse capture] ${context}:`, err);
}

function setStatus(text, isError = false) {
  const el = $("status-message");
  el.textContent = text;
  el.style.color = isError ? "#dc2626" : "#111827";
}

function setCameraStatus(text) {
  $("camera-status").textContent = text;
}

function setCaptureButtonsEnabled(enabled) {
  $("login-capture-btn").disabled = !enabled;
  $("enroll-capture-btn").disabled = !enabled;
}

function describeCameraError(err) {
  switch (err.name) {
    case "NotAllowedError":
    case "PermissionDeniedError":
      return "Camera permission was denied or dismissed. Click the camera icon in the address bar, allow access, and reopen this window.";
    case "NotFoundError":
    case "DevicesNotFoundError":
      return "No camera was found on this device.";
    case "NotReadableError":
    case "TrackStartError":
      return "The camera is already in use by another application.";
    case "OverconstrainedError":
      return "No camera satisfies the requested resolution.";
    default:
      return `Camera error: ${err.message || err}`;
  }
}

/** Starts the stream and does not resolve until a frame has actually decoded
 * (videoWidth/videoHeight > 0), so callers never draw from a black/blank
 * video onto the capture canvas. */
async function startCamera() {
  setCaptureButtonsEnabled(false);
  cameraReady = false;
  setCameraStatus("Requesting camera access…");

  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 } });
  } catch (err) {
    logError("getUserMedia failed", err);
    setCameraStatus(describeCameraError(err));
    throw err;
  }

  currentStream = stream;
  const video = $("video");
  video.srcObject = stream;

  try {
    await new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error("Camera timed out while starting.")), 8000);
      video.onloadedmetadata = () => {
        clearTimeout(timeout);
        video.play().then(resolve).catch(reject);
      };
    });
  } catch (err) {
    logError("video failed to start playing", err);
    setCameraStatus(err.message);
    throw err;
  }

  if (!video.videoWidth || !video.videoHeight) {
    const err = new Error("Camera stream started but produced no video frames.");
    logError("no video frames", err);
    setCameraStatus(err.message);
    throw err;
  }

  cameraReady = true;
  setCameraStatus("");
  setCaptureButtonsEnabled(true);
  log("camera ready", video.videoWidth, video.videoHeight);
}

function stopCamera() {
  cameraReady = false;
  if (currentStream) {
    currentStream.getTracks().forEach((t) => t.stop());
    currentStream = null;
  }
}

function captureBlob() {
  const video = $("video");
  const canvas = $("canvas");

  if (!cameraReady || !video.videoWidth || !video.videoHeight) {
    return Promise.reject(new Error("Camera isn't ready yet — wait for the preview before capturing."));
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);

  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error("Failed to capture a frame from the camera."));
    }, "image/jpeg", 0.9);
  });
}

function switchTab(tab) {
  $("tab-login").classList.toggle("active", tab === "login");
  $("tab-enroll").classList.toggle("active", tab === "enroll");
  $("login-panel").classList.toggle("hidden", tab !== "login");
  $("enroll-panel").classList.toggle("hidden", tab !== "enroll");
  setStatus("");
}

async function finishAndClose(message) {
  setStatus(message);
  setCaptureButtonsEnabled(false);
  stopCamera();
  setTimeout(() => window.close(), 900);
}

async function handleLogin() {
  const cardId = $("login-card-id").value.trim();
  if (!cardId) return setStatus("Enter a card ID", true);

  try {
    setStatus("Verifying…");
    setCaptureButtonsEnabled(false);
    const blob = await captureBlob();
    const result = await verify(cardId, blob);
    if (result.result !== "success") {
      setStatus(`Verification failed: ${result.reason || "no match"}`, true);
      setCaptureButtonsEnabled(true);
      return;
    }
    await chrome.runtime.sendMessage({ type: "START_SESSION", cardId });
    await finishAndClose("Login successful — closing…");
  } catch (err) {
    logError("login failed", err);
    setStatus(String(err.message || err), true);
    setCaptureButtonsEnabled(true);
  }
}

async function handleEnroll() {
  const name = $("enroll-name").value.trim();
  const dob = $("enroll-dob").value;
  if (!name || !dob) return setStatus("Fill in name and date of birth", true);

  try {
    setStatus("Enrolling…");
    setCaptureButtonsEnabled(false);
    const blob = await captureBlob();
    const result = await enroll(name, dob, blob);
    await chrome.runtime.sendMessage({ type: "START_SESSION", cardId: result.card_id });
    await finishAndClose(`Enrolled as ${result.card_id} — closing…`);
  } catch (err) {
    logError("enroll failed", err);
    setStatus(String(err.message || err), true);
    setCaptureButtonsEnabled(true);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const params = new URLSearchParams(window.location.search);
  const initialMode = params.get("mode") === "enroll" ? "enroll" : "login";
  switchTab(initialMode);

  $("tab-login").addEventListener("click", () => switchTab("login"));
  $("tab-enroll").addEventListener("click", () => switchTab("enroll"));
  $("login-capture-btn").addEventListener("click", handleLogin);
  $("enroll-capture-btn").addEventListener("click", handleEnroll);

  try {
    await startCamera();
  } catch (err) {
    // Already surfaced via setCameraStatus/logError inside startCamera.
  }
});

window.addEventListener("beforeunload", stopCamera);
window.addEventListener("unload", stopCamera);
