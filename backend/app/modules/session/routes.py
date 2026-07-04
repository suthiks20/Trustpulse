from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.session import handlers
from app.modules.session.schemas import SessionHeartbeatRequest, SessionStartRequest
from app.shared.database import get_db

router = APIRouter(tags=["session"])


@router.post("/session/start")
async def session_start(request: Request, payload: SessionStartRequest, db: AsyncSession = Depends(get_db)):
    return await handlers.handle_session_start(db, payload)


@router.post("/session/heartbeat")
async def session_heartbeat(request: Request, payload: SessionHeartbeatRequest, db: AsyncSession = Depends(get_db)):
    return await handlers.handle_session_heartbeat(db, payload)
