from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.trust import services
from app.shared.schemas import ok


async def handle_get_session_trust_events(db: AsyncSession, session_id: str) -> dict:
    events = await services.get_session_trust_events(db, session_id)
    return ok(events)
