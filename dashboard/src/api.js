const BASE_URL = "http://localhost:8000";

async function handle(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function enroll(name, dob, imageBlob) {
  const form = new FormData();
  form.append("name", name);
  form.append("dob", dob);
  form.append("image", imageBlob, "capture.jpg");
  const res = await fetch(`${BASE_URL}/enroll`, { method: "POST", body: form });
  return handle(res);
}

export async function verify(cardId, imageBlob) {
  const form = new FormData();
  form.append("card_id", cardId);
  form.append("image", imageBlob, "capture.jpg");
  const res = await fetch(`${BASE_URL}/verify`, { method: "POST", body: form });
  return handle(res);
}

export async function sessionStart(cardId) {
  const res = await fetch(`${BASE_URL}/session/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ card_id: cardId }),
  });
  return handle(res);
}

export async function sessionHeartbeat(sessionId) {
  const res = await fetch(`${BASE_URL}/session/heartbeat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  return handle(res);
}

export async function riskCheck(url) {
  const res = await fetch(`${BASE_URL}/risk-check`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  return handle(res);
}

export async function getCards() {
  const res = await fetch(`${BASE_URL}/dashboard/cards`);
  return handle(res);
}

export async function getSessions() {
  const res = await fetch(`${BASE_URL}/dashboard/sessions`);
  return handle(res);
}

export async function getSessionHistory(sessionId) {
  const res = await fetch(`${BASE_URL}/dashboard/sessions/${sessionId}/history`);
  return handle(res);
}

export async function getAuthLogs(limit = 20) {
  const res = await fetch(`${BASE_URL}/dashboard/auth-logs?limit=${limit}`);
  return handle(res);
}

export async function getRiskChecks(limit = 20) {
  const res = await fetch(`${BASE_URL}/dashboard/risk-checks?limit=${limit}`);
  return handle(res);
}

export async function getCardHistory(cardId) {
  const res = await fetch(`${BASE_URL}/dashboard/cards/${cardId}/history`);
  return handle(res);
}
