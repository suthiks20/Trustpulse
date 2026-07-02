import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { getCards, sessionStart, verify } from "../api";
import { useWebcamCapture } from "../hooks/useWebcamCapture";

export default function LoginPage({ onLogin }) {
  const [cardId, setCardId] = useState("");
  const [busy, setBusy] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const { videoRef, active, error: camError, start, stop, capture } = useWebcamCapture();
  const navigate = useNavigate();
  const location = useLocation();
  const infoMessage = location.state?.message;

  async function handleLogin() {
    const trimmed = cardId.trim();
    if (!trimmed) {
      setErrorMsg("Enter your card ID first");
      return;
    }

    setBusy(true);
    setErrorMsg("");

    const cameraReady = await start();
    if (!cameraReady) {
      setBusy(false);
      return;
    }

    await new Promise((resolve) => setTimeout(resolve, 800));

    try {
      const blob = await capture();
      const result = await verify(trimmed, blob);
      if (result.result !== "success") {
        setErrorMsg(`Verification failed (${result.reason || "no match"})`);
        return;
      }

      const session = await sessionStart(trimmed);
      const cards = await getCards();
      const card = cards.find((c) => c.card_id === trimmed);

      onLogin({ cardId: trimmed, sessionId: session.session_id, name: card?.name || trimmed });
      navigate("/bank");
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      stop();
      setBusy(false);
    }
  }

  return (
    <div className="max-w-md mx-auto mt-16 p-6">
      <div className="bg-white rounded-lg shadow p-6 flex flex-col gap-4">
        <h2 className="text-xl font-semibold text-slate-800">Login</h2>
        {infoMessage && <p className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded p-2">{infoMessage}</p>}

        {active && (
          <video ref={videoRef} autoPlay muted playsInline className="rounded bg-slate-900 w-full aspect-video" />
        )}

        <input
          className="border rounded px-3 py-2"
          placeholder="Card ID (e.g. DC0001)"
          value={cardId}
          onChange={(e) => setCardId(e.target.value)}
          disabled={busy}
        />

        <button
          onClick={handleLogin}
          disabled={busy}
          className="bg-slate-800 text-white rounded px-3 py-2 hover:bg-slate-700 disabled:opacity-50"
        >
          {busy ? "Verifying..." : "Login"}
        </button>

        {camError && <p className="text-sm text-red-600">{camError}</p>}
        {errorMsg && <p className="text-sm text-red-600">{errorMsg}</p>}

        <p className="text-sm text-slate-500">
          Don't have a card yet?{" "}
          <Link to="/enroll" className="text-slate-800 underline">
            Enroll here
          </Link>
        </p>
      </div>
    </div>
  );
}
