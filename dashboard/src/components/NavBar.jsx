import { NavLink, useNavigate } from "react-router-dom";
import { useAdminAuth } from "../context/AdminAuthContext";

const linkClass = ({ isActive }) =>
  `px-3 py-1.5 rounded text-sm font-medium ${
    isActive ? "bg-slate-700 text-white" : "text-slate-300 hover:text-white hover:bg-slate-700"
  }`;

export default function NavBar() {
  const { admin, logout } = useAdminAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/admin/login");
  }

  return (
    <header className="bg-slate-800 px-6 py-3 flex items-center justify-between">
      <div>
        <h1 className="text-xl font-bold text-white">TrustPulse</h1>
        <p className="text-slate-400 text-xs">Continuous identity + phishing trust scoring demo</p>
      </div>
      <nav className="flex items-center gap-1">
        <NavLink to="/login" className={linkClass}>
          Login
        </NavLink>
        <NavLink to="/enroll" className={linkClass}>
          Enroll
        </NavLink>
        <NavLink to="/reports" className={linkClass}>
          Reports
        </NavLink>
        <NavLink to="/site-risk" className={linkClass}>
          Site Risk
        </NavLink>
        {admin && (
          <NavLink to="/admin/risk-checks" className={linkClass}>
            Risk Log
          </NavLink>
        )}
        {admin ? (
          <button onClick={handleLogout} className="ml-2 px-3 py-1.5 rounded text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-700">
            Admin logout
          </button>
        ) : (
          <NavLink to="/admin/login" className={linkClass}>
            Admin
          </NavLink>
        )}
      </nav>
    </header>
  );
}
