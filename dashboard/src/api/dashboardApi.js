import { apiFetch } from "./client";

export function getCards() {
  return apiFetch("/dashboard/cards");
}

export function getCardHistory(cardId) {
  return apiFetch(`/dashboard/cards/${cardId}/history`);
}

export function getSessions() {
  return apiFetch("/dashboard/sessions");
}

export function getAuthLogs(limit = 20) {
  return apiFetch(`/dashboard/auth-logs?limit=${limit}`);
}

export function getRiskChecks(limit = 20) {
  return apiFetch(`/dashboard/risk-checks?limit=${limit}`);
}
