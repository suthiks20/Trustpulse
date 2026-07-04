import { apiFetch } from "./client";

export function enroll(name, dob, imageBlob) {
  const form = new FormData();
  form.append("name", name);
  form.append("dob", dob);
  form.append("image", imageBlob, "capture.jpg");
  return apiFetch("/enroll", { method: "POST", body: form });
}
