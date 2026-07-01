from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_db
from app.fraud.url_checker import check_url

router = APIRouter()


class RiskCheckRequest(BaseModel):
    url: str


@router.post("/risk-check")
async def risk_check(payload: RiskCheckRequest, db: Session = Depends(get_db)):
    result = check_url(payload.url)

    crud.create_site_risk_check(
        db,
        url=payload.url,
        ssl_valid=result["ssl_valid"],
        lookalike_score=result["lookalike_score"],
        risk_score=result["risk_score"],
    )

    return {
        "ssl_valid": result["ssl_valid"],
        "lookalike_score": result["lookalike_score"],
        "risk_score": result["risk_score"],
    }
