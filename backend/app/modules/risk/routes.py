from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.risk import handlers
from app.modules.risk.schemas import RiskCheckRequest
from app.shared.database import get_db
from app.shared.rate_limit import STRICT_LIMIT, limiter

router = APIRouter(tags=["risk"])


@router.post("/risk-check")
@limiter.limit(STRICT_LIMIT)
async def risk_check(request: Request, payload: RiskCheckRequest, db: AsyncSession = Depends(get_db)):
    return await handlers.handle_risk_check(db, payload)
