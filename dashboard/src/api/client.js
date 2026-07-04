import { emitApiError } from "../toast";

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

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
  return fetch(`${API_BASE_URL}${path}`, { credentials: "include", ...options }).then(unwrap);
}

export function apiJson(path, method, payload) {
  return apiFetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
