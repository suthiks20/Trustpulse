from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboard import handlers
from app.shared.database import get_db
from app.shared.security import get_current_admin

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(get_current_admin)])


@router.get("/cards")
async def dashboard_cards(db: AsyncSession = Depends(get_db)):
    return await handlers.handle_list_cards(db)


@router.get("/cards/{card_id}/history")
async def dashboard_card_history(card_id: str, db: AsyncSession = Depends(get_db)):
    return await handlers.handle_card_history(db, card_id)


@router.get("/sessions")
async def dashboard_sessions(db: AsyncSession = Depends(get_db)):
    return await handlers.handle_list_sessions(db)


@router.get("/sessions/{session_id}/history")
async def dashboard_session_history(session_id: str, db: AsyncSession = Depends(get_db)):
    return await handlers.handle_session_history(db, session_id)


@router.get("/auth-logs")
async def dashboard_auth_logs(limit: int = Query(20, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    return await handlers.handle_list_auth_logs(db, limit)


@router.get("/risk-checks")
async def dashboard_risk_checks(limit: int = Query(20, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    return await handlers.handle_list_risk_checks(db, limit)
