// Runs in an Offscreen Document so periodic webcam capture works without a
// popup open. The camera indicator will be visibly active during checks —
// that's expected, not a bug (see README).

let stream = null;

async function ensureStream() {
  if (stream && stream.active) return stream;
  stream = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 } });
  return stream;
}

/** Releases the camera so the OS/browser capture indicator turns off. Called
 * when a session ends — without this, the stream opened by ensureStream()
 * for periodic re-verify stays alive (and the camera light stays on)
 * indefinitely, since nothing else in this document's lifecycle stops it. */
function stopStream() {
  if (stream) {
    stream.getTracks().forEach((t) => t.stop());
    stream = null;
  }
  const video = document.getElementById("video");
  video.srcObject = null;
}

async function captureFrame() {
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");

  const activeStream = await ensureStream();
  video.srcObject = activeStream;
  await video.play();
  await new Promise((resolve) => setTimeout(resolve, 200)); // let exposure/focus settle

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);

  return new Promise((resolve) => {
    canvas.toBlob((blob) => resolve(blob), "image/jpeg", 0.9);
  });
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "OFFSCREEN_CAPTURE") {
    captureFrame()
      .then((blob) => sendResponse({ blob }))
      .catch((err) => sendResponse({ error: String(err) }));
    return true;
  }

  if (message.type === "OFFSCREEN_STOP") {
    stopStream();
    sendResponse({ stopped: true });
    return true;
  }

  return false;
});
