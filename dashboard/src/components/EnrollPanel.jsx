import { useEffect, useRef, useState } from "react";
import { enroll } from "../api";

export default function EnrollPanel({ onEnrolled }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [name, setName] = useState("");
  const [dob, setDob] = useState("");
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

  async function handleEnroll() {
    if (!name || !dob) {
      setStatus("Enter name and date of birth first");
      return;
    }
    setBusy(true);
    setStatus("Enrolling...");
    try {
      const blob = await captureBlob();
      const result = await enroll(name, dob, blob);
      setStatus(`Enrolled as ${result.card_id}`);
      onEnrolled?.(result.card_id);
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-4 flex flex-col gap-3">
      <h2 className="text-lg font-semibold text-slate-800">Enroll Demo Card</h2>
      <video ref={videoRef} autoPlay muted playsInline className="rounded bg-slate-900 w-full aspect-video" />
      <input
        className="border rounded px-2 py-1"
        placeholder="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        className="border rounded px-2 py-1"
        placeholder="Date of birth (YYYY-MM-DD)"
        value={dob}
        onChange={(e) => setDob(e.target.value)}
      />
      <button
        onClick={handleEnroll}
        disabled={busy}
        className="bg-slate-800 text-white rounded px-3 py-1.5 hover:bg-slate-700 disabled:opacity-50"
      >
        Enroll
      </button>
      {status && <p className="text-sm text-slate-600">{status}</p>}
    </div>
  );
}
