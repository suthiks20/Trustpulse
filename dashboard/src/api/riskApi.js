import { apiJson } from "./client";

export function riskCheck(url) {
  return apiJson("/risk-check", "POST", { url });
}
