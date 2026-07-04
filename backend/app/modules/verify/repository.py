from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models import AuthLog, DemoCard


async def get_demo_card(db: AsyncSession, card_id: str) -> DemoCard | None:
    result = await db.execute(select(DemoCard).where(DemoCard.card_id == card_id))
    return result.scalar_one_or_none()


async def create_auth_log(
    db: AsyncSession, card_id: str, match_score: float, liveness_passed: bool, result: str
) -> AuthLog:
    log = AuthLog(card_id=card_id, match_score=match_score, liveness_passed=liveness_passed, result=result)
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def get_latest_auth_log(db: AsyncSession, card_id: str) -> AuthLog | None:
    result = await db.execute(
        select(AuthLog).where(AuthLog.card_id == card_id).order_by(desc(AuthLog.timestamp)).limit(1)
    )
    return result.scalar_one_or_none()


async def get_auth_logs(db: AsyncSession, limit: int = 20) -> list[AuthLog]:
    result = await db.execute(select(AuthLog).order_by(desc(AuthLog.timestamp)).limit(limit))
    return list(result.scalars().all())


async def get_auth_logs_for_card(db: AsyncSession, card_id: str) -> list[AuthLog]:
    result = await db.execute(
        select(AuthLog).where(AuthLog.card_id == card_id).order_by(desc(AuthLog.timestamp))
    )
    return list(result.scalars().all())
