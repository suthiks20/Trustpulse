import { useEffect, useState } from "react";
import { getRiskChecks } from "../api";

export default function SiteRiskTable({ refreshKey }) {
  const [checks, setChecks] = useState([]);

  useEffect(() => {
    getRiskChecks(20).then(setChecks).catch(() => setChecks([]));
  }, [refreshKey]);

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold text-slate-800 mb-2">Site Risk Checks</h2>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 border-b">
            <th className="py-1">URL</th>
            <th>SSL</th>
            <th>Risk</th>
          </tr>
        </thead>
        <tbody>
          {checks.map((c) => (
            <tr key={c.id} className="border-b last:border-0">
              <td className="py-1 truncate max-w-[160px]">{c.url}</td>
              <td>{c.ssl_valid ? "valid" : "invalid"}</td>
              <td
                className={
                  c.risk_score >= 60 ? "text-red-600" : c.risk_score >= 30 ? "text-amber-600" : "text-green-600"
                }
              >
                {c.risk_score}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
