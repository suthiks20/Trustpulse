from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.session import services
from app.modules.session.schemas import SessionHeartbeatRequest, SessionStartRequest
from app.shared.schemas import ok


async def handle_session_start(db: AsyncSession, payload: SessionStartRequest) -> dict:
    result = await services.start_session(db, card_id=payload.card_id)
    return ok(result)


async def handle_session_heartbeat(db: AsyncSession, payload: SessionHeartbeatRequest) -> dict:
    result = await services.heartbeat(db, session_id=payload.session_id)
    return ok(result)
