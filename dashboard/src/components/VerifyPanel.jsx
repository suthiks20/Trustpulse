import { useEffect, useRef, useState } from "react";
import { sessionStart, verify } from "../api";

export default function VerifyPanel({ onSessionStarted }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [cardId, setCardId] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      })
      .catch(() => setStatus("Camera access denied"));

    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  function captureBlob() {
    const video = videoRef.current;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    return new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.92));
  }

  async function handleVerify() {
    if (!cardId) {
      setStatus("Enter a card ID first");
      return;
    }
    setBusy(true);
    setStatus("Verifying...");
    try {
      const blob = await captureBlob();
      const result = await verify(cardId, blob);
      if (result.result !== "success") {
        setStatus(`Verification failed (${result.reason || "no match"})`);
        return;
      }
      setStatus(`Verified — match score ${result.match_score}`);
      const session = await sessionStart(cardId);
      onSessionStarted?.(session.session_id);
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-4 flex flex-col gap-3">
      <h2 className="text-lg font-semibold text-slate-800">Verify & Start Session</h2>
      <video ref={videoRef} autoPlay muted playsInline className="rounded bg-slate-900 w-full aspect-video" />
      <input
        className="border rounded px-2 py-1"
        placeholder="Card ID (e.g. DC0001)"
        value={cardId}
        onChange={(e) => setCardId(e.target.value)}
      />
      <button
        onClick={handleVerify}
        disabled={busy}
        className="bg-slate-800 text-white rounded px-3 py-1.5 hover:bg-slate-700 disabled:opacity-50"
      >
        Verify
      </button>
      {status && <p className="text-sm text-slate-600">{status}</p>}
    </div>
  );
}
