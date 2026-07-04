from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboard import services
from app.shared.schemas import ok


async def handle_list_cards(db: AsyncSession) -> dict:
    return ok(await services.list_cards(db))


async def handle_card_history(db: AsyncSession, card_id: str) -> dict:
    return ok(await services.get_card_history(db, card_id))


async def handle_list_sessions(db: AsyncSession) -> dict:
    return ok(await services.list_sessions(db))


async def handle_session_history(db: AsyncSession, session_id: str) -> dict:
    return ok(await services.get_session_history(db, session_id))


async def handle_list_auth_logs(db: AsyncSession, limit: int) -> dict:
    return ok(await services.list_auth_logs(db, limit))


async def handle_list_risk_checks(db: AsyncSession, limit: int) -> dict:
    return ok(await services.list_risk_checks(db, limit))
