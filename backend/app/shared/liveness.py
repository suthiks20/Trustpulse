"""Liveness check.

Primary method: Eye Aspect Ratio (EAR) blink detection across a short sequence of
frames (requires the EAR to dip below a closed-eye threshold and then recover,
proving at least one blink happened).

Fallback: when only a single frame is available (the simple case for this demo's
/verify endpoint), fall back to a basic texture heuristic (Laplacian variance) as a
much weaker signal that the image isn't a flat/blurry printed photo. This fallback is
clearly not real anti-spoofing and is documented as such in the README.
"""

import cv2
import numpy as np

from app.shared.face_detect import get_landmarks

EAR_CLOSED_THRESHOLD = 0.21
TEXTURE_VARIANCE_THRESHOLD = 30.0

# MediaPipe FaceMesh landmark indices for eye corners/lids, ordered (p1..p6)
# to match the classic Soukupova & Cech EAR formula.
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]


def _euclidean(p1, p2, shape):
    h, w = shape[0], shape[1]
    x1, y1 = p1[0] * w, p1[1] * h
    x2, y2 = p2[0] * w, p2[1] * h
    return float(np.hypot(x1 - x2, y1 - y2))


def _eye_aspect_ratio(landmarks, eye_indices, shape) -> float:
    pts = [landmarks[i] for i in eye_indices]
    vertical_1 = _euclidean(pts[1], pts[5], shape)
    vertical_2 = _euclidean(pts[2], pts[4], shape)
    horizontal = _euclidean(pts[0], pts[3], shape)
    if horizontal == 0:
        return 0.0
    return (vertical_1 + vertical_2) / (2.0 * horizontal)


def frame_ear(image_bgr: np.ndarray) -> float | None:
    landmarks, shape = get_landmarks(image_bgr)
    if landmarks is None:
        return None
    left = _eye_aspect_ratio(landmarks, LEFT_EYE, shape)
    right = _eye_aspect_ratio(landmarks, RIGHT_EYE, shape)
    return (left + right) / 2.0


def detect_blink_in_sequence(frames: list[np.ndarray]) -> bool:
    """Return True if the EAR dips below the closed threshold and recovers above it
    somewhere across the given frame sequence (i.e. at least one blink)."""
    ears = [frame_ear(f) for f in frames]
    ears = [e for e in ears if e is not None]
    if len(ears) < 2:
        return False

    seen_closed = False
    for ear in ears:
        if ear < EAR_CLOSED_THRESHOLD:
            seen_closed = True
        elif seen_closed and ear >= EAR_CLOSED_THRESHOLD:
            return True
    return False


def texture_liveness_fallback(image_bgr: np.ndarray) -> bool:
    """Weak single-frame liveness heuristic: real, in-focus faces tend to have higher
    local texture variance than flat/blurry printed photos or screen replays."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance >= TEXTURE_VARIANCE_THRESHOLD


def check_liveness(frames: list[np.ndarray]) -> bool:
    """Runs blink-based liveness if multiple frames are provided, otherwise falls
    back to the single-frame texture heuristic."""
    if len(frames) >= 2:
        return detect_blink_in_sequence(frames)
    return texture_liveness_fallback(frames[0])
