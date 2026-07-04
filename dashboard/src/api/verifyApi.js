import { apiFetch } from "./client";

export function verify(cardId, imageBlob) {
  const form = new FormData();
  form.append("card_id", cardId);
  form.append("image", imageBlob, "capture.jpg");
  return apiFetch("/verify", { method: "POST", body: form });
}
