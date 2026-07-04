import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.session import repository
from app.modules.trust.trust_engine import compute_trust_score, is_session_expired
from app.modules.verify.repository import get_demo_card
from app.shared.exceptions import GoneError, NotFoundError


async def start_session(db: AsyncSession, card_id: str) -> dict:
    card = await get_demo_card(db, card_id)
    if card is None:
        raise NotFoundError("Unknown card_id")

    session_id = str(uuid.uuid4())
    session = await repository.create_session(db, session_id=session_id, card_id=card_id)

    return {"session_id": session.session_id, "trust_score": session.trust_score, "card_name": card.name}


async def heartbeat(db: AsyncSession, session_id: str) -> dict:
    session = await repository.get_session(db, session_id)
    if session is None:
        raise NotFoundError("Unknown session_id")

    if is_session_expired(session):
        raise GoneError("Session expired", code="session_expired")

    result = await compute_trust_score(db, session)
    await repository.update_session_heartbeat(db, session, result["trust_score"])

    return {
        "trust_score": result["trust_score"],
        "flag": result["flag"],
        "latest_reason": result["reason_code"],
    }
