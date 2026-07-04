"""MediaPipe Face Mesh wrapper: returns facial landmarks from a single image.

Runs entirely locally (no cloud calls) as part of TrustPulse's local-only face pipeline.
"""

import mediapipe as mp
import numpy as np

_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
)


def get_landmarks(image_bgr: np.ndarray):
    """Return (landmarks, image_shape) for the first detected face, or (None, shape) if no face found.

    landmarks is a list of (x, y, z) tuples in normalized [0, 1] image coordinates.
    """
    image_rgb = image_bgr[:, :, ::-1]
    results = _face_mesh.process(image_rgb)
    if not results.multi_face_landmarks:
        return None, image_bgr.shape

    face_landmarks = results.multi_face_landmarks[0]
    landmarks = [(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark]
    return landmarks, image_bgr.shape


def has_face(image_bgr: np.ndarray) -> bool:
    landmarks, _ = get_landmarks(image_bgr)
    return landmarks is not None
