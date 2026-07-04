import { useState } from "react";
import { Link } from "react-router-dom";
import { enroll } from "../api/enrollApi";
import { useWebcamCapture } from "../hooks/useWebcamCapture";

function validateDob(dob) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dob)) {
    return "Date must be in YYYY-MM-DD format";
  }
  const [year, month, day] = dob.split("-").map(Number);
  const date = new Date(dob + "T00:00:00");
  if (date.getFullYear() !== year || date.getMonth() + 1 !== month || date.getDate() !== day) {
    return "Not a valid calendar date";
  }
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  if (date > today) {
    return "Date of birth cannot be in the future";
  }
  return null;
}

export default function EnrollPage() {
  const [name, setName] = useState("");
  const [dob, setDob] = useState("");
  const [dobError, setDobError] = useState("");
  const [busy, setBusy] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [cardId, setCardId] = useState("");
  const [copied, setCopied] = useState(false);
  const { videoRef, active, error: camError, start, stop, capture } = useWebcamCapture();

  async function handleStartEnrollment() {
    if (!name.trim()) {
      setErrorMsg("Enter a name first");
      return;
    }
    const dobIssue = validateDob(dob);
    if (dobIssue) {
      setDobError(dobIssue);
      return;
    }
    setDobError("");
    setErrorMsg("");
    setBusy(true);

    const cameraReady = await start();
    if (!cameraReady) {
      setBusy(false);
      return;
    }

    await new Promise((resolve) => setTimeout(resolve, 800));

    try {
      const blob = await capture();
      const result = await enroll(name.trim(), dob, blob);
      setCardId(result.card_id);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      stop();
      setBusy(false);
    }
  }

  function handleCopy() {
    navigator.clipboard.writeText(cardId).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  if (cardId) {
    return (
      <div className="max-w-md mx-auto mt-16 p-6">
        <div className="bg-white rounded-lg shadow p-6 flex flex-col gap-4 items-center text-center">
          <h2 className="text-xl font-semibold text-slate-800">Enrollment complete</h2>
          <p className="text-slate-600 text-sm">Your card ID — save this, you'll need it to log in:</p>
          <div className="flex items-center gap-2">
            <span className="font-mono text-2xl font-bold text-slate-800">{cardId}</span>
            <button
              onClick={handleCopy}
              className="text-xs bg-slate-100 hover:bg-slate-200 rounded px-2 py-1 text-slate-700"
            >
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
          <Link to="/login" className="text-slate-800 underline text-sm">
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto mt-16 p-6">
      <div className="bg-white rounded-lg shadow p-6 flex flex-col gap-4">
        <h2 className="text-xl font-semibold text-slate-800">Enroll a Demo Card</h2>

        {active && (
          <video ref={videoRef} autoPlay muted playsInline className="rounded bg-slate-900 w-full aspect-video" />
        )}

        <input
          className="border rounded px-3 py-2"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          disabled={busy}
        />
        <div>
          <input
            className="border rounded px-3 py-2 w-full"
            placeholder="Date of birth (YYYY-MM-DD)"
            value={dob}
            onChange={(e) => setDob(e.target.value)}
            disabled={busy}
          />
          {dobError && <p className="text-sm text-red-600 mt-1">{dobError}</p>}
        </div>

        <button
          onClick={handleStartEnrollment}
          disabled={busy}
          className="bg-slate-800 text-white rounded px-3 py-2 hover:bg-slate-700 disabled:opacity-50"
        >
          {busy ? "Enrolling..." : "Start Enrollment"}
        </button>

        {camError && <p className="text-sm text-red-600">{camError}</p>}
        {errorMsg && <p className="text-sm text-red-600">{errorMsg}</p>}

        <p className="text-sm text-slate-500">
          Already have a card?{" "}
          <Link to="/login" className="text-slate-800 underline">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}
