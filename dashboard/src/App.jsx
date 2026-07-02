import { useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import NavBar from "./components/NavBar";
import BankDashboardPage from "./pages/BankDashboardPage";
import CardHistoryPage from "./pages/CardHistoryPage";
import EnrollPage from "./pages/EnrollPage";
import LoginPage from "./pages/LoginPage";
import ReportsPage from "./pages/ReportsPage";
import SiteRiskPage from "./pages/SiteRiskPage";

function AppShell() {
  const [session, setSession] = useState(null); // { cardId, sessionId, name } | null
  const location = useLocation();

  return (
    <div className="min-h-screen bg-slate-100">
      {location.pathname !== "/bank" && <NavBar />}

      <Routes>
        <Route path="/" element={<LoginPage onLogin={setSession} />} />
        <Route path="/login" element={<LoginPage onLogin={setSession} />} />
        <Route path="/enroll" element={<EnrollPage />} />
        <Route
          path="/bank"
          element={
            session ? (
              <BankDashboardPage session={session} onLogout={() => setSession(null)} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/reports/:cardId" element={<CardHistoryPage />} />
        <Route path="/site-risk" element={<SiteRiskPage />} />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}
