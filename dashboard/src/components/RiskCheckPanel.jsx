import { useState } from "react";
import { riskCheck } from "../api";

export default function RiskCheckPanel() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleCheck() {
    if (!url) return;
    setBusy(true);
    setError("");
    try {
      const res = await riskCheck(url);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-4 flex flex-col gap-3">
      <h2 className="text-lg font-semibold text-slate-800">Site Risk Check</h2>
      <input
        className="border rounded px-2 py-1"
        placeholder="e.g. hdfc-bank-secure-login.com"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button
        onClick={handleCheck}
        disabled={busy}
        className="bg-slate-800 text-white rounded px-3 py-1.5 hover:bg-slate-700 disabled:opacity-50"
      >
        Check URL
      </button>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {result && (
        <div className="text-sm text-slate-700 grid grid-cols-3 gap-2">
          <div>SSL valid: {result.ssl_valid ? "yes" : "no"}</div>
          <div>Lookalike score: {result.lookalike_score}</div>
          <div
            className={
              result.risk_score >= 60
                ? "text-red-600 font-semibold"
                : result.risk_score >= 30
                ? "text-amber-600 font-semibold"
                : "text-green-600 font-semibold"
            }
          >
            Risk score: {result.risk_score}
          </div>
        </div>
      )}
    </div>
  );
}
