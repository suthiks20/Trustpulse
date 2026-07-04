import { API_BASE_URL } from "./config.js";

async function handle(res) {
  const body = await res.json().catch(() => ({ success: false, error: { message: `HTTP ${res.status}` } }));
  if (!res.ok || body.success === false) {
    throw new Error(body?.error?.message || `Request failed: ${res.status}`);
  }
  return body.data;
}

export async function enroll(name, dob, imageBlob) {
  const form = new FormData();
  form.append("name", name);
  form.append("dob", dob);
  form.append("image", imageBlob, "capture.jpg");
  const res = await fetch(`${API_BASE_URL}/enroll`, { method: "POST", body: form });
  return handle(res);
}

export async function verify(cardId, imageBlob) {
  const form = new FormData();
  form.append("card_id", cardId);
  form.append("image", imageBlob, "capture.jpg");
  const res = await fetch(`${API_BASE_URL}/verify`, { method: "POST", body: form });
  return handle(res);
}

export async function sessionStart(cardId) {
  const res = await fetch(`${API_BASE_URL}/session/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ card_id: cardId }),
  });
  return handle(res);
}

export async function sessionHeartbeat(sessionId) {
  const res = await fetch(`${API_BASE_URL}/session/heartbeat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  return handle(res);
}

export async function riskCheck(url, proceededDespiteWarning = null) {
  const res = await fetch(`${API_BASE_URL}/risk-check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, proceeded_despite_warning: proceededDespiteWarning }),
  });
  return handle(res);
}
