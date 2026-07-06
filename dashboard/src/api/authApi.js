import { apiFetch, apiJson, setAccessToken, clearAccessToken } from "./client";

export async function login(email, password) {
  const data = await apiJson("/auth/login", "POST", { email, password });
  if (data?.access_token) {
    setAccessToken(data.access_token);
  }
  return data;
}

export async function logout() {
  const data = await apiFetch("/auth/logout", { method: "POST" });
  clearAccessToken();
  return data;
}

export async function refresh() {
  const data = await apiFetch("/auth/refresh", { method: "POST" });
  if (data?.access_token) {
    setAccessToken(data.access_token);
  }
  return data;
}

export function me() {
  return apiFetch("/auth/me");
}