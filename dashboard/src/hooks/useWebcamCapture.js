import { useCallback, useEffect, useRef, useState } from "react";

/** Camera stays off until start() is called — no getUserMedia on mount. */
export function useWebcamCapture() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [active, setActive] = useState(false);
  const [error, setError] = useState("");

  const start = useCallback(async () => {
    setError("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      setActive(true);
      return true;
    } catch {
      setError("Camera access denied or unavailable");
      return false;
    }
  }, []);

  // The <video> element only mounts once `active` flips true (it's conditionally
  // rendered by callers), so the stream can only be attached after that commit —
  // attaching it inline inside start() would hit a still-null videoRef.
  useEffect(() => {
    if (active && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(() => {});
    }
  }, [active]);

  const stop = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setActive(false);
  }, []);

  const capture = useCallback(async () => {
    const video = videoRef.current;
    if (!video.videoWidth) {
      // give the stream a moment to paint its first frame
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    return new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.92));
  }, []);

  return { videoRef, active, error, start, stop, capture };
}
