from pydantic import BaseModel


class VerifyResult(BaseModel):
    match_score: float
    liveness_passed: bool
    result: str
    reason: str | None = None
