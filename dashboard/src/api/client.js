import { emitApiError } from "../toast";

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

let accessToken = null;

export function setAccessToken(token) {
  accessToken = token;
  if (token) {
    localStorage.setItem("access_token", token);
  } else {
    localStorage.removeItem("access_token");
  }
}

export function loadAccessToken() {
  accessToken = localStorage.getItem("access_token");
  return accessToken;
}

export function clearAccessToken() {
  setAccessToken(null);
}

async function unwrap(res) {
  const body = await res.json().catch(() => ({ success: false, error: { message: `HTTP ${res.status}` } }));
  if (!res.ok || body.success === false) {
    const message = body?.error?.message || `Request failed: ${res.status}`;
    emitApiError(message);
    throw new Error(message);
  }
  return body.data;
}

export function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }
  return fetch(`${API_BASE_URL}${path}`, { ...options, headers }).then(unwrap);
}

export function apiJson(path, method, payload) {
  return apiFetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}