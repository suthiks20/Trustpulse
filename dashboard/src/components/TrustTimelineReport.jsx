import { useEffect, useState } from "react";
import { getSessionHistory } from "../api";

export default function TrustTimelineReport({ sessionId, refreshKey }) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    if (!sessionId) return;
    getSessionHistory(sessionId).then(setEvents).catch(() => setEvents([]));
  }, [sessionId, refreshKey]);

  if (!sessionId) {
    return (
      <div className="bg-white rounded-lg shadow p-4 text-slate-500 text-sm">
        Select a session to view its trust timeline report.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold text-slate-800 mb-2">Session Trust Timeline</h2>
      <ul className="text-sm text-slate-700 flex flex-col gap-1 max-h-80 overflow-y-auto">
        {events.map((e) => (
          <li key={e.event_id} className="border-b last:border-0 py-1">
            <span className="font-mono text-xs text-slate-400 mr-2">
              {new Date(e.timestamp).toLocaleTimeString()}
            </span>
            <span className="font-semibold mr-2">score {Math.round(e.resulting_score)}.</span>
            {e.explanation}
          </li>
        ))}
      </ul>
    </div>
  );
}
