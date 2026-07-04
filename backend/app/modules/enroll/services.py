import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.enroll import repository
from app.shared.embedding import get_embedding, serialize_embedding
from app.shared.exceptions import ValidationAppError
from app.shared.image_validation import validate_image_bytes
from app.shared.storage import upload_photo


def _decode_image(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValidationAppError("Could not decode image")
    return image


async def enroll_card(db: AsyncSession, name: str, dob: str, file_bytes: bytes) -> dict:
    validate_image_bytes(file_bytes)
    image_bgr = _decode_image(file_bytes)

    embedding = get_embedding(image_bgr)
    if embedding is None:
        raise ValidationAppError("No face detected in image")

    card_id = await repository.next_card_id(db)

    ok, buffer = cv2.imencode(".jpg", image_bgr)
    if not ok:
        raise ValidationAppError("Could not encode image for upload")
    storage_key = upload_photo(card_id, buffer.tobytes())

    await repository.create_demo_card(
        db,
        card_id=card_id,
        name=name,
        dob=dob,
        photo_path=storage_key,
        embedding=serialize_embedding(embedding),
    )

    return {"card_id": card_id, "status": "enrolled"}
