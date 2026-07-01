import { useState } from "react";
import EnrollPanel from "./components/EnrollPanel";
import VerifyPanel from "./components/VerifyPanel";
import RiskCheckPanel from "./components/RiskCheckPanel";
import TrustScoreMeter from "./components/TrustScoreMeter";
import TrustScoreChart from "./components/TrustScoreChart";
import SessionHistoryTable from "./components/SessionHistoryTable";
import AuthLogsTable from "./components/AuthLogsTable";
import SiteRiskTable from "./components/SiteRiskTable";
import TrustTimelineReport from "./components/TrustTimelineReport";

export default function App() {
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  function bumpRefresh() {
    setRefreshKey((k) => k + 1);
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-slate-800 text-white px-6 py-4">
        <h1 className="text-2xl font-bold">TrustPulse</h1>
        <p className="text-slate-300 text-sm">Continuous identity + phishing trust scoring demo</p>
      </header>

      <main className="max-w-6xl mx-auto p-6 flex flex-col gap-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <EnrollPanel onEnrolled={bumpRefresh} />
          <VerifyPanel
            onSessionStarted={(sessionId) => {
              setActiveSessionId(sessionId);
              bumpRefresh();
            }}
          />
          <RiskCheckPanel />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <TrustScoreMeter sessionId={activeSessionId} onUpdate={bumpRefresh} />
          <TrustScoreChart sessionId={activeSessionId} refreshKey={refreshKey} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <TrustTimelineReport sessionId={activeSessionId} refreshKey={refreshKey} />
          <SessionHistoryTable
            selectedSessionId={activeSessionId}
            onSelect={setActiveSessionId}
            refreshKey={refreshKey}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <AuthLogsTable refreshKey={refreshKey} />
          <SiteRiskTable refreshKey={refreshKey} />
        </div>
      </main>
    </div>
  );
}
