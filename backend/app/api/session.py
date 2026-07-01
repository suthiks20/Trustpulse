import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.trust_engine import compute_trust_score, is_session_expired
from app.db import crud
from app.db.database import get_db

router = APIRouter()


class SessionStartRequest(BaseModel):
    card_id: str


class SessionHeartbeatRequest(BaseModel):
    session_id: str


@router.post("/session/start")
async def session_start(payload: SessionStartRequest, db: Session = Depends(get_db)):
    card = crud.get_demo_card(db, payload.card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Unknown card_id")

    session_id = str(uuid.uuid4())
    session = crud.create_session(db, session_id=session_id, card_id=payload.card_id)

    return {"session_id": session.session_id, "trust_score": session.trust_score}


@router.post("/session/heartbeat")
async def session_heartbeat(payload: SessionHeartbeatRequest, db: Session = Depends(get_db)):
    session = crud.get_session(db, payload.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session_id")

    if is_session_expired(session):
        raise HTTPException(status_code=410, detail="Session expired")

    result = compute_trust_score(db, session)
    crud.update_session_heartbeat(db, session, result["trust_score"])

    return {
        "trust_score": result["trust_score"],
        "flag": result["flag"],
        "latest_reason": result["reason_code"],
    }
