import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import AuthLogsTable from "../components/AuthLogsTable";
import SessionHistoryTable from "../components/SessionHistoryTable";
import TrustTimelineReport from "../components/TrustTimelineReport";
import { getCardHistory } from "../api/dashboardApi";

export default function CardHistoryPage() {
  const { cardId } = useParams();
  const [history, setHistory] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setHistory(null);
    setError("");
    getCardHistory(cardId)
      .then(setHistory)
      .catch((err) => setError(err.message));
  }, [cardId]);

  return (
    <div className="max-w-5xl mx-auto p-6 flex flex-col gap-4">
      <Link to="/reports" className="text-sm text-slate-600 underline w-fit">
        ← Back to Reports
      </Link>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {history && (
        <>
          <div className="flex items-center gap-4">
            {history.photo_url ? (
              <img
                src={history.photo_url}
                alt=""
                className="w-16 h-16 rounded-full object-cover bg-slate-100"
              />
            ) : (
              <div className="w-16 h-16 rounded-full bg-slate-100" />
            )}
            <div>
              <h2 className="text-xl font-semibold text-slate-800">{history.name}</h2>
              <p className="text-sm text-slate-500 font-mono">{history.card_id}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SessionHistoryTable data={history.sessions} selectedSessionId={null} onSelect={() => {}} />
            <AuthLogsTable data={history.auth_logs} />
          </div>

          <TrustTimelineReport data={history.trust_events} title="Trust Timeline" />
        </>
      )}
    </div>
  );
}
