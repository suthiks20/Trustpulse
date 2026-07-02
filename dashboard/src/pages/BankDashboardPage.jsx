import { useCallback } from "react";
import { useNavigate } from "react-router-dom";
import RiskCheckPanel from "../components/RiskCheckPanel";
import TrustScoreMeter from "../components/TrustScoreMeter";
import { useIdleTimeout } from "../hooks/useIdleTimeout";

const IDLE_TIMEOUT_MS = 60000;

// Fake data for the mock banking UI — this demo has no real accounts or transactions.
const FAKE_TRANSACTIONS = [
  { id: 1, label: "Grocery Store", amount: -54.2, date: "2026-06-29" },
  { id: 2, label: "Salary Deposit", amount: 3200.0, date: "2026-06-28" },
  { id: 3, label: "Electric Bill", amount: -88.5, date: "2026-06-25" },
  { id: 4, label: "Coffee Shop", amount: -6.75, date: "2026-06-24" },
  { id: 5, label: "Online Transfer", amount: -200.0, date: "2026-06-20" },
];
const FAKE_BALANCE = 12480.35;

export default function BankDashboardPage({ session, onLogout }) {
  const navigate = useNavigate();

  const handleIdle = useCallback(() => {
    onLogout();
    navigate("/login", { state: { message: "Session expired due to inactivity — please verify again." } });
  }, [onLogout, navigate]);

  useIdleTimeout(IDLE_TIMEOUT_MS, handleIdle);

  function handleLogoutClick() {
    onLogout();
    navigate("/login");
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-slate-800 px-6 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">TrustPulse Bank</h1>
          <p className="text-slate-400 text-xs">Welcome back, {session.name}</p>
        </div>
        <button
          onClick={handleLogoutClick}
          className="bg-slate-700 text-white rounded px-3 py-1.5 text-sm hover:bg-slate-600"
        >
          Logout
        </button>
      </header>

      <main className="max-w-5xl mx-auto p-6 flex flex-col gap-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-4 md:col-span-2">
            <h2 className="text-lg font-semibold text-slate-800 mb-1">Account Balance</h2>
            <p className="text-3xl font-bold text-slate-900">
              ${FAKE_BALANCE.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </p>
            <p className="text-xs text-slate-500 mt-1">Checking •••• {session.cardId.slice(-4)}</p>
          </div>
          <TrustScoreMeter sessionId={session.sessionId} />
        </div>

        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold text-slate-800 mb-2">Recent Transactions</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b">
                <th className="py-1">Date</th>
                <th>Description</th>
                <th className="text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {FAKE_TRANSACTIONS.map((t) => (
                <tr key={t.id} className="border-b last:border-0">
                  <td className="py-1">{t.date}</td>
                  <td>{t.label}</td>
                  <td className={`text-right ${t.amount < 0 ? "text-slate-700" : "text-green-600"}`}>
                    {t.amount < 0 ? "-" : "+"}${Math.abs(t.amount).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <RiskCheckPanel />
      </main>
    </div>
  );
}
