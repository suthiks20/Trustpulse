from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models import Session, TrustEvent


async def create_trust_event(
    db: AsyncSession,
    session_id: str,
    signal_type: str,
    signal_value: float,
    resulting_score: float,
    reason_code: str,
) -> TrustEvent:
    event = TrustEvent(
        session_id=session_id,
        signal_type=signal_type,
        signal_value=signal_value,
        resulting_score=resulting_score,
        reason_code=reason_code,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_trust_events(db: AsyncSession, session_id: str) -> list[TrustEvent]:
    result = await db.execute(
        select(TrustEvent).where(TrustEvent.session_id == session_id).order_by(TrustEvent.timestamp)
    )
    return list(result.scalars().all())


async def get_trust_events_for_card(db: AsyncSession, card_id: str) -> list[TrustEvent]:
    result = await db.execute(
        select(TrustEvent)
        .join(Session, TrustEvent.session_id == Session.session_id)
        .where(Session.card_id == card_id)
        .order_by(TrustEvent.timestamp)
    )
    return list(result.scalars().all())
