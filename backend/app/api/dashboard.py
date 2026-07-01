from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.explain import explain
from app.core.trust_engine import is_session_expired
from app.db import crud
from app.db.database import get_db

router = APIRouter()


@router.get("/dashboard/cards")
async def dashboard_cards(db: Session = Depends(get_db)):
    cards = crud.get_all_cards(db)
    return [
        {
            "card_id": c.card_id,
            "name": c.name,
            "dob": c.dob,
            "enrolled_at": c.enrolled_at,
        }
        for c in cards
    ]


@router.get("/dashboard/sessions")
async def dashboard_sessions(db: Session = Depends(get_db)):
    sessions = crud.get_all_sessions(db)
    return [
        {
            "session_id": s.session_id,
            "card_id": s.card_id,
            "issued_at": s.issued_at,
            "last_heartbeat": s.last_heartbeat,
            "trust_score": s.trust_score,
            "expired": is_session_expired(s),
        }
        for s in sessions
    ]


@router.get("/dashboard/sessions/{session_id}/history")
async def dashboard_session_history(session_id: str, db: Session = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Unknown session_id")

    events = crud.get_trust_events(db, session_id)
    return [
        {
            "event_id": e.event_id,
            "timestamp": e.timestamp,
            "signal_type": e.signal_type,
            "signal_value": e.signal_value,
            "resulting_score": e.resulting_score,
            "reason_code": e.reason_code,
            "explanation": explain(e.reason_code),
        }
        for e in events
    ]


@router.get("/dashboard/auth-logs")
async def dashboard_auth_logs(limit: int = Query(20, ge=1, le=200), db: Session = Depends(get_db)):
    logs = crud.get_auth_logs(db, limit=limit)
    return [
        {
            "log_id": log.log_id,
            "card_id": log.card_id,
            "timestamp": log.timestamp,
            "match_score": log.match_score,
            "liveness_passed": log.liveness_passed,
            "result": log.result,
        }
        for log in logs
    ]


@router.get("/dashboard/risk-checks")
async def dashboard_risk_checks(limit: int = Query(20, ge=1, le=200), db: Session = Depends(get_db)):
    checks = crud.get_risk_checks(db, limit=limit)
    return [
        {
            "id": c.id,
            "url": c.url,
            "ssl_valid": c.ssl_valid,
            "lookalike_score": c.lookalike_score,
            "risk_score": c.risk_score,
            "checked_at": c.checked_at,
        }
        for c in checks
    ]
