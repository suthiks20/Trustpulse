import { useEffect, useRef, useState } from "react";
import { sessionHeartbeat } from "../api";

function colorFor(score) {
  if (score > 70) return "#16a34a";
  if (score >= 40) return "#d97706";
  return "#dc2626";
}

export default function TrustScoreMeter({ sessionId, onUpdate }) {
  const [score, setScore] = useState(100);
  const [flag, setFlag] = useState("none");
  const [reason, setReason] = useState("");
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;

    async function poll() {
      try {
        const res = await sessionHeartbeat(sessionId);
        setScore(res.trust_score);
        setFlag(res.flag);
        setReason(res.latest_reason);
        onUpdate?.(res);
      } catch {
        clearInterval(intervalRef.current);
      }
    }

    poll();
    intervalRef.current = setInterval(poll, 2000);
    return () => clearInterval(intervalRef.current);
  }, [sessionId]);

  if (!sessionId) {
    return (
      <div className="bg-white rounded-lg shadow p-4 text-slate-500 text-sm">
        Verify to start a session and see the live trust score.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4 flex flex-col items-center gap-2">
      <h2 className="text-lg font-semibold text-slate-800 self-start">Live Trust Score</h2>
      <div
        className="rounded-full w-32 h-32 flex items-center justify-center text-3xl font-bold border-8"
        style={{ borderColor: colorFor(score), color: colorFor(score) }}
      >
        {Math.round(score)}
      </div>
      {flag === "warning" && <p className="text-amber-600 text-sm font-medium">Warning: trust score dipped</p>}
      {flag === "reverify" && <p className="text-red-600 text-sm font-medium">Re-verification required</p>}
      {reason && <p className="text-xs text-slate-500">{reason}</p>}
    </div>
  );
}
