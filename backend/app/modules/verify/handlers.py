from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.verify import services
from app.shared.schemas import ok


async def handle_verify(db: AsyncSession, card_id: str, image: UploadFile) -> dict:
    file_bytes = await image.read()
    result = await services.verify_card(db, card_id=card_id, file_bytes=file_bytes)
    return ok(result)
