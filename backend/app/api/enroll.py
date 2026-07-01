import numpy as np
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
import cv2

from app.core.embedding import get_embedding, serialize_embedding
from app.db import crud
from app.db.database import get_db
from app.db.database import BACKEND_DIR

router = APIRouter()

ENROLLED_FACES_DIR = BACKEND_DIR.parent / "data" / "enrolled_faces"
ENROLLED_FACES_DIR.mkdir(parents=True, exist_ok=True)


def _read_image(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="Could not decode image")
    return image


@router.post("/enroll")
async def enroll(
    name: str = Form(...),
    dob: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_bytes = await image.read()
    image_bgr = _read_image(file_bytes)

    embedding = get_embedding(image_bgr)
    if embedding is None:
        raise HTTPException(status_code=422, detail="No face detected in image")

    card_id = crud.next_card_id(db)
    photo_path = str(ENROLLED_FACES_DIR / f"{card_id}.jpg")
    cv2.imwrite(photo_path, image_bgr)

    crud.create_demo_card(
        db,
        card_id=card_id,
        name=name,
        dob=dob,
        photo_path=photo_path,
        embedding=serialize_embedding(embedding),
    )

    return {"card_id": card_id, "status": "enrolled"}
