import { useEffect, useRef, useState } from "react";
import { subscribeToasts } from "../toast";

export default function ToastContainer() {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  useEffect(() => {
    return subscribeToasts(({ message, type }) => {
      const id = idRef.current++;
      setToasts((prev) => [...prev, { id, message, type }]);
      setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 5000);
    });
  }, []);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 flex flex-col gap-2 z-50">
      {toasts.map((t) => (
        <div
          key={t.id}
          className="bg-red-600 text-white text-sm rounded shadow-lg px-4 py-2 max-w-sm"
          role="alert"
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
