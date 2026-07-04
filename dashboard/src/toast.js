// Lightweight pub-sub so the API layer (outside the React tree) can surface
// failures without importing React. ToastContainer subscribes on mount.
const TOAST_EVENT = "trustpulse:toast";

export function emitApiError(message) {
  window.dispatchEvent(new CustomEvent(TOAST_EVENT, { detail: { message, type: "error" } }));
}

export function subscribeToasts(callback) {
  const handler = (event) => callback(event.detail);
  window.addEventListener(TOAST_EVENT, handler);
  return () => window.removeEventListener(TOAST_EVENT, handler);
}
