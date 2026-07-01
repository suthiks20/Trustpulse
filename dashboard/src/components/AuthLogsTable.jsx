import { useEffect, useState } from "react";
import { getAuthLogs } from "../api";

export default function AuthLogsTable({ refreshKey }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    getAuthLogs(20).then(setLogs).catch(() => setLogs([]));
  }, [refreshKey]);

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold text-slate-800 mb-2">Auth Logs</h2>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 border-b">
            <th className="py-1">Card</th>
            <th>Match</th>
            <th>Liveness</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.log_id} className="border-b last:border-0">
              <td className="py-1">{log.card_id}</td>
              <td>{log.match_score.toFixed(2)}</td>
              <td>{log.liveness_passed ? "pass" : "fail"}</td>
              <td className={log.result === "success" ? "text-green-600" : "text-red-600"}>{log.result}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
