from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models import DemoCard


async def get_all_cards(db: AsyncSession) -> list[DemoCard]:
    result = await db.execute(select(DemoCard).order_by(desc(DemoCard.enrolled_at)))
    return list(result.scalars().all())


async def next_card_id(db: AsyncSession) -> str:
    count = await db.scalar(select(func.count()).select_from(DemoCard))
    return f"DC{count + 1:04d}"


async def create_demo_card(
    db: AsyncSession, card_id: str, name: str, dob: str, photo_path: str, embedding: bytes
) -> DemoCard:
    card = DemoCard(card_id=card_id, name=name, dob=dob, photo_path=photo_path, embedding=embedding)
    db.add(card)
    await db.commit()
    await db.refresh(card)
    return card
