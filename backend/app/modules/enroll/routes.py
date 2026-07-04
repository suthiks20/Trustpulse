from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.enroll import handlers
from app.shared.database import get_db
from app.shared.rate_limit import STRICT_LIMIT, limiter

router = APIRouter(tags=["enroll"])


@router.post("/enroll")
@limiter.limit(STRICT_LIMIT)
async def enroll(
    request: Request,
    name: str = Form(...),
    dob: str = Form(...),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await handlers.handle_enroll(db, name=name, dob=dob, image=image)
