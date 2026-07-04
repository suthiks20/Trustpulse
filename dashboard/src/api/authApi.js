import { apiFetch, apiJson } from "./client";

export function login(email, password) {
  return apiJson("/auth/login", "POST", { email, password });
}

export function logout() {
  return apiFetch("/auth/logout", { method: "POST" });
}

export function refresh() {
  return apiFetch("/auth/refresh", { method: "POST" });
}

export function me() {
  return apiFetch("/auth/me");
}
