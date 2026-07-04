import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.verify import repository
from app.shared.embedding import deserialize_embedding, get_embedding
from app.shared.exceptions import NotFoundError, ValidationAppError
from app.shared.image_validation import validate_image_bytes
from app.shared.liveness import check_liveness
from app.shared.matcher import is_match


def _decode_image(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValidationAppError("Could not decode image")
    return image


async def verify_card(db: AsyncSession, card_id: str, file_bytes: bytes) -> dict:
    card = await repository.get_demo_card(db, card_id)
    if card is None:
        raise NotFoundError("Unknown card_id")

    validate_image_bytes(file_bytes)
    image_bgr = _decode_image(file_bytes)

    liveness_passed = check_liveness([image_bgr])
    if not liveness_passed:
        await repository.create_auth_log(db, card_id=card_id, match_score=0.0, liveness_passed=False, result="fail")
        return {"match_score": 0.0, "liveness_passed": False, "result": "fail", "reason": "liveness_failed"}

    probe_embedding = get_embedding(image_bgr)
    if probe_embedding is None:
        await repository.create_auth_log(db, card_id=card_id, match_score=0.0, liveness_passed=True, result="fail")
        return {"match_score": 0.0, "liveness_passed": True, "result": "fail", "reason": "no_face_detected"}

    stored_embedding = deserialize_embedding(card.embedding)
    matched, score = is_match(probe_embedding, stored_embedding)
    result = "success" if matched else "fail"

    await repository.create_auth_log(db, card_id=card_id, match_score=score, liveness_passed=True, result=result)

    return {"match_score": round(score, 4), "liveness_passed": True, "result": result, "reason": None}
