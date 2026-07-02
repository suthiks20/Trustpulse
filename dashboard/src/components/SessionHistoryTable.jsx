import { useEffect, useState } from "react";
import { getSessions } from "../api";

export default function SessionHistoryTable({ selectedSessionId, onSelect, refreshKey, data }) {
  const [fetched, setFetched] = useState([]);
  const sessions = data ?? fetched;

  useEffect(() => {
    if (data) return;
    getSessions().then(setFetched).catch(() => setFetched([]));
  }, [refreshKey, data]);

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold text-slate-800 mb-2">Sessions</h2>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-slate-500 border-b">
            <th className="py-1">Session</th>
            <th>Card</th>
            <th>Trust</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map((s) => (
            <tr
              key={s.session_id}
              onClick={() => onSelect?.(s.session_id)}
              className={`cursor-pointer border-b last:border-0 hover:bg-slate-50 ${
                selectedSessionId === s.session_id ? "bg-slate-100" : ""
              }`}
            >
              <td className="py-1 font-mono text-xs">{s.session_id.slice(0, 8)}</td>
              <td>{s.card_id}</td>
              <td>{Math.round(s.trust_score)}</td>
              <td>{s.expired ? "expired" : "active"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
