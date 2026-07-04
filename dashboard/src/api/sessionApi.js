import { apiJson } from "./client";

export function sessionStart(cardId) {
  return apiJson("/session/start", "POST", { card_id: cardId });
}

export function sessionHeartbeat(sessionId) {
  return apiJson("/session/heartbeat", "POST", { session_id: sessionId });
}
