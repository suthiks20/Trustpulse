import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.embedding import deserialize_embedding, get_embedding
from app.core.liveness import check_liveness
from app.core.matcher import is_match
from app.db import crud
from app.db.database import get_db

router = APIRouter()


def _read_image(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image")
    return image


@router.post("/verify")
async def verify(
    card_id: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    card = crud.get_demo_card(db, card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Unknown card_id")

    file_bytes = await image.read()
    image_bgr = _read_image(file_bytes)

    liveness_passed = check_liveness([image_bgr])
    if not liveness_passed:
        crud.create_auth_log(db, card_id=card_id, match_score=0.0, liveness_passed=False, result="fail")
        return {"match_score": 0.0, "liveness_passed": False, "result": "fail", "reason": "liveness_failed"}

    probe_embedding = get_embedding(image_bgr)
    if probe_embedding is None:
        crud.create_auth_log(db, card_id=card_id, match_score=0.0, liveness_passed=True, result="fail")
        return {"match_score": 0.0, "liveness_passed": True, "result": "fail", "reason": "no_face_detected"}

    stored_embedding = deserialize_embedding(card.embedding)
    matched, score = is_match(probe_embedding, stored_embedding)
    result = "success" if matched else "fail"

    crud.create_auth_log(db, card_id=card_id, match_score=score, liveness_passed=True, result=result)

    return {"match_score": round(score, 4), "liveness_passed": True, "result": result}
