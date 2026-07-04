import { apiFetch } from "./client";

/** Admin-only: full trust event history for a session, with explanations. */
export function getSessionTrustEvents(sessionId) {
  return apiFetch(`/trust/sessions/${sessionId}/events`);
}
