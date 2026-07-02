import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getCards } from "../api";

export default function ReportsPage() {
  const [cards, setCards] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getCards()
      .then(setCards)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h2 className="text-xl font-semibold text-slate-800 mb-4">Enrolled Cards</h2>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <div className="bg-white rounded-lg shadow divide-y">
        {cards.length === 0 && !error && <p className="p-4 text-sm text-slate-500">No cards enrolled yet.</p>}
        {cards.map((c) => (
          <Link
            key={c.card_id}
            to={`/reports/${c.card_id}`}
            className="flex items-center justify-between px-4 py-3 hover:bg-slate-50"
          >
            <div>
              <p className="font-medium text-slate-800">{c.name}</p>
              <p className="text-xs text-slate-500">DOB {c.dob}</p>
            </div>
            <span className="font-mono text-sm text-slate-600">{c.card_id}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
