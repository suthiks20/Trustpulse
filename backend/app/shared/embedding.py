"""FaceNet embeddings via facenet-pytorch (pretrained on vggface2). Runs locally on CPU.

Uses a pretrained model only — no training happens in this project.
"""

import io

import numpy as np
import torch
from facenet_pytorch import InceptionResnetV1, MTCNN
from PIL import Image

_device = torch.device("cpu")
_mtcnn = MTCNN(image_size=160, margin=0, post_process=True, device=_device)
_resnet = InceptionResnetV1(pretrained="vggface2").eval().to(_device)


MIN_DIMENSION_FOR_DETECTION = 400


def get_embedding(image_bgr: np.ndarray) -> np.ndarray | None:
    """Detect + crop the face with MTCNN, then return a 512-d FaceNet embedding.

    Returns None if no face could be detected/cropped.
    """
    image_rgb = image_bgr[:, :, ::-1]
    pil_image = Image.fromarray(image_rgb)

    # Small/tightly-cropped inputs make MTCNN's own detector miss context it needs
    # to localize the face accurately, so upsample before detection.
    if max(pil_image.size) < MIN_DIMENSION_FOR_DETECTION:
        scale = MIN_DIMENSION_FOR_DETECTION / max(pil_image.size)
        pil_image = pil_image.resize((int(pil_image.width * scale), int(pil_image.height * scale)))

    face_tensor = _mtcnn(pil_image)
    if face_tensor is None:
        return None

    with torch.no_grad():
        embedding = _resnet(face_tensor.unsqueeze(0).to(_device))

    return embedding[0].cpu().numpy().astype(np.float32)


def serialize_embedding(embedding: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.save(buffer, embedding.astype(np.float32))
    return buffer.getvalue()


def deserialize_embedding(blob: bytes) -> np.ndarray:
    buffer = io.BytesIO(blob)
    return np.load(buffer)
