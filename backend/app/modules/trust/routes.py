from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.trust import handlers
from app.shared.database import get_db
from app.shared.security import get_current_admin

router = APIRouter(tags=["trust"])


@router.get("/trust/sessions/{session_id}/events")
async def get_session_trust_events(
    session_id: str, db: AsyncSession = Depends(get_db), admin: str = Depends(get_current_admin)
):
    return await handlers.handle_get_session_trust_events(db, session_id)
