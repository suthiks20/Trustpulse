import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getSessionHistory } from "../api";

export default function TrustScoreChart({ sessionId, refreshKey }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    if (!sessionId) return;
    getSessionHistory(sessionId)
      .then((events) =>
        setData(
          events.map((e) => ({
            time: new Date(e.timestamp).toLocaleTimeString(),
            score: e.resulting_score,
          }))
        )
      )
      .catch(() => setData([]));
  }, [sessionId, refreshKey]);

  if (!sessionId) {
    return <div className="bg-white rounded-lg shadow p-4 text-slate-500 text-sm">No session selected yet.</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-semibold text-slate-800 mb-2">Trust Score Over Time</h2>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" fontSize={11} />
          <YAxis domain={[0, 100]} fontSize={11} />
          <Tooltip />
          <Line type="monotone" dataKey="score" stroke="#334155" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
