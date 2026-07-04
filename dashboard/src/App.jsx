import { useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary";
import NavBar from "./components/NavBar";
import RequireAdmin from "./components/RequireAdmin";
import ToastContainer from "./components/ToastContainer";
import { AdminAuthProvider } from "./context/AdminAuthContext";
import AdminLoginPage from "./pages/AdminLoginPage";
import AdminRiskChecksPage from "./pages/AdminRiskChecksPage";
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
        <Route path="/admin/login" element={<AdminLoginPage />} />
        <Route
          path="/reports"
          element={
            <RequireAdmin>
              <ReportsPage />
            </RequireAdmin>
          }
        />
        <Route
          path="/reports/:cardId"
          element={
            <RequireAdmin>
              <CardHistoryPage />
            </RequireAdmin>
          }
        />
        <Route path="/site-risk" element={<SiteRiskPage />} />
        <Route
          path="/admin/risk-checks"
          element={
            <RequireAdmin>
              <AdminRiskChecksPage />
            </RequireAdmin>
          }
        />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AdminAuthProvider>
        <BrowserRouter>
          <AppShell />
        </BrowserRouter>
        <ToastContainer />
      </AdminAuthProvider>
    </ErrorBoundary>
  );
}
