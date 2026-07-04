from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.risk import services
from app.modules.risk.schemas import RiskCheckRequest
from app.shared.schemas import ok


async def handle_risk_check(db: AsyncSession, payload: RiskCheckRequest) -> dict:
    result = await services.run_risk_check(
        db, url=payload.url, proceeded_despite_warning=payload.proceeded_despite_warning
    )
    return ok(result)
