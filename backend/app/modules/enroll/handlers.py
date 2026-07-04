from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.enroll import services
from app.shared.schemas import ok


async def handle_enroll(db: AsyncSession, name: str, dob: str, image: UploadFile) -> dict:
    file_bytes = await image.read()
    result = await services.enroll_card(db, name=name, dob=dob, file_bytes=file_bytes)
    return ok(result)
