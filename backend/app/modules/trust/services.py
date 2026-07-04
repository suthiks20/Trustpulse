from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.session import repository as session_repository
from app.modules.trust import repository
from app.modules.trust.explain import explain
from app.shared.exceptions import NotFoundError


def _serialize(event) -> dict:
    return {
        "event_id": event.event_id,
        "session_id": event.session_id,
        "timestamp": event.timestamp,
        "signal_type": event.signal_type,
        "signal_value": event.signal_value,
        "resulting_score": event.resulting_score,
        "reason_code": event.reason_code,
        "explanation": explain(event.reason_code),
    }


async def get_session_trust_events(db: AsyncSession, session_id: str) -> list[dict]:
    session = await session_repository.get_session(db, session_id)
    if session is None:
        raise NotFoundError("Unknown session_id")
    events = await repository.get_trust_events(db, session_id)
    return [_serialize(e) for e in events]
