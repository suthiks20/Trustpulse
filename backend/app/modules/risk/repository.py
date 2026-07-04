from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models import SiteRiskCheck


async def create_site_risk_check(
    db: AsyncSession,
    url: str,
    ssl_valid: bool,
    lookalike_score: float,
    risk_score: float,
    proceeded_despite_warning: bool | None = None,
) -> SiteRiskCheck:
    check = SiteRiskCheck(
        url=url,
        ssl_valid=ssl_valid,
        lookalike_score=lookalike_score,
        risk_score=risk_score,
        proceeded_despite_warning=proceeded_despite_warning,
    )
    db.add(check)
    await db.commit()
    await db.refresh(check)
    return check


async def get_latest_risk_check(db: AsyncSession) -> SiteRiskCheck | None:
    result = await db.execute(select(SiteRiskCheck).order_by(desc(SiteRiskCheck.checked_at)).limit(1))
    return result.scalar_one_or_none()


async def get_risk_checks(db: AsyncSession, limit: int = 20) -> list[SiteRiskCheck]:
    result = await db.execute(select(SiteRiskCheck).order_by(desc(SiteRiskCheck.checked_at)).limit(limit))
    return list(result.scalars().all())
