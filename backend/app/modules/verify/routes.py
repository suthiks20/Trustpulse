from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.verify import handlers
from app.shared.database import get_db
from app.shared.rate_limit import STRICT_LIMIT, limiter

router = APIRouter(tags=["verify"])


@router.post("/verify")
@limiter.limit(STRICT_LIMIT)
async def verify(
    request: Request,
    card_id: str = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await handlers.handle_verify(db, card_id=card_id, image=image)
