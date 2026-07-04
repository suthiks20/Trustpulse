from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboard import repository
from app.modules.trust.explain import explain
from app.modules.trust.trust_engine import is_session_expired
from app.shared.exceptions import NotFoundError
from app.shared.logging import logger
from app.shared.storage import get_signed_url


def _photo_url(card) -> str | None:
    # Legacy cards enrolled before the Supabase Storage migration still have a
    # local filesystem path in photo_path, not a storage key — signing that
    # would just fail against Supabase, so fall back to None instead of
    # breaking the whole cards list/history for one old record.
    try:
        return get_signed_url(card.photo_path)
    except Exception:
        logger.warning("photo_signed_url_failed", card_id=card.card_id, photo_path=card.photo_path)
        return None


def _session_out(s) -> dict:
    return {
        "session_id": s.session_id,
        "card_id": s.card_id,
        "issued_at": s.issued_at,
        "last_heartbeat": s.last_heartbeat,
        "trust_score": s.trust_score,
        "expired": is_session_expired(s),
    }


def _auth_log_out(log) -> dict:
    return {
        "log_id": log.log_id,
        "card_id": log.card_id,
        "timestamp": log.timestamp,
        "match_score": log.match_score,
        "liveness_passed": log.liveness_passed,
        "result": log.result,
    }


def _trust_event_out(e) -> dict:
    return {
        "event_id": e.event_id,
        "session_id": e.session_id,
        "timestamp": e.timestamp,
        "signal_type": e.signal_type,
        "signal_value": e.signal_value,
        "resulting_score": e.resulting_score,
        "reason_code": e.reason_code,
        "explanation": explain(e.reason_code),
    }


def _risk_check_out(c) -> dict:
    return {
        "id": c.id,
        "url": c.url,
        "ssl_valid": c.ssl_valid,
        "lookalike_score": c.lookalike_score,
        "risk_score": c.risk_score,
        "checked_at": c.checked_at,
        "proceeded_despite_warning": c.proceeded_despite_warning,
    }


async def list_cards(db: AsyncSession) -> list[dict]:
    cards = await repository.get_all_cards(db)
    return [
        {
            "card_id": c.card_id,
            "name": c.name,
            "dob": c.dob,
            "enrolled_at": c.enrolled_at,
            "photo_url": _photo_url(c),
        }
        for c in cards
    ]


async def get_card_history(db: AsyncSession, card_id: str) -> dict:
    card = await repository.get_demo_card(db, card_id)
    if card is None:
        raise NotFoundError("Unknown card_id")

    sessions = await repository.get_sessions_for_card(db, card_id)
    auth_logs = await repository.get_auth_logs_for_card(db, card_id)
    trust_events = await repository.get_trust_events_for_card(db, card_id)

    return {
        "card_id": card_id,
        "name": card.name,
        "photo_url": _photo_url(card),
        "sessions": [_session_out(s) for s in sessions],
        "auth_logs": [_auth_log_out(log) for log in auth_logs],
        "trust_events": [_trust_event_out(e) for e in trust_events],
    }


async def list_sessions(db: AsyncSession) -> list[dict]:
    sessions = await repository.get_all_sessions(db)
    return [_session_out(s) for s in sessions]


async def get_session_history(db: AsyncSession, session_id: str) -> list[dict]:
    session = await repository.get_session(db, session_id)
    if session is None:
        raise NotFoundError("Unknown session_id")

    events = await repository.get_trust_events(db, session_id)
    return [_trust_event_out(e) for e in events]


async def list_auth_logs(db: AsyncSession, limit: int) -> list[dict]:
    logs = await repository.get_auth_logs(db, limit=limit)
    return [_auth_log_out(log) for log in logs]


async def list_risk_checks(db: AsyncSession, limit: int) -> list[dict]:
    checks = await repository.get_risk_checks(db, limit=limit)
    return [_risk_check_out(c) for c in checks]
