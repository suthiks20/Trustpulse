from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models import Session


def utcnow():
    # last_heartbeat/last_score_update are TIMESTAMP WITHOUT TIME ZONE columns;
    # asyncpg rejects tz-aware values there, so store naive UTC wall-clock time.
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def create_session(db: AsyncSession, session_id: str, card_id: str) -> Session:
    session = Session(session_id=session_id, card_id=card_id, trust_score=100.0)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(db: AsyncSession, session_id: str) -> Session | None:
    result = await db.execute(select(Session).where(Session.session_id == session_id))
    return result.scalar_one_or_none()


async def get_all_sessions(db: AsyncSession) -> list[Session]:
    result = await db.execute(select(Session).order_by(desc(Session.issued_at)))
    return list(result.scalars().all())


async def get_sessions_for_card(db: AsyncSession, card_id: str) -> list[Session]:
    result = await db.execute(
        select(Session).where(Session.card_id == card_id).order_by(desc(Session.issued_at))
    )
    return list(result.scalars().all())


async def update_session_heartbeat(db: AsyncSession, session: Session, trust_score: float) -> Session:
    session.last_heartbeat = utcnow()
    session.trust_score = trust_score
    session.last_score_update = utcnow()
    await db.commit()
    await db.refresh(session)
    return session
